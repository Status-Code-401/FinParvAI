import os
from dotenv import load_dotenv
load_dotenv()
from app.services.context_agents import ContextAnalysisAgent
agent = ContextAnalysisAgent()
res = agent.analyze_context({"upcoming_festival": "Pongal", "days_to_festival": 15, "market_sentiment": "neutral", "garment_demand_signal": "low_demand"})
print("LOCAL TEST RESULT:")
print(res)
