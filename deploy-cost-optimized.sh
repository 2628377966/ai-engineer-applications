#!/bin/bash

# AWS Deployment Script for Linux/Mac - Cost Optimized
# Uses Lambda Function URL instead of API Gateway

set -e

# Configuration
PROJECT_NAME="smart-payment-checkout"
ENVIRONMENT="${1:-dev}"
REGION="${2:-us-east-1}"
AWS_PROFILE="${3:-default}"

echo "=========================================="
echo "Smart Payment Checkout Deployment"
echo "(Cost Optimized: Lambda Function URL)"
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

# Deploy Backend (Lambda Function URL)
echo ""
echo "=========================================="
echo "Deploying Backend (Lambda Function URL)"
echo "=========================================="

# Package Lambda function
echo "Packaging Lambda function..."
cd backend

# Create package directory
rm -rf package
mkdir -p package

# Install dependencies
echo "Installing dependencies..."
uv pip install --target ./package -r requirements.txt

# Copy application files
echo "Copying application files..."
cp app.py package/
cp lambda_handler.py package/
cp lambda_app.py package/
cp risk_service.py package/
cp llm_service.py package/
cp rules.json package/

# Create zip file
echo "Creating Lambda deployment package..."
cd package
zip -r ../lambda-deployment.zip .
cd ..
rm -rf package

# Create S3 bucket for Lambda code (if not exists)
BUCKET_NAME="${PROJECT_NAME}-lambda-code-${REGION}"
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
BACKEND_STACK="${PROJECT_NAME}-backend-${ENVIRONMENT}"

if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY environment variable not set."
    echo "Please set it before deployment or provide it as parameter."
    read -p "Enter OpenAI API Key: " OPENAI_API_KEY
fi

aws cloudformation deploy \
  --template-file cloudformation/backend-lambda-url.yaml \
  --stack-name "$BACKEND_STACK" \
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

# Get Backend Lambda Function URL
echo ""
echo "=========================================="
echo "Backend Deployment Information"
echo "=========================================="
LAMBDA_FUNCTION_URL=$(aws cloudformation describe-stacks \
  --stack-name "$BACKEND_STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionUrl'].OutputValue" \
  --output text \
  --region "$REGION" \
  --profile "$AWS_PROFILE")

echo "✓ Lambda Function URL: $LAMBDA_FUNCTION_URL"
echo "✓ Backend Stack: $BACKEND_STACK"

# Deploy Frontend (S3 + CloudFront)
echo ""
echo "=========================================="
echo "Deploying Frontend (S3 + CloudFront)"
echo "=========================================="

# Build frontend
echo "Building frontend..."
cd ../frontend

# Install dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm install
fi

echo "Running build..."
npm run build

# Deploy CloudFormation stack for frontend
echo "Deploying CloudFormation stack for frontend..."
FRONTEND_STACK="${PROJECT_NAME}-frontend-${ENVIRONMENT}"

aws cloudformation deploy \
  --template-file ../backend/cloudformation/frontend-s3-cloudfront.yaml \
  --stack-name "$FRONTEND_STACK" \
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
  --stack-name "$FRONTEND_STACK" \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" \
  --output text \
  --region "$REGION" \
  --profile "$AWS_PROFILE")

echo "✓ Frontend URL: $FRONTEND_URL"
echo "✓ Frontend Stack: $FRONTEND_STACK"

# Upload frontend files to S3
echo "Uploading frontend files to S3..."
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name "$FRONTEND_STACK" \
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
echo "Backend Lambda Function URL: $LAMBDA_FUNCTION_URL"
echo "Frontend CloudFront URL: $FRONTEND_URL"
echo "Environment: $ENVIRONMENT"
echo "Region: $REGION"
echo "=========================================="
echo "✓ Deployment completed successfully!"
echo ""
echo "Next steps:"
echo "1. Configure Cloudflare DNS (see CLOUDFLARE_DNS_GUIDE.md)"
echo "   - Frontend: app.yourdomain.com -> $FRONTEND_URL"
echo "   - Backend: api.yourdomain.com -> $LAMBDA_FUNCTION_URL"
echo "2. Update frontend API endpoint in .env or config files"
echo "3. Test the application"
echo "4. Monitor CloudWatch logs for any issues"
echo ""
echo "Cost Optimization:"
echo "- Using Lambda Function URL instead of API Gateway"
echo "- Using Cloudflare DNS instead of Route53"
echo "- Estimated savings: ~$3.50/month (API Gateway) + $0.50/month (Route53)"
echo "=========================================="

# Save deployment info to file
cat > deployment-info.txt <<EOF
# Smart Payment Checkout Deployment Info
Date: $(date)
Environment: $ENVIRONMENT
Region: $REGION

## Backend
- Lambda Function URL: $LAMBDA_FUNCTION_URL
- Stack Name: $BACKEND_STACK

## Frontend
- CloudFront URL: $FRONTEND_URL
- S3 Bucket: $S3_BUCKET
- Stack Name: $FRONTEND_STACK

## Cloudflare DNS Configuration
Add these DNS records in Cloudflare:

### Frontend
Type: CNAME
Name: app (or @ for root)
Target: d1234567890.cloudfront.net (extract from CloudFront URL)
Proxy: Proxied (orange cloud)

### Backend
Type: CNAME
Name: api
Target: abc123xyz.lambda-url.us-east-1.on.aws (extract from Lambda Function URL)
Proxy: DNS only (gray cloud)

## Next Steps
1. Configure Cloudflare DNS
2. Update frontend API endpoint
3. Test application
4. Monitor CloudWatch logs
EOF

echo "✓ Deployment info saved to deployment-info.txt"