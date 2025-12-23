#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
ENV_FILE="$PROJECT_ROOT/.env"

# Port configuration - change these to use different local ports
MODEL_CATALOG_PORT=9090
QWEN_LLM_PORT=7070
DEPLOYER_PORT=8080
POSTGRES_PORT=5432

# Load AWS credentials from .env file if it exists
if [[ -f "$ENV_FILE" ]]; then
    echo "Loading AWS credentials from .env file..."
    # Source the .env file to load AWS credentials
    set -a  # automatically export all variables
    source "$ENV_FILE"
    set +a  # disable auto-export
else
    echo "Warning: .env file not found at $ENV_FILE"
    echo "Please create a .env file with AWS credentials or set them in your environment"
fi

echo "Forwarding AWS services to localhost..."
echo "  Model Catalog Service:  localhost:${MODEL_CATALOG_PORT}"
echo "  Qwen LLM Predictor:     localhost:${QWEN_LLM_PORT}"
echo "  MisaLabs Deployer:      localhost:${DEPLOYER_PORT}"
echo "  PostgreSQL:             localhost:${POSTGRES_PORT}"
echo ""
echo "Press Ctrl+C to stop"
echo ""

kubectl port-forward svc/model-catalog-service ${MODEL_CATALOG_PORT}:80 -n staging &
kubectl port-forward svc/qwen-llm-predictor ${QWEN_LLM_PORT}:80 -n staging &
kubectl port-forward svc/misalabs-deployer-service -n staging ${DEPLOYER_PORT}:80 &
kubectl port-forward svc/platform-postgres-postgresql-primary ${POSTGRES_PORT}:5432 -n postgres &

wait