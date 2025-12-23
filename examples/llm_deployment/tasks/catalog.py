"""Model catalog tasks - fetching and selecting models from the catalog service."""

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
        models_raw = data.get("models", [])
        models: list[dict[str, Any]] = models_raw
        print(f"   ✓ Found {len(models)} models in catalog")
        return models
    except httpx.HTTPError as e:
        print(f"   ✗ Catalog API error: {e}")
        raise


@task(name="select-recommended-model")
def select_recommended_model(
    models: list[dict[str, Any]], model_name: str | None = None
) -> dict[str, Any]:
    """
    Select the recommended model from the catalog.

    Searches for the specified model name in the returned models list.
    Model names are matched in "vendor/name" format.
    Defaults to 'Llama-3.1-8B-Instruct' if no model name is provided.

    Args:
        models: List of available models from catalog
        model_name: Optional model name to select (default: Llama-3.1-8B-Instruct)

    Returns:
        The selected model definition
    """
    print("🎯 Selecting recommended model...")

    target_model_name = model_name if model_name else "Llama-3.1-8B-Instruct"

    # Find the model in the catalog (match by vendor/name format)
    selected_model = None
    for model in models:
        vendor = model.get("vendor", "")
        name = model.get("name", "")
        full_model_name = f"{vendor}/{name}" if vendor else name

        if full_model_name == target_model_name:
            selected_model = model
            break

    if selected_model is None:
        # Build list of available models in vendor/name format for error message
        available_models: list[str] = []
        for m in models:
            vendor = m.get("vendor", "")
            name = m.get("name", "")
            model_str = f"{vendor}/{name}" if vendor else name
            available_models.append(model_str)

        raise ValueError(
            f"Model '{target_model_name}' not found in catalog. "
            f"Available models: {available_models}"
        )

    print(f"   ✓ Selected: {selected_model.get('name')}")
    print(f"   → Provider: {selected_model.get('provider', 'unknown')}")

    return selected_model
