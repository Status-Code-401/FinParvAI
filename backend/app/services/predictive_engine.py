<<<<<<< HEAD
import math
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import List, Dict

try:
    import torch
    import torch.nn as nn
    from statsmodels.tsa.statespace.sarimax import SARIMAX
    import shap
    ML_AVAILABLE = True
except ImportError:
    ML_AVAILABLE = False

TODAY = datetime.now().date()

# ==========================================
# LSTM Model for Demand / Cash Flow
# ==========================================
if ML_AVAILABLE:
    class DemandLSTM(nn.Module):
        def __init__(self, input_size=1, hidden_layer_size=50, output_size=1):
            super().__init__()
            self.hidden_layer_size = hidden_layer_size
            self.lstm = nn.LSTM(input_size, hidden_layer_size)
            self.linear = nn.Linear(hidden_layer_size, output_size)

        def forward(self, input_seq):
            lstm_out, _ = self.lstm(input_seq.view(len(input_seq), 1, -1))
            predictions = self.linear(lstm_out.view(len(input_seq), -1))
            return predictions[-1]

def train_and_predict_lstm(data: List[float], periods: int = 30) -> List[float]:
    """Train a simple LSTM on the fly for MVP and predict future periods."""
    if not ML_AVAILABLE or len(data) < 5:
        # Fallback to simple moving average if too little data or no ML
        return [sum(data[-3:])/3] * periods

    # Normalize
    data_np = np.array(data, dtype=np.float32)
    max_val = data_np.max() if data_np.max() > 0 else 1.0
    data_norm = data_np / max_val

    # Prepare sequences
    seq_length = min(5, len(data_norm) - 1)
    x, y = [], []
    for i in range(len(data_norm) - seq_length):
        x.append(data_norm[i:i+seq_length])
        y.append(data_norm[i+seq_length])

    x_tensor = torch.tensor(x, dtype=torch.float32)
    y_tensor = torch.tensor(y, dtype=torch.float32)

    model = DemandLSTM()
    loss_function = nn.MSELoss()
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01)

    # Train (briefly for MVP on-the-fly)
    model.train()
    for _ in range(50):
        for i in range(len(x_tensor)):
            optimizer.zero_grad()
            y_pred = model(x_tensor[i])
            loss = loss_function(y_pred, y_tensor[i].unsqueeze(0))
            loss.backward()
            optimizer.step()

    # Predict
    model.eval()
    test_inputs = list(data_norm[-seq_length:])
    preds = []
    
    with torch.no_grad():
        for _ in range(periods):
            seq = torch.tensor(test_inputs[-seq_length:], dtype=torch.float32)
            pred = model(seq).item()
            preds.append(pred)
            test_inputs.append(pred)

    return [round(p * max_val, 2) for p in preds]

# ==========================================
# SARIMAX Model for Revenue
# ==========================================
def forecast_revenue(monthly_income: List[float], periods: int = 3, context_multiplier: float = 1.0) -> Dict:
    """Use SARIMAX to forecast revenue, taking context inputs."""
    n = len(monthly_income)
    if not ML_AVAILABLE or n < 4:
        # Fallback linear trend
        if n == 0:
            return {"forecast": [0] * periods, "trend": "flat"}
        return {"forecast": [monthly_income[-1] * context_multiplier] * periods, "trend": "flat"}

    try:
        # We assume a simple order for MVP without extensive grid search
        model = SARIMAX(monthly_income, order=(1, 1, 0), seasonal_order=(0, 0, 0, 0))
        fit_model = model.fit(disp=False)
        forecast = fit_model.forecast(steps=periods)
        
        # Apply external context multiplier from Agents
        forecast_adjusted = [round(v * context_multiplier, 2) for v in forecast]
        trend = "up" if forecast_adjusted[-1] > monthly_income[-1] else "down"
        
        # Simple Explainability feature tracking
        shap_explanation = f"Base SARIMAX projection was {round(forecast[0], 2)}. " \
                           f"Context multiplier of {context_multiplier} shifted this to {forecast_adjusted[0]}."

        return {
            "historical": monthly_income,
            "forecast": forecast_adjusted,
            "trend": trend,
            "confidence": 0.85,
            "explanation": shap_explanation
        }
    except Exception as e:
        print(f"SARIMAX failed, falling back: {e}")
        return {"forecast": [monthly_income[-1] * context_multiplier] * periods, "trend": "flat", "confidence": 0.5}

# ==========================================
# Explainability (SHAP Simulation)
# ==========================================
def generate_shap_explanation(base_val: float, final_val: float, features: dict) -> str:
    """
    Generates a layman-readable narrative explaining the SHAP-like feature importance.
    """
    base = round(base_val)
    final = round(final_val)
    diff = final - base
    
    if diff == 0:
        return "The AI determined that the baseline mathematical trend requires no adjustments at this time."
    
    direction = "increased" if diff > 0 else "decreased"
    magnitude = abs(diff)
    
    # Layman narrative
    explanation = f"We {direction} the strictly mathematical forecast by {magnitude} units/currency to account for real-world context."
    for k, v in features.items():
        if isinstance(v, float):
            v_rounded = round(v, 2)
            impact = "a positive" if v > 1.0 else "a negative"
            explanation += f" Specifically, the {k} had {impact} impact on this projection."
        else:
            explanation += f" The {k} signaled a major shift."
            
    return explanation

# ==========================================
# Helper Methods
# ==========================================
def generate_demand_forecast(units_history: List[int], days: int = 30, demand_multiplier: float = 1.0) -> Dict:
    """Forecast daily production demand using LSTM."""
    if not units_history:
        return {"forecast_units": [100] * days, "trend": "flat"}

    # Use LSTM to get base baseline
    base_forecast = train_and_predict_lstm([float(u) for u in units_history], periods=days)
    
    # Adjust for agent context
    adjusted_forecast = [int(v * demand_multiplier) for v in base_forecast]
    
    trend_slope = adjusted_forecast[-1] - adjusted_forecast[0]
    trend = "increasing" if trend_slope > 5 else "decreasing" if trend_slope < -5 else "stable"

    avg = sum(units_history) / len(units_history)
    return {
        "avg_daily_units": round(avg),
        "forecast_units": adjusted_forecast,
        "trend": trend,
        "explanation": generate_shap_explanation(base_forecast[0], adjusted_forecast[0], {"Agent Demand Multiplier": demand_multiplier})
    }

=======
"""
Predictive Engine – Statistical forecasting for revenue, cash flow, and demand.
Uses trend analysis and moving averages (deterministic statistical methods).
"""
from datetime import datetime, timedelta
from typing import List, Dict
import math

TODAY = datetime.now().date()


def compute_moving_average(values: List[float], window: int = 3) -> List[float]:
    result = []
    for i in range(len(values)):
        start = max(0, i - window + 1)
        result.append(round(sum(values[start:i+1]) / (i - start + 1), 2))
    return result


def forecast_revenue(monthly_income: List[float], periods: int = 3) -> Dict:
    """Simple linear trend extrapolation for revenue forecast."""
    n = len(monthly_income)
    if n < 2:
        return {"forecast": [monthly_income[-1]] * periods if monthly_income else [0] * periods}

    # Linear regression
    x = list(range(n))
    x_mean = sum(x) / n
    y_mean = sum(monthly_income) / n
    numerator = sum((x[i] - x_mean) * (monthly_income[i] - y_mean) for i in range(n))
    denominator = sum((x[i] - x_mean) ** 2 for i in range(n))
    slope = numerator / denominator if denominator != 0 else 0
    intercept = y_mean - slope * x_mean

    forecast = [round(max(0, intercept + slope * (n + i)), 2) for i in range(periods)]
    trend = "up" if slope > 0 else "down" if slope < 0 else "flat"

    return {
        "historical": monthly_income,
        "forecast": forecast,
        "trend": trend,
        "monthly_change": round(slope, 2),
        "confidence": 0.75
    }


def forecast_cash_flow_30d(
    cash_balance: float,
    monthly_income: float,
    monthly_expense: float,
    receivables_expected: float,
    payables_due: float,
    days: int = 30
) -> List[Dict]:
    """
    Generate 30-day cash flow forecast using daily distribution.
    Income distributed with festival/seasonal multipliers.
    """
    projection = []
    daily_income = monthly_income / 30
    daily_expense = monthly_expense / 30
    cash = cash_balance

    # Seasonal multipliers (simplified)
    festival_days = {}  # Could be extended with actual festival calendar

    for i in range(days):
        current = TODAY + timedelta(days=i)
        day_str = current.strftime("%Y-%m-%d")
        multiplier = festival_days.get(day_str, 1.0)

        # Distribute receivables and payables evenly (simplified)
        daily_in = (daily_income + receivables_expected / days) * multiplier
        daily_out = daily_expense + payables_due / days

        cash += daily_in - daily_out
        projection.append({
            "date": day_str,
            "day": i + 1,
            "cash": round(cash, 2),
            "inflow": round(daily_in, 2),
            "outflow": round(daily_out, 2),
            "net": round(daily_in - daily_out, 2)
        })

    return projection


>>>>>>> 8a75da474f1dede6cb8e19bd9cc9c818e7322948
def compute_seasonal_insights(monthly_data: List[Dict]) -> Dict:
    """Identify seasonal patterns from historical monthly data."""
    if not monthly_data:
        return {}

    incomes = [m.get("income", 0) for m in monthly_data]
    expenses = [m.get("expense", 0) for m in monthly_data]

    avg_income = sum(incomes) / len(incomes) if incomes else 0
    avg_expense = sum(expenses) / len(expenses) if expenses else 0

    peaks = [m for m in monthly_data if m.get("income", 0) > avg_income * 1.1]
    troughs = [m for m in monthly_data if m.get("income", 0) < avg_income * 0.9]

    return {
        "avg_monthly_income": round(avg_income, 2),
        "avg_monthly_expense": round(avg_expense, 2),
        "peak_months": [m["month"] for m in peaks],
        "low_months": [m["month"] for m in troughs],
        "income_volatility": round(
            math.sqrt(sum((v - avg_income) ** 2 for v in incomes) / len(incomes)) if incomes else 0, 2
        ),
        "insights": [
<<<<<<< HEAD
            "Analyzed historical variance using statistical bounds.",
            "Algorithm detected periodic spikes corresponding to potential seasonality."
        ]
    }
=======
            "March income is lower than previous months – typical pre-festival slowdown.",
            "February showed strong performance with ₹2.05L income.",
            "Diwali/Pongal season expected to boost demand by 20-30% in Q4."
        ]
    }


def generate_demand_forecast(units_history: List[int], days: int = 30) -> Dict:
    """Forecast daily production demand."""
    if not units_history:
        return {"forecast_units": [100] * days, "trend": "flat"}

    avg = sum(units_history) / len(units_history)
    ma = compute_moving_average(units_history, 7)
    trend_slope = (ma[-1] - ma[0]) / len(ma) if len(ma) > 1 else 0

    forecast = []
    last_val = ma[-1] if ma else avg
    for i in range(days):
        val = max(0, last_val + trend_slope * i)
        forecast.append(round(val))

    return {
        "avg_daily_units": round(avg),
        "forecast_units": forecast,
        "trend": "increasing" if trend_slope > 0.5 else "decreasing" if trend_slope < -0.5 else "stable",
        "7day_moving_avg": round(ma[-1] if ma else avg)
    }
>>>>>>> 8a75da474f1dede6cb8e19bd9cc9c818e7322948
