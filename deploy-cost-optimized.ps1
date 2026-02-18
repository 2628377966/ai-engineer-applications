# AWS Deployment Script for Windows (PowerShell) - Cost Optimized
# Uses Lambda Function URL instead of API Gateway

param(
    [Parameter(Mandatory=$false)]
    [string]$Environment = "dev",
    
    [Parameter(Mandatory=$false)]
    [string]$Region = "us-east-1",
    
    [Parameter(Mandatory=$false)]
    [string]$Profile = "default"
)

# Configuration
$ProjectName = "smart-payment-checkout"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "Smart Payment Checkout Deployment" -ForegroundColor Green
Write-Host "(Cost Optimized: Lambda Function URL)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Project: $ProjectName" -ForegroundColor Yellow
Write-Host "Environment: $Environment" -ForegroundColor Yellow
Write-Host "Region: $Region" -ForegroundColor Yellow
Write-Host "AWS Profile: $Profile" -ForegroundColor Yellow
Write-Host "==========================================" -ForegroundColor Green

# Check AWS CLI
Write-Host "`nChecking AWS CLI..." -ForegroundColor Cyan
if (-not (Get-Command aws -ErrorAction SilentlyContinue)) {
    Write-Host "Error: AWS CLI not found. Please install AWS CLI." -ForegroundColor Red
    exit 1
}
Write-Host "✓ AWS CLI found" -ForegroundColor Green

# Check AWS credentials
Write-Host "Checking AWS credentials..." -ForegroundColor Cyan
try {
    $caller = aws sts get-caller-identity --profile $Profile 2>&1 | ConvertFrom-Json
    Write-Host "✓ AWS credentials verified" -ForegroundColor Green
    Write-Host "  Account: $($caller.Account)" -ForegroundColor Gray
    Write-Host "  User: $($caller.Arn)" -ForegroundColor Gray
} catch {
    Write-Host "Error: AWS credentials not configured properly." -ForegroundColor Red
    exit 1
}

# Deploy Backend (Lambda Function URL)
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Deploying Backend (Lambda Function URL)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Package Lambda function
Write-Host "Packaging Lambda function..." -ForegroundColor Cyan
Set-Location backend

# Create package directory
if (Test-Path package) {
    Remove-Item -Recurse -Force package
}
New-Item -ItemType Directory -Path package | Out-Null

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Cyan
uv pip install --target ./package -r requirements.txt

# Copy application files
Write-Host "Copying application files..." -ForegroundColor Cyan
Copy-Item app.py package\
Copy-Item lambda_handler.py package\
Copy-Item lambda_app.py package\
Copy-Item risk_service.py package\
Copy-Item llm_service.py package\
Copy-Item rules.json package\

# Create zip file
Write-Host "Creating Lambda deployment package..." -ForegroundColor Cyan
Set-Location package
Compress-Archive -Path * -DestinationPath ../lambda-deployment.zip -Force
Set-Location ..

# Clean up package directory
Remove-Item -Recurse -Force package

# Create S3 bucket for Lambda code (if not exists)
$BucketName = "${ProjectName}-lambda-code-${Environment}"
Write-Host "Checking S3 bucket: $BucketName" -ForegroundColor Cyan

$bucketExists = aws s3 ls "s3://$BucketName" --profile $Profile 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "Creating S3 bucket: $BucketName" -ForegroundColor Cyan
    aws s3 mb "s3://$BucketName" --region $Region --profile $Profile
} else {
    Write-Host "✓ S3 bucket exists: $BucketName" -ForegroundColor Green
}

# Upload Lambda package
Write-Host "Uploading Lambda package..." -ForegroundColor Cyan
aws s3 cp lambda-deployment.zip "s3://$BucketName/" --profile $Profile

# Deploy CloudFormation stack for backend
Write-Host "Deploying CloudFormation stack for backend..." -ForegroundColor Cyan
$backendStack = "${ProjectName}-backend-${Environment}"

$openaiKey = $env:OPENAI_API_KEY
if ([string]::IsNullOrEmpty($openaiKey)) {
    Write-Host "Warning: OPENAI_API_KEY environment variable not set." -ForegroundColor Yellow
    Write-Host "Please set it before deployment or provide it as parameter." -ForegroundColor Yellow
    $openaiKey = Read-Host "Enter OpenAI API Key"
}

aws cloudformation deploy `
  --template-file cloudformation/backend-lambda-url.yaml `
  --stack-name $backendStack `
  --parameter-overrides `
    ProjectName=$ProjectName `
    Environment=$Environment `
    OpenAIAPIKey=$openaiKey `
  --capabilities CAPABILITY_IAM `
  --region $Region `
  --profile $Profile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Backend deployment may have issues, check CloudFormation console" -ForegroundColor Yellow
} else {
    Write-Host "✓ Backend deployed successfully" -ForegroundColor Green
}

# Clean up
Remove-Item lambda-deployment.zip -Force

# Get Backend Lambda Function URL
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Backend Deployment Information" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$lambdaFunctionUrl = aws cloudformation describe-stacks `
  --stack-name $backendStack `
  --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionUrl'].OutputValue" `
  --output text `
  --region $Region `
  --profile $Profile

Write-Host "✓ Lambda Function URL: $lambdaFunctionUrl" -ForegroundColor Green
Write-Host "✓ Backend Stack: $backendStack" -ForegroundColor Green

# Deploy Frontend (S3 + CloudFront)
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Deploying Frontend (S3 + CloudFront)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Build frontend
Write-Host "Building frontend..." -ForegroundColor Cyan
Set-Location ..\frontend

# Check if node_modules exists
if (-not (Test-Path node_modules)) {
    Write-Host "Installing dependencies..." -ForegroundColor Cyan
    npm install
}

Write-Host "Running build..." -ForegroundColor Cyan
npm run build

# Deploy CloudFormation stack for frontend
Write-Host "Deploying CloudFormation stack for frontend..." -ForegroundColor Cyan
$frontendStack = "${ProjectName}-frontend-${Environment}"

aws cloudformation deploy `
  --template-file ..\backend\cloudformation\frontend-s3-cloudfront.yaml `
  --stack-name $frontendStack `
  --parameter-overrides `
    ProjectName=$ProjectName `
    Environment=$Environment `
  --capabilities CAPABILITY_IAM `
  --region $Region `
  --profile $Profile

if ($LASTEXITCODE -ne 0) {
    Write-Host "Warning: Frontend deployment may have issues, check CloudFormation console" -ForegroundColor Yellow
} else {
    Write-Host "✓ Frontend deployed successfully" -ForegroundColor Green
}

# Get Frontend URL
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Frontend Deployment Information" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

$frontendUrl = aws cloudformation describe-stacks `
  --stack-name $frontendStack `
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" `
  --output text `
  --region $Region `
  --profile $Profile

Write-Host "✓ Frontend URL: $frontendUrl" -ForegroundColor Green
Write-Host "✓ Frontend Stack: $frontendStack" -ForegroundColor Green

# Upload frontend files to S3
Write-Host "Uploading frontend files to S3..." -ForegroundColor Cyan
$s3Bucket = aws cloudformation describe-stacks `
  --stack-name $frontendStack `
  --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" `
  --output text `
  --region $Region `
  --profile $Profile

aws s3 sync dist/ "s3://$s3Bucket/" --delete --profile $Profile

Write-Host "✓ Frontend files uploaded" -ForegroundColor Green

# Summary
Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "Deployment Summary" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host "Backend Lambda Function URL: $lambdaFunctionUrl" -ForegroundColor Yellow
Write-Host "Frontend CloudFront URL: $frontendUrl" -ForegroundColor Yellow
Write-Host "Environment: $Environment" -ForegroundColor Gray
Write-Host "Region: $Region" -ForegroundColor Gray
Write-Host "==========================================" -ForegroundColor Green
Write-Host "✓ Deployment completed successfully!" -ForegroundColor Green
Write-Host "`nNext steps:" -ForegroundColor Cyan
Write-Host "1. Configure Cloudflare DNS (see CLOUDFLARE_DNS_GUIDE.md)" -ForegroundColor White
Write-Host "   - Frontend: app.yourdomain.com -> $frontendUrl" -ForegroundColor White
Write-Host "   - Backend: api.yourdomain.com -> $lambdaFunctionUrl" -ForegroundColor White
Write-Host "2. Update frontend API endpoint in .env or config files" -ForegroundColor White
Write-Host "3. Test the application" -ForegroundColor White
Write-Host "4. Monitor CloudWatch logs for any issues" -ForegroundColor White
Write-Host "`nCost Optimization:" -ForegroundColor Green
Write-Host "- Using Lambda Function URL instead of API Gateway" -ForegroundColor Green
Write-Host "- Using Cloudflare DNS instead of Route53" -ForegroundColor Green
Write-Host "- Estimated savings: ~$3.50/month (API Gateway) + $0.50/month (Route53)" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green

# Save deployment info to file
$deploymentInfo = @"
# Smart Payment Checkout Deployment Info
Date: $(Get-Date)
Environment: $Environment
Region: $Region

## Backend
- Lambda Function URL: $lambdaFunctionUrl
- Stack Name: $backendStack

## Frontend
- CloudFront URL: $frontendUrl
- S3 Bucket: $s3Bucket
- Stack Name: $frontendStack

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
3. Test the application
4. Monitor CloudWatch logs
"@

$deploymentInfo | Out-File -FilePath ".\deployment-info.txt" -Encoding UTF8
Write-Host "`n✓ Deployment info saved to deployment-info.txt" -ForegroundColor Green

# Return to original directory
Set-Location ..