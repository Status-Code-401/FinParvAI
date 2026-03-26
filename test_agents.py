import os
import sys
import json
from datetime import date

# Add backend to path
sys.path.insert(0, os.path.join(os.getcwd(), "backend"))

from app.services.context_agents import WebCrawlingAgent, ContextAnalysisAgent

def test_agents():
    print("Testing WebCrawlingAgent...")
    crawler = WebCrawlingAgent()
    signals = crawler.gather_signals()
    print("Headlines found:", signals.get("headlines", []))
    print("Signals found:", json.dumps(signals, indent=2, default=str))
    
    print("\nTesting ContextAnalysisAgent...")
    analyzer = ContextAnalysisAgent()
    context = analyzer.analyze_context(signals)
    print("Context analysis:", json.dumps(context, indent=2))

if __name__ == "__main__":
    test_agents()
