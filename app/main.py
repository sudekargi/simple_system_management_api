from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.endpoints import user
from app.db.base import init_db

app = FastAPI(
    title="Kullanıcı Yönetim Sistemi",
    description="Kullanıcı yönetimi için API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(user.router, prefix="/api", tags=["users"])

@app.on_event("startup")
async def startup_event():
    await init_db()

@app.get("/")
async def root():
    return {"message": "Kullanıcı Yönetim Sistemi API'sine Hoş Geldiniz!"} 