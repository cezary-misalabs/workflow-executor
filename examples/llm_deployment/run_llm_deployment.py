"""
Entry point for running the LLM deployment pipeline example.

This demonstrates a sequential workflow where each step depends
on the output of the previous step:

1. Fetch models from catalog service
2. Select recommended model (default: Llama-3.1-8B-Instruct)
3. Find or deploy model (checks for existing deployments first)
4. Verify deployment (confirms model availability)
5. Run inference on deployed model

The pipeline automatically handles internal cluster endpoints by setting up
kubectl port-forward to provide local access. Both internal and external
endpoint URLs are tracked in the deployment information.

Prerequisites:
    - kubectl configured and connected to your cluster
    - Model catalog service running (default: http://localhost:9090)
    - Model management service running (default: http://localhost:8080)

Usage:
    # Default settings
    uv run python examples/llm_deployment/run_llm_deployment.py

    # Custom catalog URL
    uv run python examples/llm_deployment/run_llm_deployment.py --catalog-url http://localhost:9090

    # Custom question
    uv run python examples/llm_deployment/run_llm_deployment.py \\
        --question "Explain transformers in ML"

    # Custom model (use vendor/name format)
    uv run python examples/llm_deployment/run_llm_deployment.py \\
        --model "meta/Llama-3.1-70B-Instruct"

    # All custom options
    uv run python examples/llm_deployment/run_llm_deployment.py \\
        --catalog-url http://localhost:9090 \\
        --model "meta/Llama-3.1-8B-Instruct" \\
        --question "What is the difference between RAG and fine-tuning?"
"""

import argparse
import subprocess
import sys
import time
from pathlib import Path

import httpx

# Add project root to Python path
# ruff: noqa: E402
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from examples.llm_deployment.workflows import llm_deployment_flow


def is_prefect_server_running() -> bool:
    """
    Check if Prefect server is running.

    Returns:
        True if server is accessible, False otherwise
    """
    try:
        response = httpx.get("http://127.0.0.1:4200/api/health", timeout=2.0)
        return response.status_code == 200
    except (httpx.ConnectError, httpx.TimeoutException):
        return False


def start_prefect_server() -> None:
    """
    Start Prefect server in the background as a daemon process.

    The server will continue running even after the script terminates.
    """
    print("🚀 Starting Prefect server in the background...")

    # Start Prefect server as a detached background process
    # Using nohup to keep it running after script exits
    subprocess.Popen(
        ["prefect", "server", "start"],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
    )

    # Wait for server to become ready
    max_retries = 30
    for _attempt in range(max_retries):
        time.sleep(1)
        if is_prefect_server_running():
            print("   ✓ Prefect server is running")
            return

    print("   ⚠ Warning: Prefect server may not be fully ready yet")


def ensure_prefect_server() -> None:
    """Ensure Prefect server is running, start it if needed."""
    if is_prefect_server_running():
        print("✓ Prefect server is already running")
    else:
        print("⚠ Prefect server is not running")
        start_prefect_server()


def main() -> None:
    """Run the LLM deployment pipeline workflow."""
    parser = argparse.ArgumentParser(
        description="Run LLM deployment pipeline workflow example",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s
  %(prog)s --question "What is machine learning?"
  %(prog)s --model "Llama-3.1-70B-Instruct"
  %(prog)s --catalog-url http://localhost:9090 --model "Llama-3.1-8B-Instruct"
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
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name to deploy (default: Llama-3.1-8B-Instruct)",
    )

    args = parser.parse_args()

    print("\n" + "🌟" * 35)
    print("  LLM DEPLOYMENT PIPELINE EXAMPLE")
    print("🌟" * 35 + "\n")

    # Ensure Prefect server is running
    ensure_prefect_server()
    print()

    result = llm_deployment_flow(
        catalog_url=args.catalog_url,
        question=args.question,
        model=args.model,
    )

    # Exit with appropriate code
    sys.exit(0 if result["success"] else 1)


if __name__ == "__main__":
    main()
