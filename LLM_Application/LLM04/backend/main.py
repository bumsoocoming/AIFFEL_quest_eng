import sys
from pathlib import Path

# 프로젝트 루트를 sys.path에 추가
sys.path.insert(0, str(Path(__file__).parent.parent))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from backend.api import classify, interview, storybook, video_script, image, train
from backend.models import tfidf_lr, classifier

app = FastAPI(title='HERO API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_methods=['*'],
    allow_headers=['*'],
)

# API 라우터 등록
app.include_router(classify.router, prefix='/api')
app.include_router(interview.router, prefix='/api')
app.include_router(storybook.router, prefix='/api')
app.include_router(video_script.router, prefix='/api')
app.include_router(image.router, prefix='/api')
app.include_router(train.router, prefix='/api')

# 정적 파일 (프론트엔드) 서빙
FRONTEND_DIR = Path(__file__).parent.parent / 'frontend'
if FRONTEND_DIR.exists():
    app.mount('/images', StaticFiles(directory=str(FRONTEND_DIR / 'images')), name='images')
    app.mount('/css', StaticFiles(directory=str(FRONTEND_DIR / 'css')), name='css')
    app.mount('/js', StaticFiles(directory=str(FRONTEND_DIR / 'js')), name='js')


NO_CACHE_HEADERS = {
    'Cache-Control': 'no-store, no-cache, must-revalidate, max-age=0',
    'Pragma': 'no-cache',
    'Expires': '0',
}


@app.get('/')
async def root():
    index = FRONTEND_DIR / 'index.html'
    if index.exists():
        return FileResponse(str(index), headers=NO_CACHE_HEADERS)
    return {'message': 'HERO API 서버 실행 중. /docs 에서 API 문서를 확인하세요.'}


# 캐시 우회용 새 주소 (한 번도 방문 안 한 URL → 무조건 최신 화면)
@app.get('/new')
@app.get('/v2')
@app.get('/hero')
async def fresh():
    index = FRONTEND_DIR / 'index.html'
    if index.exists():
        return FileResponse(str(index), headers=NO_CACHE_HEADERS)
    return {'message': 'index.html 없음'}


@app.get('/poster')
async def poster():
    poster_path = FRONTEND_DIR / 'poster.html'
    if poster_path.exists():
        return FileResponse(str(poster_path), headers=NO_CACHE_HEADERS)
    return {'message': 'poster.html을 frontend/ 폴더에 넣어주세요.'}


# PWA 파일들 (앱 설치용)
@app.get('/manifest.json')
async def manifest():
    return FileResponse(str(FRONTEND_DIR / 'manifest.json'), media_type='application/manifest+json')


@app.get('/sw.js')
async def service_worker():
    return FileResponse(str(FRONTEND_DIR / 'sw.js'), media_type='application/javascript', headers=NO_CACHE_HEADERS)


@app.get('/icon-192.png')
async def icon192():
    return FileResponse(str(FRONTEND_DIR / 'icon-192.png'), media_type='image/png')


@app.get('/icon-512.png')
async def icon512():
    return FileResponse(str(FRONTEND_DIR / 'icon-512.png'), media_type='image/png')


@app.on_event('startup')
async def startup():
    pipe, encoder = tfidf_lr.load()
    if pipe is not None:
        classifier.load_model(pipe, encoder)
        print('[OK] 저장된 TF-IDF+LR 모델 로드 완료')
    else:
        print('[INFO] 학습된 모델 없음. POST /api/train 으로 먼저 학습하세요.')
