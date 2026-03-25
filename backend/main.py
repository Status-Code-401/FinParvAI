from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import ingest, decision, predict, actions

app = FastAPI(title="FinParvai API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(ingest.router, prefix="/api/ingest", tags=["Data Ingestion"])
app.include_router(decision.router, prefix="/api/decision", tags=["Decision Engine"])
app.include_router(predict.router, prefix="/api/predict", tags=["Predictive Engine"])
app.include_router(actions.router, prefix="/api/actions", tags=["Actions"])

@app.get("/")
def root():
    return {"message": "FinParvai Financial Decision Intelligence API", "status": "running"}

@app.get("/health")
def health():
    return {"status": "healthy"}
