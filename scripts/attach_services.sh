#!/bin/bash

# AWS Credentials - paste your own here
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