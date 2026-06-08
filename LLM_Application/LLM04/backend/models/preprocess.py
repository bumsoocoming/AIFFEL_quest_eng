import re
import pandas as pd
import numpy as np


def clean_text(text: str) -> str:
    text = str(text)
    text = re.sub(r'\(([^)]+)\)/\([^)]+\)', r'\1', text)
    text = re.sub(r'\[[^\]]*\]', ' ', text)
    text = re.sub(r'\*+', ' ', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def make_balanced_sample(df: pd.DataFrame, per_class: int, random_state: int = 42) -> pd.DataFrame:
    parts = []
    for _, part in df.groupby('category_enc'):
        n = min(per_class, len(part))
        parts.append(part.sample(n=n, random_state=random_state))
    return pd.concat(parts).sample(frac=1.0, random_state=random_state).reset_index(drop=True)
