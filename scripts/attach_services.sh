#!/bin/bash

# AWS credentials
# WARNING: Do NOT paste real AWS credentials into this script or commit them to source control.
# Prefer sourcing credentials from your environment, a .env file, or AWS CLI configuration (aws configure).
# The values below are placeholders and should be overridden by your environment as needed.
export AWS_ACCESS_KEY_ID="AWS_ACCESS_KEY_ID"
export AWS_SECRET_ACCESS_KEY="AWS_SECRET_ACCESS_KEY"
export AWS_SESSION_TOKEN="AWS_SESSION_TOKEN"

echo "Forwarding AWS services to localhost..."
echo "Model Catalog Service: localhost:9090"
echo "PostgreSQL: localhost:5432"
echo ""
echo "Press Ctrl+C to stop"
echo ""

kubectl port-forward svc/model-catalog-service 9090:80 -n staging &
#kubectl port-forward svc/platform-postgres-postgresql-primary 5432:5432 -n postgres &

wait