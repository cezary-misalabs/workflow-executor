#!/usr/bin/env python
"""
Run the trading bot workflow.

Usage:
    # Single symbol
    uv run python run_trading_bot.py

    # Multiple symbols
    uv run python run_trading_bot.py --multi

    # Custom symbol
    uv run python run_trading_bot.py --symbol TSLA
"""

import argparse

from workflows.trading_bot import multi_symbol_trading_flow, trading_bot_flow


def main() -> None:
    """Run trading bot workflows."""
    parser = argparse.ArgumentParser(description="Run trading bot workflow")
    parser.add_argument("--symbol", type=str, default="AAPL", help="Stock symbol to trade")
    parser.add_argument(
        "--multi", action="store_true", help="Run multi-symbol trading for AAPL, TSLA, GOOGL"
    )

    args = parser.parse_args()

    if args.multi:
        # Run multiple symbols in parallel
        symbols = ["AAPL", "TSLA", "GOOGL"]
        result = multi_symbol_trading_flow(symbols)
        print(f"\n📈 Results: {result}")
    else:
        # Run single symbol
        result = trading_bot_flow(args.symbol)
        print(f"\n📈 Result: {result}")


if __name__ == "__main__":
    main()
