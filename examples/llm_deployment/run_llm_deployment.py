"""
Entry point for running the LLM deployment pipeline example.

This demonstrates a sequential workflow where each step depends
on the output of the previous step:

1. Fetch models from catalog service
2. Select recommended model (hardcoded to LLama 3.1 8B)
3. Deploy model (simulated, returns hardcoded endpoint)
4. Run inference on deployed model

Usage:
    # Default settings
    uv run python examples/llm_deployment/run_llm_deployment.py

    # Custom catalog URL
    uv run python examples/llm_deployment/run_llm_deployment.py --catalog-url http://localhost:9090

    # Custom question
    uv run python examples/llm_deployment/run_llm_deployment.py --question "Explain transformers in ML"

    # Both custom options
    uv run python examples/llm_deployment/run_llm_deployment.py \\
        --catalog-url http://localhost:9090 \\
        --question "What is the difference between RAG and fine-tuning?"
"""

import argparse
import sys
from pathlib import Path

# Add project root to Python path
# ruff: noqa: E402
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.llm_deployment.workflows import llm_deployment_flow


def main() -> None:
    """Run the LLM deployment pipeline workflow."""
    parser = argparse.ArgumentParser(
        description="Run LLM deployment pipeline workflow example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --question "What is machine learning?"
  %(prog)s --catalog-url http://localhost:9090
        """,
    )
    parser.add_argument(
        "--catalog-url",
        type=str,
        default="http://localhost:9090",
        help="Model catalog service URL (default: http://localhost:9090)",
    )
    parser.add_argument(
        "--question",
        type=str,
        default=None,
        help="Question to ask the deployed model (default: about workflow orchestration)",
    )

    args = parser.parse_args()

    print("\n" + "🌟" * 35)
    print("  LLM DEPLOYMENT PIPELINE EXAMPLE")
    print("🌟" * 35 + "\n")

    result = llm_deployment_flow(
        catalog_url=args.catalog_url,
        question=args.question,
    )

    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
