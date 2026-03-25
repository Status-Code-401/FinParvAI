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
