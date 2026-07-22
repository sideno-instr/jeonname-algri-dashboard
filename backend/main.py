from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from config import settings
from routers import prices

app = FastAPI(
    title="Jeonnam Agri Dashboard API",
    description="전남 농산물 가격 및 유통 대시보드 백엔드 API",
    version="0.1.0"
)

# 개발용 CORS 설정 (Next.js 주소 허용)
origins = [
    "http://localhost:3000",
    settings.FRONTEND_ORIGIN
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=list(set([o for o in origins if o])),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(prices.router)


@app.get("/health")
def health_check():
    return {
        "status": "ok",
        "service": "jeonam-agri-backend"
    }
