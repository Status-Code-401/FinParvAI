from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import financial, ingest
import os

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

app = FastAPI(
    title="FinParvai API",
    description="Financial Decision Intelligence System for SMEs",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(financial.router)
app.include_router(ingest.router)


@app.get("/")
def root():
    return {
        "product": "FinParvai",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs"
    }


@app.get("/health")
def health():
    return {"status": "ok"}
