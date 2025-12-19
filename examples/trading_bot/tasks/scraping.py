"""Data and sentiment scraping tasks."""

import time
from typing import Any

from prefect import task


@task(name="scrape-market-data", retries=3, retry_delay_seconds=5)
def scrape_market_data(symbol: str) -> dict[str, Any]:
    """
    Scrape market data for a given symbol.

    In production, this would fetch real market data from APIs.
    """
    print(f"🔍 Scraping market data for {symbol}...")
    time.sleep(1)  # Simulate API call

    return {
        "symbol": symbol,
        "price": 150.25,
        "volume": 1_000_000,
        "change": 2.5,
        "timestamp": time.time(),
    }


@task(name="scrape-sentiment", retries=3, retry_delay_seconds=5)
def scrape_sentiment(symbol: str) -> dict[str, Any]:
    """
    Scrape sentiment data from news and social media.

    In production, this would analyze news articles, tweets, etc.
    """
    print(f"📰 Scraping sentiment for {symbol}...")
    time.sleep(1.5)  # Simulate API call

    return {
        "symbol": symbol,
        "news_sentiment": 0.75,  # -1 to 1 scale
        "social_sentiment": 0.65,
        "article_count": 42,
        "timestamp": time.time(),
    }
