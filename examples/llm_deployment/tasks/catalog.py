"""Model catalog tasks - fetching and selecting models from the catalog service."""

import time
from typing import Any

import httpx
from prefect import task


@task(name="fetch-models-from-catalog", retries=2, retry_delay_seconds=3)
def fetch_models(catalog_url: str = "http://localhost:9090") -> list[dict[str, Any]]:
    """
    Fetch available models from the Model Catalog Service.

    In production, this returns a list of all available models.
    For this demo, we make the real API call but will select a specific model.

    Args:
        catalog_url: Base URL of the model catalog service

    Returns:
        List of model definitions from the catalog
    """
    print(f"📚 Fetching models from catalog at {catalog_url}...")

    try:
        response = httpx.get(
            f"{catalog_url}/catalogue/api/v1/models",
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        models = data.get("models", [])
        print(f"   ✓ Found {len(models)} models in catalog")
        return models
    except httpx.HTTPError as e:
        print(f"   ✗ Catalog API error: {e}")
        raise


@task(name="select-recommended-model")
def select_recommended_model(models: list[dict[str, Any]]) -> dict[str, Any]:
    """
    Select the recommended model from the catalog.

    Searches for 'Llama-3.1-8B-Instruct' in the returned models list.

    Args:
        models: List of available models from catalog

    Returns:
        The selected model definition
    """
    print("🎯 Selecting recommended model...")

    target_model_name = "Llama-3.1-8B-Instruct"

    # Find the model in the catalog
    selected_model = None
    for model in models:
        if model.get("name") == target_model_name:
            selected_model = model
            break

    if selected_model is None:
        raise ValueError(f"Model '{target_model_name}' not found in catalog. "
                        f"Available models: {[m.get('name') for m in models]}")

    print(f"   ✓ Selected: {selected_model.get('name')}")
    print(f"   → Provider: {selected_model.get('provider', 'unknown')}")

    return selected_model
