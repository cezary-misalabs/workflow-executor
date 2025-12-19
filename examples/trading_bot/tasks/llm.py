"""LLM processing tasks."""

import time
from typing import Any

from prefect import task


@task(name="extract-with-llm")
def extract_insights(market_data: dict[str, Any], sentiment_data: dict[str, Any]) -> dict[str, Any]:
    """
    Use LLM to extract insights from market and sentiment data.

    In production, this would call OpenAI, Anthropic, or other LLM APIs.
    """
    print("🤖 Extracting insights with LLM...")
    time.sleep(2)  # Simulate LLM API call

    # Simulated LLM analysis
    combined_sentiment = (
        sentiment_data["news_sentiment"] * 0.6 + sentiment_data["social_sentiment"] * 0.4
    )

    return {
        "symbol": market_data["symbol"],
        "overall_sentiment": combined_sentiment,
        "price_momentum": "bullish" if market_data["change"] > 0 else "bearish",
        "recommendation": "buy"
        if combined_sentiment > 0.6 and market_data["change"] > 0
        else "hold",
        "confidence": 0.82,
        "reasoning": f"Strong positive sentiment ({combined_sentiment:.2f}) combined with "
        f"price momentum ({market_data['change']:.2f}%)",
    }
