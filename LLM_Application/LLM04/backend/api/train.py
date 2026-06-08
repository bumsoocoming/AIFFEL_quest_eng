from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from pathlib import Path
from backend.models import tfidf_lr, classifier

router = APIRouter()
DATA_PATH = Path(__file__).parent.parent.parent / 'data' / 'train_5cat.csv'


class TrainRequest(BaseModel):
    data_path: str = ''


@router.post('/train')
async def train_model(req: TrainRequest):
    path = req.data_path or str(DATA_PATH)
    if not Path(path).exists():
        raise HTTPException(status_code=404, detail=f'데이터 파일을 찾을 수 없습니다: {path}')
    result = tfidf_lr.train(path)
    pipe, encoder = tfidf_lr.load()
    if pipe:
        classifier.load_model(pipe, encoder)
    return {'status': 'ok', **result}


@router.get('/model/status')
async def model_status():
    from backend.models.classifier import _pipe_lr
    return {'loaded': _pipe_lr is not None}
