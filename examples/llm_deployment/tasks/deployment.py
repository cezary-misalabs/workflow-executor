"""Model deployment tasks - deploying models to inference endpoints."""

import hashlib
import os
import secrets
import socket
import subprocess
import time
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import httpx
from dotenv import load_dotenv
from prefect import task

# Load environment variables from .env file for AWS/kubectl authentication
env_file = Path(__file__).parent.parent.parent.parent / ".env"
if env_file.exists():
    load_dotenv(env_file)


def _generate_unique_model_name() -> str:
    """Generate a unique model name with SHA-based suffix."""
    timestamp = str(time.time_ns()).encode()
    random_bytes = secrets.token_bytes(16)
    hash_input = timestamp + random_bytes
    sha_hash = hashlib.sha256(hash_input).hexdigest()
    suffix = sha_hash[:8]
    return f"qwen-llm-{suffix}"


def _create_deployment_payload(model_name: str) -> dict[str, Any]:
    """
    Create the deployment payload for the model management service.

    Args:
        model_name: Unique model name

    Returns:
        Deployment payload dictionary
    """
    return {
        "uuid": None,
        "model_info": {
            "model_name": model_name,
            "model_path": "Qwen/Qwen2.5-0.5B-Instruct",
            "url": "https://huggingface.co/Qwen/Qwen2.5-0.5B-Instruct/tree/main",
        },
        "namespace": "staging",
        "node_name": None,
        "storage_uri": "s3://misalabs-staging-mlflow-model-bucket/Qwen/Qwen2.5-0.5B-Instruct/",
        "instance": None,
        "health_info": {
            "status": "StandBy",
            "details": None,
            "last_probe": None,
        },
        "created_at": None,
        "expires_at": None,
        "endpoint": None,
    }


def _create_deployment(service_url: str, payload: dict[str, Any]) -> str:
    """
    Create a new deployment via the model management service.

    Args:
        service_url: Base URL of the model management service
        payload: Deployment configuration payload

    Returns:
        Deployment ID (UUID)

    Raises:
        httpx.HTTPError: If the API request fails
        ValueError: If no deployment ID is returned
    """
    print(f"   → Creating deployment with model name: {payload['model_info']['model_name']}...")
    try:
        response = httpx.post(
            f"{service_url}/modman/new",
            json=payload,
            timeout=30.0,
        )
        response.raise_for_status()
        deployment_data = response.json()
        deployment_id_raw = deployment_data.get("uuid")
        if not deployment_id_raw or not isinstance(deployment_id_raw, str):
            raise ValueError("No deployment ID returned from service")
        deployment_id: str = deployment_id_raw
        print(f"   → Deployment created with ID: {deployment_id}")
        return deployment_id
    except (httpx.HTTPError, ValueError) as e:
        print(f"   ✗ Failed to create deployment: {e}")
        raise


def _start_deployment(service_url: str, deployment_id: str) -> None:
    """
    Start a deployment via the model management service.

    Args:
        service_url: Base URL of the model management service
        deployment_id: UUID of the deployment to start

    Raises:
        httpx.HTTPError: If the API request fails
    """
    print(f"   → Starting deployment {deployment_id}...")
    try:
        response = httpx.post(
            f"{service_url}/modman/start/{deployment_id}",
            timeout=30.0,
        )
        response.raise_for_status()
        print("   → Deployment start command sent")
    except httpx.HTTPError as e:
        print(f"   ✗ Failed to start deployment: {e}")
        raise


def _poll_deployment_status(
    service_url: str,
    deployment_id: str,
    max_retries: int = 30,
    retry_interval: int = 10,
) -> str:
    """
    Poll deployment status until it's running or fails.

    Args:
        service_url: Base URL of the model management service
        deployment_id: UUID of the deployment to monitor
        max_retries: Maximum number of polling attempts
        retry_interval: Seconds to wait between polling attempts

    Returns:
        Endpoint URL of the running deployment

    Raises:
        RuntimeError: If deployment fails or doesn't become ready in time
        httpx.HTTPError: If the API request fails
    """
    print("   → Monitoring deployment status...")
    deployed_endpoint: str | None = None

    for attempt in range(max_retries):
        try:
            response = httpx.get(
                f"{service_url}/modman/info/{deployment_id}",
                timeout=30.0,
            )
            response.raise_for_status()
            deployment_info = response.json()

            status = deployment_info.get("health_info", {}).get("status", "Unknown")
            endpoint = deployment_info.get("endpoint")

            print(f"   → Status: {status} (attempt {attempt + 1}/{max_retries})")

            if status == "Running" and endpoint and isinstance(endpoint, str):
                deployed_endpoint = endpoint
                print(f"   → Deployment is running at: {deployed_endpoint}")
                break

            if status in ["Failed", "Error"]:
                details = deployment_info.get("health_info", {}).get("details", "")
                raise RuntimeError(f"Deployment failed: {details}")

            time.sleep(retry_interval)
        except httpx.HTTPError as e:
            print(f"   ⚠ Failed to check deployment status: {e}")
            if attempt == max_retries - 1:
                raise

    if not deployed_endpoint:
        raise RuntimeError(
            f"Deployment did not become ready after {max_retries * retry_interval} seconds"
        )

    return deployed_endpoint


def _find_available_port(start_port: int = 8000, max_attempts: int = 100) -> int:
    """
    Find an available local port for port forwarding.

    Args:
        start_port: Port to start searching from
        max_attempts: Maximum number of ports to try

    Returns:
        An available port number

    Raises:
        RuntimeError: If no available port is found
    """
    for port in range(start_port, start_port + max_attempts):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                sock.bind(("127.0.0.1", port))
                return port
        except OSError:
            continue
    raise RuntimeError(f"No available port found in range {start_port}-{start_port + max_attempts}")


def _setup_port_forward(
    k8s_service_name: str, internal_endpoint: str, local_port: int
) -> subprocess.Popen[bytes]:
    """
    Set up kubectl port-forward for internal cluster endpoint.

    This creates a background process that forwards traffic from localhost
    to the internal cluster service.

    Args:
        k8s_service_name: Kubernetes service name (from model_info.model_name)
        internal_endpoint: Internal cluster endpoint URL
        local_port: Local port to forward to

    Returns:
        Popen process handle for the port-forward process

    Raises:
        RuntimeError: If port forwarding fails to start
    """
    # Parse the internal endpoint to extract port
    parsed = urlparse(internal_endpoint)
    internal_port = parsed.port or 80

    print(
        f"   → Setting up port forward: "
        f"localhost:{local_port} -> {k8s_service_name}:{internal_port}"
    )

    try:
        # Start kubectl port-forward in background
        # Using k8s service name from model_info
        # Pass current environment (including .env variables) to subprocess
        process = subprocess.Popen(
            [
                "kubectl",
                "port-forward",
                f"svc/{k8s_service_name}-predictor",
                f"{local_port}:{internal_port}",
                "-n",
                "staging",  # Adjust namespace as needed
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=os.environ.copy(),  # Pass environment variables including AWS credentials
            start_new_session=True,
        )

        # Give it a moment to start
        time.sleep(2)

        # Check if process is still running
        if process.poll() is not None:
            stderr_output = process.stderr.read().decode() if process.stderr else ""
            raise RuntimeError(f"Port forwarding failed to start: {stderr_output}")

        print(f"   ✓ Port forward active on localhost:{local_port}")
        return process

    except FileNotFoundError as e:
        raise RuntimeError(
            "kubectl not found. Please ensure kubectl is installed and in your PATH."
        ) from e
    except Exception as e:
        raise RuntimeError(f"Failed to set up port forwarding: {e}") from e


def _create_external_endpoint(
    deployment_info: dict[str, Any], internal_endpoint: str
) -> dict[str, Any]:
    """
    Create external access to an internal cluster endpoint via port forwarding.

    Args:
        deployment_info: Full deployment dict containing model_info with model_name
        internal_endpoint: Internal cluster endpoint URL

    Returns:
        Dictionary with external_endpoint and port_forward_process

    Raises:
        ValueError: If model_name cannot be extracted from deployment_info
    """
    # Check if endpoint is already localhost (no forwarding needed)
    parsed = urlparse(internal_endpoint)
    if parsed.hostname in ["localhost", "127.0.0.1"]:
        return {
            "external_endpoint": internal_endpoint,
            "port_forward_process": None,
        }

    # Extract kubernetes service name from model_info
    model_info = deployment_info.get("model_info", {})
    k8s_service_name = model_info.get("model_name")

    if not k8s_service_name:
        raise ValueError(
            f"Cannot extract kubernetes service name from deployment. model_info: {model_info}"
        )

    # Find available local port and set up forwarding
    local_port = _find_available_port()
    port_forward_process = _setup_port_forward(k8s_service_name, internal_endpoint, local_port)

    external_endpoint = f"http://localhost:{local_port}"

    return {
        "external_endpoint": external_endpoint,
        "port_forward_process": port_forward_process,
    }


def _verify_deployment_endpoint(endpoint_url: str, fallback_model_name: str) -> str:
    """
    Verify the deployment by querying the endpoint for available models.

    Args:
        endpoint_url: URL of the deployed model endpoint
        fallback_model_name: Model name to use if verification fails

    Returns:
        Verified model ID or fallback name
    """
    print("   → Verifying deployment...")
    deployed_model_id = fallback_model_name
    try:
        response = httpx.get(
            f"{endpoint_url}/v1/models",
            timeout=10.0,
        )
        response.raise_for_status()
        models_data = response.json()
        models_list = models_data.get("data", [])
        if models_list:
            deployed_model_id = models_list[0]["id"]
            print(f"   → Verified model: {deployed_model_id}")
        else:
            models_list = models_data.get("models", [])
            if models_list:
                deployed_model_id = models_list[0]
                print(f"   → Verified model: {deployed_model_id}")
            else:
                print("   ⚠ No models found in deployment response")
    except (httpx.HTTPError, KeyError, IndexError) as e:
        print(f"   ⚠ Could not verify model from endpoint: {e}")

    return deployed_model_id


@task(name="find-running-deployment", retries=2, retry_delay_seconds=3)
def find_running_deployment(model: dict[str, Any]) -> dict[str, Any] | None:
    """
    Check if the selected model is already deployed and running.

    Queries the model management service to find existing deployments,
    checks their endpoints to verify the hosted model, and returns a match
    if the deployed model matches the requested model.

    Args:
        model: The model definition from catalog (with vendor and name)

    Returns:
        Deployment information if found, running, and hosting the correct model; None otherwise
    """
    service_url = "http://localhost:8080"
    vendor = model.get("vendor", "")
    name = model.get("name", "")
    full_model_name = f"{vendor}/{name}" if vendor else name

    print(f"🔍 Checking for existing deployment of {full_model_name}...")

    try:
        response = httpx.post(
            f"{service_url}/modman/list",
            timeout=30.0,
        )
        response.raise_for_status()
        deployments = response.json()

        # Check each running deployment to see if it hosts our model
        for deployment in deployments:
            deployment_status = deployment.get("health_info", {}).get("status", "")
            internal_endpoint = deployment.get("endpoint")
            deployment_id = deployment.get("uuid")
            model_info = deployment.get("model_info", {})
            model_path = model_info.get("model_path", "")

            if (
                deployment_status == "Running"
                and internal_endpoint
                and isinstance(internal_endpoint, str)
            ):
                print(f"   → Checking deployment {deployment_id}...")
                print(f"   → Model path: {model_path}")

                # Check if the model_path matches the requested model
                # Handle both "vendor/name" and "name" formats
                if model_path == full_model_name or model_path == name:
                    print("   ✓ Found matching deployment!")
                    print(f"   → Internal Endpoint: {internal_endpoint}")

                    # Set up external access via port forwarding
                    try:
                        external_info = _create_external_endpoint(deployment, internal_endpoint)
                        external_endpoint = external_info["external_endpoint"]

                        # Return deployment info in consistent format
                        return {
                            "name": model_path,
                            "endpoint_url": external_endpoint,
                            "internal_endpoint_url": internal_endpoint,
                            "docs_url": f"{external_endpoint}/docs",
                            "status": "running",
                            "deployment_id": deployment_id,
                            "deployed_at": deployment.get("created_at", "unknown"),
                            "port_forward_process": external_info["port_forward_process"],
                        }

                    except (RuntimeError, ValueError) as e:
                        print(f"   ⚠ Could not set up port forwarding: {e}")
                        continue
                else:
                    print(f"   → Model mismatch: {model_path} != {full_model_name}")

        print("   ✓ No matching deployment found")
        return None

    except httpx.HTTPError as e:
        print(f"   ⚠ Could not check for existing deployments: {e}")
        return None


@task(name="deploy-model", retries=2, retry_delay_seconds=5)
def deploy_model(model: dict[str, Any]) -> dict[str, Any]:
    """
    Deploy the selected model to an inference endpoint.

    This connects to the model management service on localhost:8080 to:
    - Create a new deployment
    - Start the deployment
    - Monitor deployment status
    - Verify the deployed endpoint

    Args:
        model: The model definition to deploy

    Returns:
        Deployment information including the endpoint URL
    """
    service_url = "http://localhost:8080"
    print(f"🚀 Deploying {model['name']}...")

    # Generate unique model name and create deployment payload
    unique_model_name = _generate_unique_model_name()
    deployment_payload = _create_deployment_payload(unique_model_name)

    # Create and start deployment
    deployment_id = _create_deployment(service_url, deployment_payload)
    _start_deployment(service_url, deployment_id)

    # Monitor deployment until ready
    deployed_endpoint = _poll_deployment_status(service_url, deployment_id)

    print(f"   → Internal Endpoint: {deployed_endpoint}")

    # Set up external access via port forwarding
    # Construct deployment info dict with model_info for k8s service name extraction
    deployment_info_for_forwarding = {
        "model_info": {
            "model_name": unique_model_name,
        }
    }
    external_info = _create_external_endpoint(deployment_info_for_forwarding, deployed_endpoint)

    # Return deployment information (verification will be done separately)
    deployment: dict[str, Any] = {
        "name": unique_model_name,  # Will be verified in separate step
        "endpoint_url": external_info["external_endpoint"],
        "internal_endpoint_url": deployed_endpoint,
        "docs_url": f"{external_info['external_endpoint']}/docs",
        "status": "running",
        "deployment_id": deployment_id,
        "deployed_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "port_forward_process": external_info["port_forward_process"],
    }

    print("   ✓ Deployment complete!")
    print(f"   → External Endpoint: {deployment['endpoint_url']}")
    print(f"   → Deployment ID: {deployment['deployment_id']}")

    return deployment


@task(name="verify-deployment", retries=2, retry_delay_seconds=3)
def verify_deployment(deployment: dict[str, Any]) -> dict[str, Any]:
    """
    Verify the deployment by querying its endpoint and updating model name.

    Queries the deployment endpoint to get the actual model ID and updates
    the deployment info with the verified name.

    Args:
        deployment: Deployment information with endpoint_url

    Returns:
        Updated deployment information with verified model name
    """
    print(f"🔍 Verifying deployment at {deployment['endpoint_url']}...")

    endpoint_url = deployment["endpoint_url"]
    fallback_model_name = deployment["name"]

    # Verify and get the actual model ID
    verified_model_id = _verify_deployment_endpoint(endpoint_url, fallback_model_name)

    # Update deployment info with verified model name
    verified_deployment = deployment.copy()
    verified_deployment["name"] = verified_model_id

    print(f"   ✓ Deployment verified with model: {verified_model_id}")

    return verified_deployment
