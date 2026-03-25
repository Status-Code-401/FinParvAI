from fastapi import APIRouter
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from models.schemas import FinancialState
from services.predict_engine import generate_forecast

router = APIRouter()

@router.post("/forecast")
def forecast(state: FinancialState, horizon_days: int = 30):
    """Generate revenue and cash flow forecasts."""
    return generate_forecast(state, horizon_days=horizon_days)
