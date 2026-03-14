#!/usr/bin/env bash
# Deploy to AWS ECS Fargate
# Prerequisites:
#   - AWS CLI configured with appropriate permissions
#   - ECR repository created
#   - ECS cluster created
#   - RDS PostgreSQL instance running
#   - Secrets stored in AWS Secrets Manager

set -euo pipefail

# --- Configuration (edit these) ---
AWS_REGION="${AWS_REGION:-us-east-1}"
AWS_ACCOUNT_ID="${AWS_ACCOUNT_ID:-$(aws sts get-caller-identity --query Account --output text)}"
ECR_REPO="mortgage-underwriting"
ECS_CLUSTER="mortgage-underwriting-cluster"
ECS_SERVICE="mortgage-underwriting-service"
IMAGE_TAG="${IMAGE_TAG:-latest}"

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
PROJECT_DIR="$(dirname "$(dirname "$SCRIPT_DIR")")"

cd "$PROJECT_DIR"

ECR_URI="${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com/${ECR_REPO}"

echo "=== Step 1: Authenticate with ECR ==="
aws ecr get-login-password --region "$AWS_REGION" | \
    docker login --username AWS --password-stdin "${AWS_ACCOUNT_ID}.dkr.ecr.${AWS_REGION}.amazonaws.com"

echo "=== Step 2: Build Docker image ==="
docker build -t "${ECR_REPO}:${IMAGE_TAG}" .

echo "=== Step 3: Tag and push to ECR ==="
docker tag "${ECR_REPO}:${IMAGE_TAG}" "${ECR_URI}:${IMAGE_TAG}"
docker push "${ECR_URI}:${IMAGE_TAG}"

echo "=== Step 4: Update ECS service ==="
aws ecs update-service \
    --cluster "$ECS_CLUSTER" \
    --service "$ECS_SERVICE" \
    --force-new-deployment \
    --region "$AWS_REGION"

echo ""
echo "=== Deployment initiated ==="
echo "Image: ${ECR_URI}:${IMAGE_TAG}"
echo "Monitor: aws ecs describe-services --cluster $ECS_CLUSTER --services $ECS_SERVICE --region $AWS_REGION"
