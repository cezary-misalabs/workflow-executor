"""
LLM Deployment workflow demonstrating sequential execution.

This workflow demonstrates a realistic ML ops pipeline:
1. Fetch models from catalog (API call)
2. Select recommended model (decision step)
3. Find or deploy model (check existing deployments first)
4. Verify deployment endpoint (confirm model availability)
5. Run inference (use the deployed model)

Each step depends on the output of the previous step,
making this a perfect example of sequential workflow execution.

The workflow handles both internal cluster endpoints and local access:
- Internal cluster endpoints are automatically port-forwarded to localhost
- Both internal and external endpoint URLs are tracked
- Port forwarding processes run in the background during workflow execution
"""

from typing import Any

from prefect import flow

from examples.llm_deployment.tasks.catalog import fetch_models, select_recommended_model
from examples.llm_deployment.tasks.deployment import (
    deploy_model,
    find_running_deployment,
    verify_deployment,
)
from examples.llm_deployment.tasks.inference import run_inference


@flow(name="llm-deployment-pipeline", log_prints=True)
def llm_deployment_flow(
    catalog_url: str = "http://localhost:9090",
    question: str | None = None,
    model: str | None = None,
) -> dict[str, Any]:
    """
    LLM Deployment Pipeline - Sequential workflow example.

    This demonstrates a complete ML ops workflow where each step
    depends on the previous step's output:

    fetch_models → select_model → find_or_deploy → verify → run_inference

    Args:
        catalog_url: URL of the model catalog service
        question: Optional custom question for inference
        model: Optional model name to select (default: Llama-3.1-8B-Instruct)

    Returns:
        Complete workflow result including all step outputs
    """
    # Default question if none provided
    if question is None:
        question = "What are the key benefits of using workflow orchestration in ML pipelines?"

    print("=" * 70)
    print("🔄 LLM DEPLOYMENT PIPELINE")
    print("=" * 70)
    print(f"\n📍 Catalog URL: {catalog_url}")
    if model:
        print(f"🤖 Model: {model}")
    print(f"❓ Question: {question[:60]}{'...' if len(question) > 60 else ''}\n")

    # STEP 1: Fetch available models from catalog
    print("-" * 70)
    print("STEP 1/5: Fetch Models from Catalog")
    print("-" * 70)
    models = fetch_models(catalog_url)

    # STEP 2: Select the recommended model
    print("\n" + "-" * 70)
    print("STEP 2/5: Select Recommended Model")
    print("-" * 70)
    selected_model = select_recommended_model(models, model)

    # STEP 3: Find or deploy the model
    print("\n" + "-" * 70)
    print("STEP 3/5: Find or Deploy Model")
    print("-" * 70)

    # Check for existing deployment first
    existing_deployment = find_running_deployment(selected_model)

    if existing_deployment:
        print("   ✓ Using existing deployment")
        deployment = existing_deployment
    else:
        print("   → Deploying new model...")
        deployment = deploy_model(selected_model)

    # STEP 4: Verify deployment
    print("\n" + "-" * 70)
    print("STEP 4/5: Verify Deployment")
    print("-" * 70)
    verified_deployment = verify_deployment(deployment)

    # STEP 5: Run inference
    print("\n" + "-" * 70)
    print("STEP 5/5: Run Inference")
    print("-" * 70)
    inference_result = run_inference(verified_deployment, question)

    # FINAL SUMMARY
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE")
    print("=" * 70)

    print("\n📊 Summary:")
    print(f"   • Model: {selected_model['name']}")
    print(f"   • Endpoint: {verified_deployment['endpoint_url']}")
    print(f"   • Latency: {inference_result['latency_ms']:.0f}ms")

    print("\n💬 Question:")
    print(f"   {question}")

    print("\n🤖 Answer:")
    # Format answer with proper indentation
    for line in inference_result["answer"].split("\n"):
        print(f"   {line}")

    print("\n" + "=" * 70)

    # Return comprehensive result
    return {
        "success": True,
        "pipeline": "llm-deployment",
        "steps": {
            "fetch_models": {"count": len(models)},
            "select_model": selected_model,
            "find_deployment": existing_deployment is not None,
            "deploy_model": deployment,
            "verify_deployment": verified_deployment,
            "inference": inference_result,
        },
        "summary": {
            "model": selected_model["name"],
            "endpoint": verified_deployment["endpoint_url"],
            "question": question,
            "answer": inference_result["answer"],
            "latency_ms": inference_result["latency_ms"],
        },
    }


if __name__ == "__main__":
    # Quick test - run directly
    result = llm_deployment_flow()
