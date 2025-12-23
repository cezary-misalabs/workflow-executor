"""Data preprocessing and cleaning tasks."""

import time
from typing import Any

from prefect import task


@task(name="clean-and-normalize")
def clean_and_normalize(insights: dict[str, Any]) -> dict[str, Any]:
    """
    Clean and normalize extracted insights for model input.

    In production, this would handle missing values, outliers, scaling, etc.
    """
    print("🧹 Cleaning and normalizing data...")
    time.sleep(0.5)  # Simulate preprocessing

    # Normalize sentiment to 0-1 range
    normalized_sentiment = (insights["overall_sentiment"] + 1) / 2

    # Convert recommendation to numeric
    recommendation_score = {"buy": 1.0, "hold": 0.5, "sell": 0.0}.get(
        insights["recommendation"], 0.5
    )

    return {
        "symbol": insights["symbol"],
        "features": {
            "sentiment_normalized": normalized_sentiment,
            "momentum_signal": 1.0 if insights["price_momentum"] == "bullish" else 0.0,
            "recommendation_score": recommendation_score,
            "confidence": insights["confidence"],
        },
        "metadata": {
            "original_recommendation": insights["recommendation"],
            "reasoning": insights["reasoning"],
        },
    }
