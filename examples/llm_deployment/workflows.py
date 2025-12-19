"""
LLM Deployment workflow demonstrating sequential execution.

This workflow demonstrates a realistic ML ops pipeline:
1. Fetch models from catalog (API call)
2. Select recommended model (decision step)
3. Deploy model to endpoint (provisioning)
4. Run inference (use the deployed model)

Each step depends on the output of the previous step,
making this a perfect example of sequential workflow execution.
"""

from typing import Any

from prefect import flow

from examples.llm_deployment.tasks.catalog import fetch_models, select_recommended_model
from examples.llm_deployment.tasks.deployment import deploy_model
from examples.llm_deployment.tasks.inference import run_inference


@flow(name="llm-deployment-pipeline", log_prints=True)
def llm_deployment_flow(
    catalog_url: str = "http://localhost:9090",
    question: str | None = None,
) -> dict[str, Any]:
    """
    LLM Deployment Pipeline - Sequential workflow example.

    This demonstrates a complete ML ops workflow where each step
    depends on the previous step's output:

    fetch_models → select_model → deploy_model → run_inference

    Args:
        catalog_url: URL of the model catalog service
        question: Optional custom question for inference

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
    print(f"❓ Question: {question[:60]}{'...' if len(question) > 60 else ''}\n")

    # STEP 1: Fetch available models from catalog
    print("-" * 70)
    print("STEP 1/4: Fetch Models from Catalog")
    print("-" * 70)
    models = fetch_models(catalog_url)

    # STEP 2: Select the recommended model
    print("\n" + "-" * 70)
    print("STEP 2/4: Select Recommended Model")
    print("-" * 70)
    selected_model = select_recommended_model(models)

    # STEP 3: Deploy the model
    print("\n" + "-" * 70)
    print("STEP 3/4: Deploy Model")
    print("-" * 70)
    deployment = deploy_model(selected_model)

    # STEP 4: Run inference
    print("\n" + "-" * 70)
    print("STEP 4/4: Run Inference")
    print("-" * 70)
    inference_result = run_inference(deployment, question)

    # FINAL SUMMARY
    print("\n" + "=" * 70)
    print("✅ PIPELINE COMPLETE")
    print("=" * 70)

    print(f"\n📊 Summary:")
    print(f"   • Model: {selected_model['name']}")
    print(f"   • Endpoint: {deployment['endpoint_url']}")
    print(f"   • Latency: {inference_result['latency_ms']:.0f}ms")

    print(f"\n💬 Question:")
    print(f"   {question}")

    print(f"\n🤖 Answer:")
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
            "deploy_model": deployment,
            "inference": inference_result,
        },
        "summary": {
            "model": selected_model["name"],
            "endpoint": deployment["endpoint_url"],
            "question": question,
            "answer": inference_result["answer"],
            "latency_ms": inference_result["latency_ms"],
        },
    }


if __name__ == "__main__":
    # Quick test - run directly
    result = llm_deployment_flow()
