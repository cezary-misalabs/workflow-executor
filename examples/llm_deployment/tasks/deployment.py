"""Model deployment tasks - deploying models to inference endpoints."""

import time
from typing import Any

import httpx
from prefect import task


@task(name="deploy-model", retries=2, retry_delay_seconds=5)
def deploy_model(model: dict[str, Any]) -> dict[str, Any]:
    """
    Deploy the selected model to an inference endpoint.

    In production, this would:
    - Provision infrastructure (GPU instances)
    - Pull model weights
    - Start inference server
    - Configure load balancing
    - Run health checks

    For this demo, we simulate deployment and return a hardcoded endpoint.

    Args:
        model: The model definition to deploy

    Returns:
        Deployment information including the endpoint URL
    """
    print(f"🚀 Deploying {model['name']}...")

    # Simulate deployment steps
    steps = [
        ("Provisioning GPU instance", 0.1),
        ("Pulling model weights", 0.1),
        ("Starting inference server", 0.1),
        ("Running health checks", 0.1),
    ]

    for step_name, duration in steps:
        print(f"   → {step_name}...")
        time.sleep(duration)

    #deployed_endpoint = "http://localhost:7070"
    deployed_endpoint = "http://52.91.14.233:11434"

    # Fetch actual model name from the deployed endpoint
    try:
        response = httpx.get(
            f"{deployed_endpoint}/v1/models",
            timeout=10.0,
        )
        response.raise_for_status()
        models_data = response.json()
        models_list = models_data.get("data", [])
        if models_list:
            deployed_model_id = models_list[0]["id"]
            print(f"   → Deployed model: {deployed_model_id}")
        else:
            models_list = models_data.get("models", [])
            if models_list:
                deployed_model_id = models_list[0]
                print(f"   → Deployed model: {deployed_model_id}")
            else:
                print("   ⚠ No models found in deployment response")
                deployed_model_id = model["name"]
    except (httpx.HTTPError, KeyError, IndexError) as e:
        print(f"   ⚠ Could not fetch model from endpoint: {e}")
        deployed_model_id = model["name"]

    # Hardcoded deployment endpoint for demo
    deployment = {
        "name": deployed_model_id,
        #"vendor": model.get("vendor", ""),
        "endpoint_url": deployed_endpoint,
        "docs_url": f"{deployed_endpoint}docs",
        "status": "running",
        "instance_type": "g5.xlarge",
        "gpu": "NVIDIA A10G",
        "deployed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
    }

    print(f"   ✓ Deployment complete!")
    print(f"   → Endpoint: {deployment['endpoint_url']}")
    print(f"   → Instance: {deployment['instance_type']} ({deployment['gpu']})")

    return deployment
