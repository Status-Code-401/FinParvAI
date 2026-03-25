import random
import os

# Placeholder for real LLM integration. 
# We are using robust mock logic to ensure the MVP works without requiring API keys.

class WebCrawlingAgent:
    def __init__(self):
        self.sources = [
            "https://news.ycombinator.com",
            "https://in.investing.com/"
        ]

    def gather_signals(self) -> dict:
        """
        Simulates web crawling to find relevant market signals and festival data
        based on the user's PRD configuration.
        """
        # In a generic production scenario, this would use BeautifulSoup / LangChain document loaders
        # with targeted URLs. For this MVP, we mock the signals.
        festivals = ["Diwali", "Pongal", "Dussehra", "Holi"]
        upcoming = random.choice(festivals)
        
        return {
            "upcoming_festival": upcoming,
            "days_to_festival": random.randint(5, 30),
            "market_sentiment": random.choice(["bullish", "neutral", "bearish"]),
            "garment_demand_signal": random.choice(["high_demand", "moderate_demand", "low_demand"])
        }


class ContextAnalysisAgent:
    def __init__(self):
        self.llm_key = os.environ.get("OPENAI_API_KEY", None)
        
    def analyze_context(self, signals: dict) -> dict:
        """
        Uses an LLM (LangChain) to convert qualitative signals into quantitative multipliers.
        Produces a genuine Chain of Thought string explaining the rationale.
        Falls back to robust deterministic rules if no API key is present.
        """
        if self.llm_key and isinstance(self.llm_key, str) and len(self.llm_key) > 10:
            try:
                from langchain_openai import ChatOpenAI
                import json
                
                llm = ChatOpenAI(temperature=0.2, openai_api_key=self.llm_key)
                prompt = (
                    f"You are a friendly, expert financial advisor for a small business owner. Review these real-world market signals: {signals}. "
                    "Output a strict JSON containing two fields: "
                    "'demand_multiplier' (a float around 1.0, where >1.0 means demand is growing, and <1.0 means shrinking), and "
                    "'chain_of_thought' (A friendly, single paragraph explaining to the business owner exactly why you are adjusting their forecast based on the current market/festival conditions. Do not use jargon. Speak directly to them like an advisor.)"
                )
                
                response = llm.invoke(prompt).content
                
                # Cleanup potential markdown ticks if returned by LLM
                clean_resp = response.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean_resp)
                
                return {
                    "demand_multiplier": parsed.get("demand_multiplier", 1.0),
                    "reasoning": parsed.get("chain_of_thought", "Analysis completed successfully.")
                }
            except Exception as e:
                print(f"LangChain CoT failed: {e}. Falling back to deterministic rules.")
                pass
                
        # Mocking / Fallback logic to guarantee MVP execution
        multiplier = 1.0
        insights = []

        if signals["garment_demand_signal"] == "high_demand":
            multiplier += 0.2
            insights.append("Market demand for garments is currently high.")
        elif signals["garment_demand_signal"] == "low_demand":
            multiplier -= 0.1
            insights.append("Sluggish market demand detected.")

        if signals["days_to_festival"] < 15:
            multiplier += 0.15
            insights.append(f"Upcoming {signals['upcoming_festival']} festival within 15 days is expected to boost sales.")

        if signals["market_sentiment"] == "bearish":
            multiplier -= 0.05
            insights.append("Bearish macroeconomic sentiment might reduce discretionary spending.")

        # High quality layman conversational formatting for Fallback
        if multiplier > 1.0:
            narrative = "As your financial AI, I am optimistic about your upcoming runway. " + " ".join(insights) + " Because of these positive momentum indicators, I have adjusted your baseline demand forecast upwards to ensure you do not stock out."
        elif multiplier < 1.0:
            narrative = "As your financial AI, I advise slight caution right now. " + " ".join(insights) + " Due to these headwinds, I have conservatively lowered your projected demand so you don't overspend on excess inventory."
        else:
            narrative = "Market conditions appear stable at the moment. I haven't detected any major disruptive signals, so your baseline mathematical forecast remains the safest projection."

        return {
            "demand_multiplier": round(multiplier, 2),
            "reasoning": narrative
        }


class RAGIntegration:
    """
    Interfaces with Pinecone / Vector DB to retrieve past forecasts and historical performance.
    """
    def __init__(self):
        pass

    def retrieve_similar_periods(self, current_signals: dict):
        """
        Retrieves similar past periods based on current market context.
        """
        # Mock retrieval
        return {
            "past_accuracy": 0.85,
            "similar_period_growth": 1.12,
            "notes": "Similar market conditions last year resulted in 12% growth."
        }
