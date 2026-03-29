from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import decision, predict, actions
from routers import impact, leakage, execution, signals
from app.routers import financial, ingest

app = FastAPI(
    title="FinParvai API",
    description="Autonomous Cost Intelligence Engine v2",
    version="2.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://finparvai.vercel.app",
        "https://finparvai.onrender.com"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Existing routers ──
app.include_router(ingest.router)
app.include_router(decision.router, prefix="/api/decision", tags=["Decision Engine"])
app.include_router(predict.router, prefix="/api/predict", tags=["Predictive Engine"])
app.include_router(actions.router, prefix="/api/actions", tags=["Actions"])
app.include_router(financial.router)

# ── NEW v2 Module Routers ──
app.include_router(impact.router)        # POST /api/impact/calculate
app.include_router(leakage.router)       # POST /api/leakage/detect
app.include_router(execution.router)     # POST /api/execution/run, /logs, etc.
app.include_router(signals.router)       # POST /api/signals/analyze

@app.get("/")
def root():
    return {
        "message": "FinParvai — Autonomous Cost Intelligence Engine",
        "version": "2.0.0",
        "status": "running",
        "modules": [
            "Decision Engine",
            "Predictive Engine",
            "Cost Impact Engine (v2)",
            "Cost Leakage Detection (v2)",
            "Autonomous Execution Layer (v2)",
            "Enterprise Signal Layer (v2)"
        ],
        "docs": "/docs"
    }

@app.get("/health")
def health():
    return {"status": "healthy", "version": "2.0.0"}
