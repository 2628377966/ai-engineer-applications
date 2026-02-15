# AWS部署指南 - Smart Payment Checkout

## 🎯 推荐架构

### 后端：Lambda + API Gateway ✅
- **为什么选择Lambda：**
  - API服务完美适合serverless架构
  - 按需付费，成本效益高
  - 自动扩展，无需管理服务器
  - CloudFormation基础设施即代码

### 前端：S3 + CloudFront ✅
- **为什么选择S3 + CloudFront：**
  - **Lambda不适合前端**：
    - Lambda是计算服务，不是文件托管
    - React应用是静态文件（HTML, CSS, JS）
    - 需要持续运行的HTTP服务器
  - **S3 + CloudFront优势**：
    - 全球CDN加速
    - HTTPS免费证书
    - 高可用性（99.99%）
    - 极低成本（存储+流量费用）
    - 自动缓存优化

## 📁 项目结构

```
ai-engineer-applications/
├── backend/
│   ├── app.py                          # FastAPI应用
│   ├── lambda_handler.py                # Lambda处理器
│   ├── risk_service.py                  # 风险服务
│   ├── llm_service.py                   # LLM服务
│   ├── rules.json                       # 风险规则
│   ├── cloudformation/
│   │   ├── backend-lambda.yaml           # 后端CloudFormation模板
│   │   └── frontend-s3-cloudfront.yaml  # 前端CloudFormation模板
│   └── requirements.txt                # Python依赖
├── frontend/
│   ├── src/                            # React源代码
│   ├── package.json                     # Node.js依赖
│   └── vite.config.js                  # Vite配置
└── deploy.sh                          # 部署脚本
```

## 🚀 快速部署

### 前置要求

1. **安装AWS CLI**
```bash
# Windows (使用PowerShell)
Invoke-WebRequest -Uri "https://awscli.amazonaws.com/awscli-exe-windows.zip" -OutFile "awsclizip"
Expand-Archive -LiteralPath "awsclizip" -DestinationPath "."
```

2. **配置AWS凭证**
```bash
aws configure --profile smart-payment
# 输入你的AWS Access Key ID和Secret Access Key
# 默认区域: us-east-1
# 默认输出格式: json
```

3. **设置环境变量**
```bash
export OPENAI_API_KEY="your_deepseek_api_key"
```

### 一键部署

```bash
# 使用部署脚本
./deploy.sh dev us-east-1 smart-payment

# 参数说明：
# 1. 环境: dev | staging | prod
# 2. 区域: us-east-1 | us-west-2 | eu-west-1
# 3. AWS配置文件: default | smart-payment
```

## 📋 详细部署步骤

### 1. 后端部署（Lambda + API Gateway）

#### 1.1 准备Lambda函数

```bash
cd backend

# 创建Lambda处理器（如果不存在）
# lambda_handler.py已经创建，包含完整的FastAPI应用
```

#### 1.2 部署CloudFormation栈

```bash
# 使用CloudFormation模板部署
aws cloudformation deploy \
  --template-file cloudformation/backend-lambda.yaml \
  --stack-name smart-payment-checkout-backend-dev \
  --parameter-overrides \
    ProjectName=smart-payment-checkout \
    Environment=dev \
    OpenAIAPIKey=$OPENAI_API_KEY \
    OpenAIBaseURL=https://api.deepseek.com \
    OpenAIModel=deepseek-chat \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --profile smart-payment
```

#### 1.3 获取API端点

```bash
# 从CloudFormation输出获取API URL
aws cloudformation describe-stacks \
  --stack-name smart-payment-checkout-backend-dev \
  --query "Stacks[0].Outputs[?OutputKey=='ApiEndpoint'].OutputValue" \
  --output text \
  --region us-east-1 \
  --profile smart-payment
```

**输出示例：**
```
https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev
```

### 2. 前端部署（S3 + CloudFront）

#### 2.1 构建前端

```bash
cd frontend

# 安装依赖
npm install

# 构建生产版本
npm run build
```

#### 2.2 部署CloudFormation栈

```bash
# 创建S3 + CloudFront基础设施
aws cloudformation deploy \
  --template-file ../backend/cloudformation/frontend-s3-cloudfront.yaml \
  --stack-name smart-payment-checkout-frontend-dev \
  --parameter-overrides \
    ProjectName=smart-payment-checkout \
    Environment=dev \
  --capabilities CAPABILITY_IAM \
  --region us-east-1 \
  --profile smart-payment
```

#### 2.3 上传前端文件

```bash
# 获取S3 bucket名称
S3_BUCKET=$(aws cloudformation describe-stacks \
  --stack-name smart-payment-checkout-frontend-dev \
  --query "Stacks[0].Outputs[?OutputKey=='BucketName'].OutputValue" \
  --output text \
  --region us-east-1 \
  --profile smart-payment)

# 上传构建文件到S3
aws s3 sync dist/ "s3://$S3_BUCKET/" --delete --profile smart-payment
```

#### 2.4 获取前端URL

```bash
# 从CloudFormation输出获取CloudFront URL
aws cloudformation describe-stacks \
  --stack-name smart-payment-checkout-frontend-dev \
  --query "Stacks[0].Outputs[?OutputKey=='CloudFrontURL'].OutputValue" \
  --output text \
  --region us-east-1 \
  --profile smart-payment
```

**输出示例：**
```
https://d1234567890.cloudfront.net
```

#### 2.5 更新前端API配置

```javascript
// frontend/src/config.js 或 .env
const API_BASE_URL = 'https://abc123xyz.execute-api.us-east-1.amazonaws.com/dev';
```

## 🔧 配置说明

### CloudFormation参数

#### 后端参数
| 参数 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| ProjectName | String | smart-payment-checkout | 项目名称 |
| Environment | String | dev | 部署环境 |
| OpenAIAPIKey | String | - | OpenAI API密钥（加密） |
| OpenAIBaseURL | String | https://api.deepseek.com | API基础URL |
| OpenAIModel | String | deepseek-chat | 模型名称 |

#### 前端参数
| 参数 | 类型 | 默认值 | 描述 |
|-----|------|--------|------|
| ProjectName | String | smart-payment-checkout | 项目名称 |
| Environment | String | dev | 部署环境 |
| DomainName | String | '' | 自定义域名（可选） |

### 环境变量

Lambda函数会自动配置以下环境变量：

```bash
OPENAI_API_KEY=your_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
ENVIRONMENT=dev
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

### CloudWatch日志

```bash
# 查看Lambda日志
aws logs tail /aws/lambda/smart-payment-checkout-checkout-dev --follow

# 查看API Gateway日志
aws logs tail /aws/apigateway/smart-payment-checkout-api-dev --follow
```

### CloudWatch指标

```bash
# 查看Lambda指标
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

**解决方案：**
1. 增加Lambda超时时间（在CloudFormation模板中）
2. 优化代码性能
3. 检查外部API调用延迟

### 问题：API Gateway 502错误

**解决方案：**
1. 检查Lambda函数是否正常
2. 验证API Gateway配置
3. 查看CloudWatch日志

### 问题：CloudFront 403错误

**解决方案：**
1. 检查S3 bucket策略
2. 验证Origin Access Control配置
3. 确认CloudFront分发状态

### 问题：前端无法连接后端

**解决方案：**
1. 检查CORS配置
2. 验证API端点URL
3. 确认Lambda函数权限

## 🚀 生产环境最佳实践

### 1. 安全性

- 使用AWS Secrets Manager存储敏感信息
- 启用API Gateway授权
- 配置CloudFront WAF
- 启用S3 bucket加密
- 使用HTTPS only

### 2. 性能优化

- 配置CloudFront缓存策略
- 启用Lambda预留并发
- 使用API Gateway缓存
- 优化前端资源压缩

### 3. 可靠性

- 配置多区域部署
- 设置健康检查
- 配置自动扩展
- 启用版本控制

### 4. 监控和告警

- 设置CloudWatch告警
- 配置错误率监控
- 设置延迟监控
- 配置成本告警

## 📈 扩展性

### 水平扩展

Lambda自动扩展，无需配置：
- API Gateway自动处理并发请求
- Lambda自动创建执行环境
- 无需管理服务器

### 垂直扩展

在CloudFormation模板中调整：
- Lambda内存大小（128MB - 10GB）
- Lambda超时时间（1-900秒）
- API Gateway限制

## 🔄 CI/CD集成

### GitHub Actions示例

```yaml
name: Deploy to AWS

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      
      - name: Configure AWS credentials
        uses: aws-actions/configure-aws-credentials@v1
        with:
          aws-access-key-id: ${{ secrets.AWS_ACCESS_KEY_ID }}
          aws-secret-access-key: ${{ secrets.AWS_SECRET_ACCESS_KEY }}
          aws-region: us-east-1
      
      - name: Deploy backend
        run: |
          aws cloudformation deploy \
            --template-file backend/cloudformation/backend-lambda.yaml \
            --stack-name smart-payment-backend-prod \
            --parameter-overrides \
              ProjectName=smart-payment \
              Environment=prod \
              OpenAIAPIKey=${{ secrets.OPENAI_API_KEY }}
      
      - name: Deploy frontend
        run: |
          cd frontend
          npm install
          npm run build
          aws s3 sync dist/ s3://smart-payment-frontend-prod/ --delete
```

## 📚 相关资源

- [AWS Lambda文档](https://docs.aws.amazon.com/lambda/)
- [API Gateway文档](https://docs.aws.amazon.com/apigateway/)
- [S3文档](https://docs.aws.amazon.com/s3/)
- [CloudFront文档](https://docs.aws.amazon.com/cloudfront/)
- [CloudFormation文档](https://docs.aws.amazon.com/cloudformation/)

## 🤝 贡献

欢迎改进部署脚本和文档！

## 📄 许可证

MIT License

---

**注意：** 本指南基于AWS最佳实践，实际部署时请根据具体需求调整配置。