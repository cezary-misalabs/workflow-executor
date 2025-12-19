"""
Entry point for running the trading bot example.

This demonstrates how to execute workflows built with the workflow-executor framework.

Usage:
    # Single symbol trading
    uv run python examples/trading_bot/run_trading_bot.py --symbol AAPL

    # Multi-symbol trading (parallel)
    uv run python examples/trading_bot/run_trading_bot.py --multi
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.trading_bot.workflows import multi_symbol_trading_flow, trading_bot_flow


def main() -> None:
    """Run the trading bot workflow."""
    parser = argparse.ArgumentParser(description="Run trading bot workflow example")
    parser.add_argument(
        "--symbol",
        type=str,
        default="AAPL",
        help="Stock symbol to trade (default: AAPL)",
    )
    parser.add_argument(
        "--multi",
        action="store_true",
        help="Run multi-symbol trading in parallel",
    )

    args = parser.parse_args()

    if args.multi:
        # Run parallel workflows for multiple symbols
        symbols = ["AAPL", "TSLA", "GOOGL", "MSFT"]
        print(f"\n🚀 Starting multi-symbol trading for: {', '.join(symbols)}\n")
        result = multi_symbol_trading_flow(symbols)
        print("\n" + "=" * 60)
        print("📊 Multi-Symbol Trading Results:")
        print("=" * 60)
        for symbol, trade_result in result.items():
            if "error" in trade_result:
                print(f"  {symbol}: ❌ {trade_result['status']} - {trade_result['error']}")
            else:
                print(f"  {symbol}: ✅ {trade_result['action']} - {trade_result['trade_id']}")
    else:
        # Run single symbol workflow
        print(f"\n🚀 Starting trading bot for {args.symbol}\n")
        result = trading_bot_flow(args.symbol)
        print("\n" + "=" * 60)
        print("📊 Trading Result:")
        print("=" * 60)
        print(f"  Symbol: {result['symbol']}")
        print(f"  Action: {result['action']}")
        print(f"  Trade ID: {result['trade_id']}")


if __name__ == "__main__":
    main()
