"""
Trading bot workflow demonstrating parallel and sequential execution.

This workflow:
1. Scrapes market data and sentiment in parallel
2. Processes results through LLM (sequential)
3. Cleans and normalizes data (sequential)
4. Runs prediction model (sequential)
5. Executes trade (sequential)
"""

from concurrent.futures import ThreadPoolExecutor, as_completed
from typing import Any

from prefect import flow

from workflows.tasks.llm import extract_insights
from workflows.tasks.prediction import execute_trade, run_prediction_model
from workflows.tasks.preprocessing import clean_and_normalize
from workflows.tasks.scraping import scrape_market_data, scrape_sentiment


@flow(name="trading-bot", log_prints=True)
def trading_bot_flow(symbol: str = "AAPL") -> dict[str, Any]:
    """
    Main trading bot workflow.

    This demonstrates:
    - Parallel execution: market data and sentiment scraping happen simultaneously
    - Sequential execution: LLM → preprocessing → prediction → trade execution

    Args:
        symbol: Stock symbol to trade (e.g., 'AAPL', 'TSLA')

    Returns:
        Trade execution result
    """
    print(f"🚀 Starting trading bot for {symbol}")
    print("=" * 60)

    # PHASE 1: PARALLEL DATA COLLECTION
    # Both scraping tasks run in parallel (independent operations)
    print("\n📊 Phase 1: Parallel data collection...")
    market_data_future = scrape_market_data.submit(symbol)
    sentiment_future = scrape_sentiment.submit(symbol)

    # Wait for both to complete
    market_data = market_data_future.result()
    sentiment_data = sentiment_future.result()

    # PHASE 2: SEQUENTIAL PROCESSING
    # Each step depends on the previous one
    print("\n🔄 Phase 2: Sequential processing pipeline...")

    # Step 1: LLM extracts insights from combined data
    insights = extract_insights(market_data, sentiment_data)

    # Step 2: Clean and normalize for model input
    processed_data = clean_and_normalize(insights)

    # Step 3: Run prediction model
    prediction = run_prediction_model(processed_data)

    # Step 4: Execute trade based on prediction
    print("\n💸 Phase 3: Trade execution...")
    result = execute_trade(prediction)

    print("\n" + "=" * 60)
    print(f"✅ Trading bot completed for {symbol}")
    print(f"   Action: {result['action']}")
    print(f"   Trade ID: {result['trade_id']}")

    return result


@flow(name="multi-symbol-trading")
def multi_symbol_trading_flow(symbols: list[str]) -> dict[str, Any]:
    """
    Run trading bot for multiple symbols in parallel.

    This demonstrates flow-level parallelism where each symbol
    gets its own independent workflow execution using ThreadPoolExecutor.

    Args:
        symbols: List of stock symbols to trade

    Returns:
        Dictionary mapping symbols to their trade results
    """
    print(f"🌐 Starting multi-symbol trading for: {', '.join(symbols)}")

    # Use ThreadPoolExecutor to run flows in parallel
    results = {}
    with ThreadPoolExecutor(max_workers=len(symbols)) as executor:
        # Submit all flows to executor
        future_to_symbol = {executor.submit(trading_bot_flow, symbol): symbol for symbol in symbols}

        # Collect results as they complete
        for future in as_completed(future_to_symbol):
            symbol = future_to_symbol[future]
            try:
                result = future.result()
                results[symbol] = result
            except Exception as exc:
                print(f"❌ {symbol} generated an exception: {exc}")
                results[symbol] = {"status": "failed", "error": str(exc)}

    print(f"\n✅ All trades completed for {len(symbols)} symbols")
    return results
