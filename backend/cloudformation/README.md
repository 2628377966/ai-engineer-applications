# AWS部署文件说明

本目录包含Smart Payment Checkout项目的AWS部署配置文件和脚本。

## 📁 文件结构

```
backend/cloudformation/
├── backend-lambda.yaml           # 后端Lambda + API Gateway CloudFormation模板
├── frontend-s3-cloudfront.yaml  # 前端S3 + CloudFront CloudFormation模板
└── README.md                    # 本文件
```

## 📋 CloudFormation模板说明

### backend-lambda.yaml

**用途：** 部署后端API服务到AWS Lambda

**创建的资源：**
- Lambda函数（Python 3.11运行时）
- API Gateway REST API
- IAM角色和策略
- CloudWatch日志组

**参数：**
- `ProjectName`: 项目名称（默认：smart-payment-checkout）
- `Environment`: 部署环境（dev/staging/prod）
- `OpenAIAPIKey`: OpenAI API密钥（加密存储）
- `OpenAIBaseURL`: OpenAI API基础URL（默认：https://api.deepseek.com）
- `OpenAIModel`: OpenAI模型名称（默认：deepseek-chat）

**输出：**
- `ApiEndpoint`: API Gateway端点URL
- `LambdaFunctionArn`: Lambda函数ARN
- `LambdaFunctionName`: Lambda函数名称

**使用示例：**
```bash
aws cloudformation deploy \
  --template-file backend-lambda.yaml \
  --stack-name smart-payment-backend-dev \
  --parameter-overrides \
    ProjectName=smart-payment-checkout \
    Environment=dev \
    OpenAIAPIKey=$OPENAI_API_KEY \
  --capabilities CAPABILITY_IAM
```

### frontend-s3-cloudfront.yaml

**用途：** 部署前端React应用到S3和CloudFront

**创建的资源：**
- S3存储桶（静态文件托管）
- CloudFront分发（CDN）
- CloudFront Origin Access Control
- S3存储桶策略
- Route53记录集（可选，自定义域名）

**参数：**
- `ProjectName`: 项目名称（默认：smart-payment-checkout）
- `Environment`: 部署环境（dev/staging/prod）
- `DomainName`: 自定义域名（可选）

**输出：**
- `WebsiteURL`: S3网站URL
- `CloudFrontURL`: CloudFront分发URL
- `DistributionID`: CloudFront分发ID
- `BucketName`: S3存储桶名称

**使用示例：**
```bash
aws cloudformation deploy \
  --template-file frontend-s3-cloudfront.yaml \
  --stack-name smart-payment-frontend-dev \
  --parameter-overrides \
    ProjectName=smart-payment-checkout \
    Environment=dev \
  --capabilities CAPABILITY_IAM
```

## 🚀 快速部署

### 使用部署脚本（推荐）

#### Linux/Mac
```bash
# 设置环境变量
export OPENAI_API_KEY="your_api_key_here"

# 运行部署脚本
./deploy.sh dev us-east-1 default
```

#### Windows (PowerShell)
```powershell
# 设置环境变量
$env:OPENAI_API_KEY="your_api_key_here"

# 运行部署脚本
.\deploy.ps1 -Environment dev -Region us-east-1 -Profile default
```

### 手动部署

#### 1. 部署后端

```bash
# 创建Lambda部署包
cd backend
pip install --target ./package -r requirements.txt
cp app.py package/
cp lambda_handler.py package/
cp risk_service.py package/
cp llm_service.py package/
cp rules.json package/
cd package
zip -r ../lambda-deployment.zip .
cd ..
rm -rf package

# 上传到S3
aws s3 cp lambda-deployment.zip s3://your-bucket/

# 部署CloudFormation栈
aws cloudformation deploy \
  --template-file cloudformation/backend-lambda.yaml \
  --stack-name smart-payment-backend-dev \
  --parameter-overrides \
    ProjectName=smart-payment-checkout \
    Environment=dev \
    OpenAIAPIKey=$OPENAI_API_KEY \
  --capabilities CAPABILITY_IAM
```

#### 2. 部署前端

```bash
# 构建前端
cd frontend
npm install
npm run build

# 部署CloudFormation栈
aws cloudformation deploy \
  --template-file ../backend/cloudformation/frontend-s3-cloudfront.yaml \
  --stack-name smart-payment-frontend-dev \
  --parameter-overrides \
    ProjectName=smart-payment-checkout \
    Environment=dev \
  --capabilities CAPABILITY_IAM

# 获取S3 bucket名称
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name smart-payment-frontend-dev \
  --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" \
  --output text)

# 上传文件到S3
aws s3 sync dist/ s3://$S3_BUCKET/ --delete
```

## 🔧 配置说明

### 环境变量

Lambda函数会自动配置以下环境变量：

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
ENVIRONMENT=dev
```

### 前端API配置

构建前端前，需要配置API端点：

```javascript
// frontend/src/config.js
export const API_BASE_URL = 'https://your-api-gateway-url.execute-api.region.amazonaws.com/dev';
```

或在 `.env` 文件中：

```bash
VITE_API_BASE_URL=https://your-api-gateway-url.execute-api.region.amazonaws.com/dev
```

## 📊 成本估算

### 后端（Lambda + API Gateway）

| 服务 | 免费额度 | 预估成本 |
|-----|---------|----------|
| Lambda | 100万请求/月 | $0.20/百万请求 |
| API Gateway | 100万API调用/月 | $3.50/百万调用 |
| CloudWatch Logs | 5GB日志存储 | $0.50/GB |

**月成本（中等使用）：** ~$5-15

### 前端（S3 + CloudFront）

| 服务 | 免费额度 | 预估成本 |
|-----|---------|----------|
| S3存储 | 5GB | $0.023/GB |
| S3流量 | 1TB/月 | $0.09/GB |
| CloudFront | 1TB流量 | $0.085/GB |

**月成本（中等使用）：** ~$2-10

### 总成本估算

- **开发环境：** ~$10-25/月
- **生产环境：** ~$20-50/月

## 🔍 监控和日志

### 查看Lambda日志

```bash
# 实时查看日志
aws logs tail /aws/lambda/smart-payment-checkout-checkout-dev --follow

# 查看特定时间段的日志
aws logs filter-log-events \
  --log-group-name /aws/lambda/smart-payment-checkout-checkout-dev \
  --start-time 1679080800000
```

### 查看API Gateway日志

```bash
aws logs tail API-Gateway-Execution-Logs_smart-payment-checkout_dev --follow
```

### CloudWatch指标

```bash
# 查看Lambda调用次数
aws cloudwatch get-metric-statistics \
  --namespace AWS/Lambda \
  --metric-name Invocations \
  --dimensions Name=FunctionName,Value=smart-payment-checkout-checkout-dev \
  --start-time 2026-02-15T00:00:00Z \
  --end-time 2026-02-15T23:59:59Z \
  --period 3600 \
  --statistics Sum
```

## 🛠️ 故障排查

### 问题：Lambda函数超时

**症状：** API Gateway返回504错误

**解决方案：**
1. 增加Lambda超时时间（在CloudFormation模板中修改`Timeout`参数）
2. 优化代码性能
3. 检查外部API调用延迟
4. 增加Lambda内存大小

### 问题：API Gateway 502错误

**症状：** API Gateway返回502 Bad Gateway

**解决方案：**
1. 检查Lambda函数是否正常
2. 验证API Gateway配置
3. 查看CloudWatch日志
4. 检查Lambda函数权限

### 问题：CloudFront 403错误

**症状：** 访问前端URL时返回403 Forbidden

**解决方案：**
1. 检查S3 bucket策略
2. 验证Origin Access Control配置
3. 确认CloudFront分发状态
4. 检查文件是否正确上传到S3

### 问题：前端无法连接后端

**症状：** 前端API调用失败

**解决方案：**
1. 检查CORS配置
2. 验证API端点URL
3. 确认Lambda函数权限
4. 查看浏览器控制台错误

## 🔄 更新部署

### 更新后端

```bash
# 重新打包Lambda函数
cd backend
pip install --target ./package -r requirements.txt
cp *.py package/
cp rules.json package/
cd package
zip -r ../lambda-deployment.zip .
cd ..
rm -rf package

# 更新Lambda函数代码
aws lambda update-function-code \
  --function-name smart-payment-checkout-checkout-dev \
  --zip-file fileb://lambda-deployment.zip
```

### 更新前端

```bash
# 重新构建
cd frontend
npm run build

# 同步到S3
aws s3 sync dist/ s3://your-bucket/ --delete

# 使CloudFront缓存失效（可选）
aws cloudfront create-invalidation \
  --distribution-id YOUR_DISTRIBUTION_ID \
  --paths "/*"
```

## 🚀 生产环境最佳实践

### 安全性

- ✅ 使用AWS Secrets Manager存储敏感信息
- ✅ 启用API Gateway授权
- ✅ 配置CloudFront WAF
- ✅ 启用S3 bucket加密
- ✅ 使用HTTPS only
- ✅ 配置IAM最小权限原则

### 性能优化

- ✅ 配置CloudFront缓存策略
- ✅ 启用Lambda预留并发
- ✅ 使用API Gateway缓存
- ✅ 优化前端资源压缩
- ✅ 启用HTTP/2和HTTP/3

### 可靠性

- ✅ 配置多区域部署
- ✅ 设置健康检查
- ✅ 配置自动扩展
- ✅ 启用版本控制
- ✅ 配置备份策略

### 监控和告警

- ✅ 设置CloudWatch告警
- ✅ 配置错误率监控
- ✅ 设置延迟监控
- ✅ 配置成本告警
- ✅ 设置安全告警

## 📚 相关文档

- [AWS部署指南](../../AWS_DEPLOYMENT_GUIDE.md)
- [AWS服务对比](../../AWS_SERVICE_COMPARISON.md)
- [CloudFormation文档](https://docs.aws.amazon.com/cloudformation/)
- [Lambda文档](https://docs.aws.amazon.com/lambda/)
- [API Gateway文档](https://docs.aws.amazon.com/apigateway/)
- [S3文档](https://docs.aws.amazon.com/s3/)
- [CloudFront文档](https://docs.aws.amazon.com/cloudfront/)

## 🤝 贡献

欢迎改进CloudFormation模板和部署脚本！

## 📄 许可证

MIT License