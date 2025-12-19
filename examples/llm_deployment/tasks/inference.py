"""Inference tasks - running inference on deployed models."""

import time
from typing import Any

import httpx
from prefect import task


@task(name="run-inference", retries=2, retry_delay_seconds=3)
def run_inference(
    deployment: dict[str, Any],
    question: str = "What are the key benefits of using workflow orchestration in ML pipelines?",
) -> dict[str, Any]:
    """
    Run inference on the deployed model using vLLM OpenAI-compatible API.

    Sends a question to the deployed LLM endpoint and returns the response.

    Args:
        deployment: Deployment information including endpoint URL
        question: The question to ask the model

    Returns:
        Inference result including question, answer, and metadata
    """
    # Construct full model ID (vendor/name) for vLLM
    vendor = deployment.get("vendor", "")
    name = deployment.get("name", "unknown")
    model_id = f"{vendor}/{name}" if vendor else name

    print(f"💬 Running inference on {model_id}...")
    print(f"   Question: {question[:80]}{'...' if len(question) > 80 else ''}")

    endpoint_url = deployment["endpoint_url"]
    start_time = time.time()

    # Use vLLM OpenAI-compatible API
    response = httpx.post(
        f"{endpoint_url}/v1/chat/completions",
        json={
            "model": model_id,
            "messages": [{"role": "user", "content": question}],
            "max_tokens": 512,
            "temperature": 0.7,
        },
        timeout=120.0,
    )
    response.raise_for_status()
    result = response.json()

    # Extract answer from OpenAI-compatible response
    answer = result["choices"][0]["message"]["content"]
    latency_ms = (time.time() - start_time) * 1000

    # Extract token usage if available
    usage = result.get("usage", {})

    inference_result = {
        "model": model_id,
        "endpoint": endpoint_url,
        "question": question,
        "answer": answer,
        "latency_ms": round(latency_ms, 2),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
    }

    print(f"   ✓ Inference complete ({inference_result['latency_ms']:.0f}ms)")
    if usage:
        print(f"   → Tokens: {usage.get('total_tokens', 'N/A')} total")

    return inference_result
