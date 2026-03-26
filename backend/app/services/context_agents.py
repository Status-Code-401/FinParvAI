import os
import re
import json
import xml.etree.ElementTree as ET
from datetime import date, datetime, timedelta
from typing import Any

# ────────────────────────────────────────────────────────────────────────────
# Attempt to import scraping libs — both are in requirements.txt
# ────────────────────────────────────────────────────────────────────────────
# ────────────────────────────────────────────────────────────────────────────
# Agent Layer: Live Context Discovery (Pure Webscraping)
# ────────────────────────────────────────────────────────────────────────────

try:
    import httpx
    try:
        from bs4 import BeautifulSoup
    except ImportError:
        BeautifulSoup = None  # type: ignore[assignment, misc]
    SCRAPING_AVAILABLE = True
except ImportError:
    SCRAPING_AVAILABLE = False

# ────────────────────────────────────────────────────────────────────────────
# Date-accurate Indian festival / garment peak calendar
# Keys are (month, day) tuples; each entry covers a window of ±7 days
# Sources: Indian public holiday list + garment industry trade peaks
# ────────────────────────────────────────────────────────────────────────────
FESTIVAL_CALENDAR = [
    {"name": "Pongal / Makar Sankranti", "date": date(2026, 1, 14), "multiplier": 1.25},
    {"name": "Republic Day Season",      "date": date(2026, 1, 26), "multiplier": 1.10},
    {"name": "Holi",                     "date": date(2026, 3, 13), "multiplier": 1.15},
    {"name": "Summer Launch",            "date": date(2026, 4, 14), "multiplier": 1.12},
    {"name": "Onam / Aadi Festival",     "date": date(2026, 8, 17), "multiplier": 1.10},
    {"name": "Navratri / Dussehra",      "date": date(2026, 10, 2),"multiplier": 1.35},
    {"name": "Diwali",                   "date": date(2026, 10, 20),"multiplier": 1.45},
    {"name": "Diwali Post-Season",       "date": date(2026, 11, 5),"multiplier": 1.20},
    {"name": "Wedding / New Year Season","date": date(2026, 12, 10),"multiplier": 1.30},
    # 2025 editions for backward compat
    {"name": "Diwali",                   "date": date(2025, 10, 20),"multiplier": 1.45},
    {"name": "Navratri / Dussehra",      "date": date(2025, 10, 2), "multiplier": 1.35},
    {"name": "Holi",                     "date": date(2025, 3, 14), "multiplier": 1.15},
    {"name": "Pongal / Makar Sankranti", "date": date(2025, 1, 14), "multiplier": 1.25},
]

POSITIVE_KEYWORDS = [
    "demand surge", "high demand", "sales up", "festive rush", "strong orders",
    "export growth", "textile boom", "garment orders up", "apparel surge",
    "consumption up", "retail growth", "fashion week", "wedding season",
    "order book full", "surplus revenue", "capacity utilization up", "market recovery",
    "favourable policy", "cotton price drop", "import duty cut",
    "textile park", "investment", "cluster", "pm mitra", "economic zone",
]
NEGATIVE_KEYWORDS = [
    "demand slump", "slowdown", "low demand", "export decline", "recession",
    "orders fall", "sales down", "textile slump", "apparel decline",
    "weavers distress", "job cuts", "cotton prices rise", "demand weak",
    "power shortage", "labour shortage", "inventory pileup", "shipment delay",
    "raw material spike", "input cost high", "global slowdown",
]


def _get_upcoming_festivals(days_ahead: int = 90) -> list[dict]:
    """Return festivals falling within the next `days_ahead` days, sorted by proximity."""
    today = date.today()
    window_end = today + timedelta(days=days_ahead)
    upcoming = []
    for f in FESTIVAL_CALENDAR:
        fdate: date = f["date"]  # always a date object by construction
        if today <= fdate <= window_end:
            upcoming.append({
                "name": f["name"],
                "date": str(fdate),
                "days_away": (fdate - today).days,
                "multiplier": f["multiplier"],
            })
    return sorted(upcoming, key=lambda x: x["days_away"])


def _scrape_news_sentiment() -> dict:
    """
    Fetch Google News RSS for India garment/textile industry.
    Returns sentiment and demand signal derived from headline keyword analysis.
    Falls back gracefully if network is unavailable.
    """
    RSS_URLS = [
        "https://news.google.com/rss/search?q=Tamil+Nadu+garment+industry+news&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=India+textile+manufacturing+demand&hl=en-IN&gl=IN&ceid=IN:en",
        "https://news.google.com/rss/search?q=apparel+export+india+surge+drop&hl=en-IN&gl=IN&ceid=IN:en",
    ]

    articles: list[dict] = []  # [{"title": str, "url": str}]
    if not SCRAPING_AVAILABLE:
        return {"headlines": [], "source_links": [], "sentiment": "neutral", "demand_signal": "moderate_demand", "source": "unavailable"}

    for url in RSS_URLS:
        try:
            resp = httpx.get(url, timeout=5.0, follow_redirects=True,
                             headers={"User-Agent": "Mozilla/5.0 (compatible; FinParvai/1.0)"})
            if resp.status_code == 200:
                root = ET.fromstring(resp.text)  # type: ignore[arg-type]
                for item in root.iter("item"):
                    title_el = item.find("title")
                    link_el  = item.find("link")
                    if title_el is not None and isinstance(title_el.text, str):
                        link_url = ""
                        # <link> in RSS is usually the element text; in Google RSS it
                        # can be a CDATA or a separate text node after the element.
                        if link_el is not None and link_el.text:
                            link_url = link_el.text.strip()
                        elif link_el is not None:
                            # Some parsers put the URL in the tail
                            link_url = (link_el.tail or "").strip()
                        articles.append({"title": title_el.text, "url": link_url})
                if articles:
                    break  # got enough from first URL
        except Exception:
            continue  # silently fall through to next URL or fallback

    headlines = [a["title"].lower() for a in articles]

    if not headlines:
        return {"headlines": [], "source_links": [], "sentiment": "neutral", "demand_signal": "moderate_demand", "source": "fallback"}

    positive_hits = sum(1 for h in headlines for kw in POSITIVE_KEYWORDS if kw in h)
    negative_hits = sum(1 for h in headlines for kw in NEGATIVE_KEYWORDS if kw in h)

    if positive_hits > negative_hits + 1:
        sentiment = "bullish"
        demand_signal = "high_demand"
    elif negative_hits > positive_hits + 1:
        sentiment = "bearish"
        demand_signal = "low_demand"
    else:
        sentiment = "neutral"
        demand_signal = "moderate_demand"

    return {
        "headlines": headlines[:5],
        "source_links": [{"title": a["title"], "url": a["url"]} for a in articles[:5]],
        "positive_signals": positive_hits,
        "negative_signals": negative_hits,
        "sentiment": sentiment,
        "demand_signal": demand_signal,
        "source": "google_news_rss",
        "sentiment_analysis": _generate_sentiment_analysis(
            headlines, positive_hits, negative_hits, sentiment
        ),
    }


def _generate_sentiment_analysis(
    headlines: list[str],
    positive_hits: int,
    negative_hits: int,
    sentiment: str,
) -> dict:
    """
    Converts raw headline keyword signals into a summary and an action insight.
    Returns {"summary": str, "action_insight": str}
    """
    total = positive_hits + negative_hits
    if total == 0:
        return {
            "summary": "No distinct market signals were detected in today's garment industry news.",
            "action_insight": "Maintain standard inventory levels. Monitor local buyer sentiment directly."
        }

    # Identify which specific themes appeared
    found_positive = [kw for kw in POSITIVE_KEYWORDS if any(kw in h for h in headlines)]
    found_negative = [kw for kw in NEGATIVE_KEYWORDS if any(kw in h for h in headlines)]

    # Build opening sentence based on overall balance
    if sentiment == "bullish":
        opening = (
            f"Market intelligence from {len(headlines)} live news sources is broadly optimistic for the "
            f"Indian garment sector, with {positive_hits} positive signal(s) outweighing {negative_hits} "
            f"negative one(s)."
        )
    elif sentiment == "bearish":
        opening = (
            f"Market intelligence from {len(headlines)} live news sources signals caution for the "
            f"Indian garment sector, with {negative_hits} bearish signal(s) outweighing {positive_hits} "
            f"positive one(s)."
        )
    else:
        opening = (
            f"Market intelligence from {len(headlines)} live news sources shows a mixed picture "
            f"for the Indian garment sector ({positive_hits} positive vs {negative_hits} negative signals)."
        )

    # Build theme sentence
    themes = []
    if found_positive:
        themes.append(f"Positive themes include: {', '.join(found_positive[:3])}.")
    if found_negative:
        themes.append(f"Concern areas flagged: {', '.join(found_negative[:3])}.")
    theme_sentence = " ".join(themes) if themes else ""

    # Build recommendation close
    if sentiment == "bullish":
        action = "Prioritize procurement of raw materials and maximize production runs to meet the anticipated demand surge."
    elif sentiment == "bearish":
        action = "Hold off on long-term raw material contracts. Liquidate existing stock with targeted localized marketing."
    else:
        action = "Continue standard procurement cycles. Keep a 10% buffer for unexpected demand spikes."

    summary = f"{opening} {theme_sentence}".strip()
    return {"summary": summary, "action_insight": action}


# ────────────────────────────────────────────────────────────────────────────
# Agents
# ────────────────────────────────────────────────────────────────────────────

class WebCrawlingAgent:
    """
    Gathers real market signals using:
    1. Date-accurate Indian festival calendar (deterministic, no API needed)
    2. Google News RSS scraping for live garment/textile sentiment
    """

    def gather_signals(self) -> dict:
        upcoming = _get_upcoming_festivals(days_ahead=45)

        nearest = upcoming[0] if upcoming else None
        festival_name = nearest["name"] if nearest else "None"
        days_to_festival = nearest["days_away"] if nearest else 999

        news = _scrape_news_sentiment()

        return {
            "upcoming_festival": festival_name,
            "days_to_festival": days_to_festival,
            "market_sentiment": news["sentiment"],
            "garment_demand_signal": news["demand_signal"],
            "sentiment_summary": news.get("sentiment_analysis", {}).get("summary", ""),
            "action_insight": news.get("sentiment_analysis", {}).get("action_insight", ""),
            "source_links": news.get("source_links", []),
            "headlines": news.get("headlines", []),
            "upcoming_festivals": upcoming,
            "news_source": news.get("source", "fallback"),
            "positive_news_signals": news.get("positive_signals", 0),
            "negative_news_signals": news.get("negative_signals", 0),
        }


class ContextAnalysisAgent:
    """
    Converts qualitative signals into a demand_multiplier and chain-of-thought reasoning.
    Uses LangChain/OpenAI when available; falls back to deterministic rules.
    """

    def __init__(self):
        self.llm_key = os.environ.get("OPENAI_API_KEY", None)

    def analyze_context(self, signals: dict) -> dict:
        if self.llm_key and isinstance(self.llm_key, str) and len(self.llm_key) > 10:
            try:
                from langchain_openai import ChatOpenAI
                import json

                llm = ChatOpenAI(temperature=0.2, openai_api_key=self.llm_key)
                prompt = (
                    f"You are a friendly, expert financial advisor for a small Indian garment business. "
                    f"Review these real-world market signals gathered from live news and the festival calendar: {signals}. "
                    "Output a strict JSON with two fields: "
                    "'demand_multiplier' (float near 1.0; >1.0 = growing demand, <1.0 = shrinking), "
                    "'chain_of_thought' (one friendly paragraph explaining your adjustment to the business owner, no jargon)."
                )
                response = llm.invoke(prompt).content
                clean = response.replace("```json", "").replace("```", "").strip()
                parsed = json.loads(clean)
                return {
                    "demand_multiplier": parsed.get("demand_multiplier", 1.0),
                    "reasoning": parsed.get("chain_of_thought", "Analysis completed."),
                }
            except Exception as e:
                print(f"LangChain CoT failed: {e}. Falling back to deterministic rules.")

        # ── Deterministic fallback (always works without API keys) ──────────
        multiplier = 1.0
        insights = []

        demand = signals.get("garment_demand_signal", "moderate_demand")
        if demand == "high_demand":
            multiplier += 0.20
            insights.append("Live news signals show strong garment market demand right now.")
        elif demand == "low_demand":
            multiplier -= 0.10
            insights.append("News headlines indicate sluggish demand in the garment sector.")

        days_to = signals.get("days_to_festival", 999)
        festival = signals.get("upcoming_festival", "")
        upcoming_all = signals.get("upcoming_festivals", [])

        if days_to <= 15:
            # Use the specific festival multiplier if available
            fest_mult = upcoming_all[0]["multiplier"] if upcoming_all else 1.20
            boost = round(fest_mult - 1.0, 2)
            multiplier += boost
            insights.append(f"{festival} is just {days_to} days away — expect a {int(boost*100)}% demand uplift.")
        elif days_to <= 45:
            multiplier += 0.08
            insights.append(f"{festival} is approaching in {days_to} days. Start building inventory now.")

        if signals.get("market_sentiment") == "bearish":
            multiplier -= 0.05
            insights.append("Macroeconomic sentiment is cautious — some consumers may delay discretionary spending.")
        elif signals.get("market_sentiment") == "bullish":
            multiplier += 0.05
            insights.append("Overall market sentiment is positive, which typically lifts discretionary purchases.")

        multiplier = round(max(0.6, min(multiplier, 2.0)), 2)

        # Build layman narrative
        pos = signals.get("positive_news_signals", 0)
        neg = signals.get("negative_news_signals", 0)
        news_src = signals.get("news_source", "fallback")
        headlines = signals.get("headlines", [])
        is_tn_relevant = any("tamil nadu" in h.lower() or "tirupur" in h.lower() or "chennai" in h.lower() for h in headlines)
        
        region_note = " (Detected regional signals for Tamil Nadu/Tirupur.)" if is_tn_relevant else ""
        news_note = (
            f" (Based on {pos} positive and {neg} negative signals from live news.{region_note})"
            if news_src == "google_news_rss" else " (Live news unavailable — using calendar only.)"
        )

        if multiplier > 1.05:
            narrative = (
                "As your financial AI, I'm optimistic about your upcoming runway. "
                + " ".join(insights)
                + " I've adjusted your demand forecast upward so you don't stock out during the peak."
                + news_note
            )
        elif multiplier < 0.95:
            narrative = (
                "As your financial AI, I'm advising slight caution. "
                + " ".join(insights)
                + " I've conservatively lowered your projected demand to avoid overspending on inventory."
                + news_note
            )
        else:
            narrative = (
                "Market conditions are broadly stable. " + " ".join(insights)
                + " Your baseline forecast is a safe projection." + news_note
            )

        return {
            "demand_multiplier": multiplier,
            "reasoning": narrative,
        }


class RAGIntegration:
    """
    Interfaces with Pinecone / Vector DB to retrieve past forecasts.
    Currently mocked.
    """
    def retrieve_similar_periods(self, current_signals: dict):
        return {
            "past_accuracy": 0.85,
            "similar_period_growth": 1.12,
            "notes": "Similar market conditions last year resulted in 12% growth.",
        }
