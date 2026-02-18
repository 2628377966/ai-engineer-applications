# AWS部署指南 - Smart Payment Checkout

## 🎯 推荐架构

### 后端：Lambda Function URL ✅ (成本优化)
- **为什么选择Lambda Function URL：**
  - 完全免费（替代API Gateway的$3.50/百万调用费用）
  - 更低延迟（直接调用Lambda，无API Gateway中间层）
  - 简单配置（内置CORS和HTTPS支持）
  - 按需付费，成本效益高
  - 自动扩展，无需管理服务器
  - CloudFormation基础设施即代码

### 前端：S3 + CloudFront ✅
- **为什么选择S3 + CloudFront：**
  - **Lambda不适合前端**：
    - Lambda是计算服务，不是文件托管
    - React应用是静态文件（HTML, CSS, JS）
    - 需要持续运行的HTTP服务器
  - **S3 + CloudFront优势：**
    - 全球CDN加速
    - HTTPS免费证书
    - 高可用性（99.99%）
    - 极低成本（存储+流量费用）
    - 自动缓存优化

### DNS：Cloudflare DNS ✅ (成本优化)
- **为什么选择Cloudflare DNS：**
  - 完全免费（替代Route53的$0.50/月费用）
  - 全球DNS网络
  - 内置CDN和DDoS防护
  - 简单易用的管理界面
  - 免费SSL证书

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
│   │   ├── backend-lambda-url.yaml       # 后端Lambda Function URL模板
│   │   ├── backend-lambda.yaml          # 后端Lambda + API Gateway模板（已弃用）
│   │   └── frontend-s3-cloudfront.yaml  # 前端CloudFormation模板
│   └── requirements.txt                # Python依赖
├── frontend/
│   ├── src/                            # React源代码
│   ├── package.json                     # Node.js依赖
│   └── vite.config.js                  # Vite配置
├── deploy-cost-optimized.sh            # Linux/Mac成本优化部署脚本
├── deploy-cost-optimized.ps1           # Windows成本优化部署脚本
├── CLOUDFLARE_DNS_GUIDE.md           # Cloudflare DNS配置指南
├── COST_OPTIMIZED_DEPLOYMENT.md       # 成本优化部署文档
└── AWS_SERVICE_COMPARISON.md         # AWS服务对比分析
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

### 一键部署（成本优化）

#### Windows (PowerShell)
```powershell
# 设置环境变量
$env:OPENAI_API_KEY="your_deepseek_api_key"

# 运行成本优化部署脚本
.\deploy-cost-optimized.ps1 -Environment dev -Region us-east-1 -Profile default
```

#### Linux/Mac
```bash
# 设置环境变量
export OPENAI_API_KEY="your_deepseek_api_key"

# 运行成本优化部署脚本
chmod +x deploy-cost-optimized.sh
./deploy-cost-optimized.sh dev us-east-1 default
```

**参数说明：**
1. 环境: dev | staging | prod
2. 区域: us-east-1 | us-west-2 | eu-west-1
3. AWS配置文件: default | smart-payment

### 步骤2: 配置Cloudflare DNS（可选）

如果你有域名，可以配置Cloudflare DNS：

1. **添加域名到Cloudflare**
   - 登录 https://dash.cloudflare.com/
   - 添加你的域名
   - 更新域名的NS记录

2. **配置前端DNS**
   ```
   类型: CNAME
   名称: app (或 @)
   目标: d1234567890.cloudfront.net
   代理: 已代理 (橙色云朵)
   ```

3. **配置后端DNS**
   ```
   类型: CNAME
   名称: api
   目标: abc123xyz.lambda-url.us-east-1.on.aws
   代理: 仅DNS (灰色云朵)
   ```

详细配置请参考 [CLOUDFLARE_DNS_GUIDE.md](CLOUDFLARE_DNS_GUIDE.md)

### 步骤2（替代方案）：直接使用AWS URL（无域名）

如果你没有域名，可以直接使用AWS提供的公共URL，完全免费！

**优势：**
- ✅ 完全免费（无域名和DNS费用）
- ✅ 无需配置DNS
- ✅ 自动HTTPS
- ✅ 即开即用
- ✅ 全球CDN加速

**部署后会自动获得：**
- 后端URL：`https://abc123xyz.lambda-url.us-east-1.on.aws`
- 前端URL：`https://d1234567890.cloudfront.net`

**更新前端配置：**
```javascript
// frontend/src/config.js 或 .env
const API_BASE_URL = 'https://abc123xyz.lambda-url.us-east-1.on.aws';
```

详细说明请参考 [NO_DOMAIN_DEPLOYMENT.md](NO_DOMAIN_DEPLOYMENT.md)

## 📋 详细部署步骤

### 1. 后端部署（Lambda Function URL）

#### 1.1 准备Lambda函数

```bash
cd backend

# 创建Lambda处理器（如果不存在）
# lambda_handler.py已经创建，包含完整的FastAPI应用
```

#### 1.2 部署CloudFormation栈

```bash
# 使用CloudFormation模板部署（Lambda Function URL）
aws cloudformation deploy \
  --template-file cloudformation/backend-lambda-url.yaml \
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

#### 1.3 获取Lambda Function URL

```bash
# 从CloudFormation输出获取Lambda Function URL
aws cloudformation describe-stacks \
  --stack-name smart-payment-checkout-backend-dev \
  --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionUrl'].OutputValue" \
  --output text \
  --region us-east-1 \
  --profile smart-payment
```

**输出示例：**
```
https://abc123xyz.lambda-url.us-east-1.on.aws
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
const API_BASE_URL = 'https://abc123xyz.lambda-url.us-east-1.on.aws';
```

或者使用Cloudflare DNS配置的域名：
```javascript
// 使用Cloudflare DNS配置的域名
const API_BASE_URL = 'https://api.yourdomain.com';
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

### 后端（Lambda Function URL）

| 服务 | 免费额度 | 预估成本 |
|-----|---------|----------|
| Lambda | 100万请求/月 | $0.20/百万请求 |
| Lambda Function URL | 完全免费 | $0 |
| CloudWatch Logs | 5GB日志存储 | $0.50/GB |

**月成本（中等使用）：** ~$1-5

**成本节省：** 相比API Gateway方案节省$3.50/月

### 前端（S3 + CloudFront）

| 服务 | 免费额度 | 预估成本 |
|-----|---------|----------|
| S3存储 | 5GB | $0.023/GB |
| S3流量 | 1TB/月 | $0.09/GB |
| CloudFront | 1TB流量 | $0.085/GB |

**月成本（中等使用）：** ~$2-10

### DNS服务（可选）

#### 有域名方案

| 服务 | 免费额度 | 预估成本 |
|-----|---------|----------|
| Cloudflare DNS | 完全免费 | $0 |
| Route53 | $0.50/月/zone | $0.50/月 |

**月成本：** $0（使用Cloudflare）

**成本节省：** 相比Route53方案节省$0.50/月

#### 无域名方案（推荐用于测试/开发）

| 服务 | 免费额度 | 预估成本 |
|-----|---------|----------|
| DNS服务 | 完全免费 | $0 |

**月成本：** $0

**优势：**
- ✅ 完全免费
- ✅ 无需配置
- ✅ 即开即用

详细说明请参考 [NO_DOMAIN_DEPLOYMENT.md](NO_DOMAIN_DEPLOYMENT.md)

### 总成本估算

#### 有域名方案
- **开发环境：** ~$3-15/月
- **生产环境：** ~$5-30/月

**成本节省：** 相比原始方案节省$4.00/月（$48.00/年）

#### 无域名方案（推荐用于测试/开发）
- **开发环境：** ~$2-13/月
- **生产环境：** ~$4-28/月

**额外节省：** 相比有域名方案节省$1-2/月（域名费用）

详细成本分析请参考 [COST_OPTIMIZED_DEPLOYMENT.md](COST_OPTIMIZED_DEPLOYMENT.md)

## 🔍 监控和日志

### CloudWatch日志

```bash
# 查看Lambda日志
aws logs tail /aws/lambda/smart-payment-checkout-checkout-dev --follow
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

### 问题：Lambda Function URL无法访问

**解决方案：**
1. 检查Lambda函数状态
2. 验证Function URL配置
3. 检查IAM权限
4. 查看CloudWatch日志

### 问题：CloudFront 403错误

**解决方案：**
1. 检查S3 bucket策略
2. 验证Origin Access Control配置
3. 确认CloudFront分发状态

### 问题：前端无法连接后端

**解决方案：**
1. 检查Lambda Function URL的CORS配置
2. 验证Cloudflare DNS设置
3. 确认Lambda函数权限
4. 检查前端API配置

## 🚀 生产环境最佳实践

### 1. 安全性

- 使用AWS Secrets Manager存储敏感信息
- 启用API Gateway授权
- 配置CloudFront WAF
- 启用S3 bucket加密
- 使用HTTPS only

### 2. 性能优化

- 配置CloudFront缓存策略
- 启用Lambda预留并发（如果需要）
- 使用Cloudflare CDN缓存（可选）
- 优化前端资源压缩
- 启用HTTP/2和HTTP/3

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
- Lambda自动创建执行环境
- 无需管理服务器
- 自动处理并发请求

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