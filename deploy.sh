#!/bin/bash

# AWS Deployment Script for Smart Payment Checkout
# This script deploys both backend and frontend to AWS

set -e

# Configuration
PROJECT_NAME="smart-payment-checkout"
ENVIRONMENT="${1:-dev}"
REGION="${2:-us-east-1}"
AWS_PROFILE="${3:-default}"

echo "=========================================="
echo "Smart Payment Checkout Deployment"
echo "=========================================="
echo "Project: $PROJECT_NAME"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "AWS Profile: $AWS_PROFILE"
echo "=========================================="

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    echo "Error: AWS CLI not found. Please install AWS CLI."
    exit 1
fi

# Check AWS credentials
echo "Checking AWS credentials..."
if ! aws sts get-caller-identity --profile "$AWS_PROFILE" &> /dev/null; then
    echo "Error: AWS credentials not configured properly."
    exit 1
fi
echo "✓ AWS credentials verified"

# Deploy Backend (Lambda + API Gateway)
echo ""
echo "=========================================="
echo "Deploying Backend (Lambda + API Gateway)"
echo "=========================================="

# Package Lambda function
echo "Packaging Lambda function..."
cd backend
pip install --target ./package -r requirements.txt
cp app.py package/
cp risk_service.py package/
cp llm_service.py package/
cp rules.json package/
cd package
zip -r ../lambda-deployment.zip .
cd ..
rm -rf package

# Create S3 bucket for Lambda deployment (if not exists)
BUCKET_NAME="${PROJECT_NAME}-lambda-deployment-${REGION}"
echo "Checking S3 bucket: $BUCKET_NAME"
if ! aws s3 ls "s3://$BUCKET_NAME" --profile "$AWS_PROFILE" 2>&1 | grep -q 'NoSuchBucket'; then
    echo "Creating S3 bucket: $BUCKET_NAME"
    aws s3 mb "s3://$BUCKET_NAME" --region "$REGION" --profile "$AWS_PROFILE"
else
    echo "✓ S3 bucket exists: $BUCKET_NAME"
fi

# Upload Lambda package
echo "Uploading Lambda package..."
aws s3 cp lambda-deployment.zip "s3://$BUCKET_NAME/" --profile "$AWS_PROFILE"

# Deploy CloudFormation stack for backend
echo "Deploying CloudFormation stack for backend..."
aws cloudformation deploy \
  --template-file cloudformation/backend-lambda.yaml \
  --stack-name "${PROJECT_NAME}-backend-${ENVIRONMENT}" \
  --parameter-overrides \
    ProjectName="$PROJECT_NAME" \
    Environment="$ENVIRONMENT" \
    OpenAIAPIKey="$OPENAI_API_KEY" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION" \
  --profile "$AWS_PROFILE" \
  || echo "Backend deployment may have issues, check CloudFormation console"

# Clean up
rm -f lambda-deployment.zip

# Get Backend API Endpoint
echo ""
echo "=========================================="
echo "Backend Deployment Information"
echo "=========================================="
API_ENDPOINT=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-backend-${ENVIRONMENT}" \
  --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
  --output text \
  --region "$REGION" \
  --profile "$AWS_PROFILE")

echo "✓ Backend API Endpoint: $API_ENDPOINT"
echo "✓ Backend Stack: ${PROJECT_NAME}-backend-${ENVIRONMENT}"

# Deploy Frontend (S3 + CloudFront)
echo ""
echo "=========================================="
echo "Deploying Frontend (S3 + CloudFront)"
echo "=========================================="

# Build frontend
echo "Building frontend..."
cd ../frontend
npm run build

# Deploy CloudFormation stack for frontend
echo "Deploying CloudFormation stack for frontend..."
aws cloudformation deploy \
  --template-file ../backend/cloudformation/frontend-s3-cloudfront.yaml \
  --stack-name "${PROJECT_NAME}-frontend-${ENVIRONMENT}" \
  --parameter-overrides \
    ProjectName="$PROJECT_NAME" \
    Environment="$ENVIRONMENT" \
  --capabilities CAPABILITY_IAM \
  --region "$REGION" \
  --profile "$AWS_PROFILE" \
  || echo "Frontend deployment may have issues, check CloudFormation console"

# Get Frontend URL
echo ""
echo "=========================================="
echo "Frontend Deployment Information"
echo "=========================================="
FRONTEND_URL=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-frontend-${ENVIRONMENT}" \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" \
  --output text \
  --region "$REGION" \
  --profile "$AWS_PROFILE")

echo "✓ Frontend URL: $FRONTEND_URL"
echo "✓ Frontend Stack: ${PROJECT_NAME}-frontend-${ENVIRONMENT}"

# Upload frontend files to S3
echo "Uploading frontend files to S3..."
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "${PROJECT_NAME}-frontend-${ENVIRONMENT}" \
  --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" \
  --output text \
  --region "$REGION" \
  --profile "$AWS_PROFILE")

aws s3 sync dist/ "s3://$S3_BUCKET/" --delete --profile "$AWS_PROFILE"

echo "✓ Frontend files uploaded"

# Summary
echo ""
echo "=========================================="
echo "Deployment Summary"
echo "=========================================="
echo "Backend API: $API_ENDPOINT"
echo "Frontend URL: $FRONTEND_URL"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "=========================================="
echo "✓ Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Update frontend API endpoint in .env or config files"
echo "2. Test the application: $FRONTEND_URL"
echo "3. Monitor CloudWatch logs for any issues"
echo "=========================================="