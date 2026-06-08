import os
import joblib
import numpy as np
import pandas as pd
from pathlib import Path
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import accuracy_score, f1_score

from .preprocess import clean_text, make_balanced_sample

MODEL_PATH = Path(__file__).parent.parent.parent / 'outputs' / 'models' / 'tfidf_lr_pipeline.pkl'
ENCODER_PATH = Path(__file__).parent.parent.parent / 'outputs' / 'models' / 'cat_encoder.pkl'

RANDOM_STATE = 42
PER_CLASS = 30_000
VALID_CATEGORIES = ['감정긍정', '감정부정', '관계', '장소', '사물']


def train(data_path: str) -> dict:
    df = pd.read_csv(
        data_path,
        encoding='utf-8-sig',
        engine='python',
        on_bad_lines='skip',
        usecols=[0, 1, 2, 3, 4],
        names=['text', 'category', 'label', 'age', 'sex'],
        header=0,
    )
    df = df[df['category'].isin(VALID_CATEGORIES)].copy()
    df['text'] = df['text'].astype(str).map(clean_text)
    df = df[df['text'].str.len() >= 10].drop_duplicates(subset='text').copy()

    encoder = LabelEncoder()
    df['category_enc'] = encoder.fit_transform(df['category'])

    df_sample = make_balanced_sample(df, PER_CLASS, RANDOM_STATE)
    X = df_sample['text'].astype(str)
    y = df_sample['category_enc'].astype(int)
    X_train, X_val, y_train, y_val = train_test_split(X, y, test_size=0.2, stratify=y, random_state=RANDOM_STATE)

    pipe = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), max_features=50_000)),
        ('lr', LogisticRegression(random_state=RANDOM_STATE, max_iter=500, class_weight='balanced')),
    ])
    pipe.fit(X_train, y_train)

    y_pred = pipe.predict(X_val)
    metrics = {
        'accuracy': round(accuracy_score(y_val, y_pred), 4),
        'macro_f1': round(f1_score(y_val, y_pred, average='macro'), 4),
        'weighted_f1': round(f1_score(y_val, y_pred, average='weighted'), 4),
    }

    MODEL_PATH.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(pipe, MODEL_PATH)
    joblib.dump(encoder, ENCODER_PATH)

    return {'metrics': metrics, 'model_path': str(MODEL_PATH)}


def load():
    if MODEL_PATH.exists() and ENCODER_PATH.exists():
        return joblib.load(MODEL_PATH), joblib.load(ENCODER_PATH)
    return None, None
