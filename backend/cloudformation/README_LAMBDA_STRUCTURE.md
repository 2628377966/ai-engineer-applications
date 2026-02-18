# Lambda Function URL Deployment - 文件结构说明

## 📁 文件组织

### 核心文件

```
backend/
├── lambda_app.py                    # Lambda应用主文件（新）
├── lambda_handler.py                # Lambda处理器（保留用于其他用途）
├── app.py                          # FastAPI应用（本地开发）
├── risk_service.py                  # 风险评估服务
├── llm_service.py                   # LLM分析服务
├── rules.json                       # 风险规则配置
├── requirements.txt                # Python依赖
└── cloudformation/
    └── backend-lambda-url.yaml       # CloudFormation模板（已更新）
```

## 🔧 文件说明

### lambda_app.py
**用途：** Lambda Function URL的FastAPI应用

**特点：**
- 包含完整的FastAPI应用
- 使用Mangum适配器
- 包含所有API端点（/health, /checkout, /3ds-verify）
- 包含支付处理逻辑
- 包含3DS验证逻辑

**为什么单独文件：**
- CloudFormation模板更简洁
- 代码更容易维护和测试
- 可以独立开发和测试
- 便于版本控制

### lambda_handler.py
**用途：** 通用Lambda处理器（保留用于其他用途）

**特点：**
- 简化的Lambda处理器
- 用于其他Lambda函数
- 保留向后兼容性

### app.py
**用途：** 本地开发的FastAPI应用

**特点：**
- 用于本地开发
- 使用uvicorn服务器
- 与lambda_app.py功能相同
- 便于本地测试

## 🚀 部署流程

### 1. 打包Lambda函数

部署脚本会自动完成以下步骤：

```bash
# 1. 创建package目录
mkdir package

# 2. 安装依赖
# 使用uv安装依赖（推荐）
uv pip install --target ./package -r requirements.txt

# 3. 复制所有必要的文件
cp lambda_app.py package/
cp risk_service.py package/
cp llm_service.py package/
cp rules.json package/

# 4. 创建zip包
cd package
zip -r ../lambda-deployment.zip .
```

### 2. 上传到S3

```bash
aws s3 cp lambda-deployment.zip s3://bucket-name/
```

### 3. 部署CloudFormation栈

```bash
aws cloudformation deploy \
  --template-file cloudformation/backend-lambda-url.yaml \
  --stack-name smart-payment-checkout-backend-dev \
  --parameter-overrides \
    ProjectName=smart-payment-checkout \
    Environment=dev \
    OpenAIAPIKey=$OPENAI_API_KEY
```

### 4. Lambda函数配置

CloudFormation模板会配置Lambda函数：

```yaml
PaymentCheckoutFunction:
  Type: AWS::Lambda::Function
  Properties:
    FunctionName: smart-payment-checkout-checkout-dev
    Runtime: python3.11
    Handler: lambda_app.lambda_handler  # 使用lambda_app.py中的lambda_handler
    Code:
      S3Bucket: lambda-code-bucket
      S3Key: lambda-deployment.zip
```

## 🔄 开发流程

### 本地开发

1. **修改代码**
   ```bash
   # 编辑app.py或lambda_app.py
   vim lambda_app.py
   ```

2. **本地测试**
   ```bash
   # 使用uvicorn运行
   uvicorn lambda_app:app --reload
   ```

3. **测试API**
   ```bash
   curl http://localhost:8000/health
   ```

### 部署到AWS

1. **运行部署脚本**
   ```bash
   ./deploy-cost-optimized.sh dev us-east-1 default
   ```

2. **验证部署**
   ```bash
   # 获取Lambda Function URL
   aws cloudformation describe-stacks \
     --stack-name smart-payment-checkout-backend-dev \
     --query "Stacks[0].Outputs[?OutputKey=='LambdaFunctionUrl'].OutputValue" \
     --output text
   ```

3. **测试部署**
   ```bash
   curl https://abc123xyz.lambda-url.us-east-1.on.aws/health
   ```

## 📋 CloudFormation模板变化

### 之前（内联代码）

```yaml
PaymentCheckoutFunction:
  Type: AWS::Lambda::Function
  Properties:
    Handler: lambda_handler.lambda_handler
    Code:
      S3Bucket: !Ref LambdaCodeBucket
      S3Key: !Ref LambdaCodeKey

LambdaCodeKey:
  Type: AWS::S3::Object
  Properties:
    Bucket: !Ref LambdaCodeBucket
    Key: lambda-deployment.zip
    SourceCode:
      ZipFile: |
        # 100+行代码内联在YAML中
```

### 现在（外部文件）

```yaml
PaymentCheckoutFunction:
  Type: AWS::Lambda::Function
  Properties:
    Handler: lambda_app.lambda_handler  # 使用外部文件
    Code:
      S3Bucket: !Ref LambdaCodeBucket
      S3Key: lambda-deployment.zip  # 直接引用zip文件
```

## ✅ 优势

### 1. 代码可维护性
- ✅ 代码在单独文件中，易于编辑
- ✅ 支持IDE语法高亮和自动补全
- ✅ 便于代码审查和版本控制

### 2. CloudFormation简洁性
- ✅ 模板文件更小（从289行减少到~120行）
- ✅ 更容易阅读和理解
- ✅ 减少YAML错误

### 3. 开发效率
- ✅ 可以独立开发和测试
- ✅ 本地测试更方便
- ✅ 快速迭代

### 4. 部署灵活性
- ✅ 可以单独更新代码而不修改模板
- ✅ 支持CI/CD流程
- ✅ 便于A/B测试

## 🔍 文件关系

```
lambda_app.py (FastAPI应用)
    ↓
lambda_handler = Mangum(app) (Lambda处理器)
    ↓
CloudFormation配置
    ↓
AWS Lambda Function
    ↓
Lambda Function URL
    ↓
外部访问
```

## 📝 更新代码

### 修改API端点

1. 编辑 `lambda_app.py`
2. 本地测试
3. 重新部署

```bash
# 编辑文件
vim lambda_app.py

# 本地测试
uvicorn lambda_app:app --reload

# 重新部署
./deploy-cost-optimized.sh dev us-east-1 default
```

### 添加新的依赖

1. 更新 `requirements.txt`
2. 重新部署

```bash
# 添加依赖
echo "new-package" >> requirements.txt

# 重新部署（会自动安装新依赖）
./deploy-cost-optimized.sh dev us-east-1 default
```

## 🛠️ 故障排查

### 问题：Lambda函数无法找到模块

**症状：** Lambda函数报错 "ModuleNotFoundError"

**解决方案：**
1. 检查部署脚本是否包含所有必要文件
2. 验证zip包内容
3. 确认文件路径正确

```bash
# 检查zip包内容
unzip -l lambda-deployment.zip
```

### 问题：Lambda函数超时

**症状：** Lambda函数执行超时

**解决方案：**
1. 增加Lambda超时时间（在CloudFormation模板中）
2. 优化代码性能
3. 检查外部API调用延迟

### 问题：CORS错误

**症状：** 浏览器控制台显示CORS错误

**解决方案：**
1. 检查Lambda Function URL的CORS配置
2. 验证Cloudflare代理设置
3. 检查前端API调用配置

## 📚 相关文档

- [AWS部署指南](../../AWS_DEPLOYMENT_GUIDE.md)
- [成本优化部署](../../COST_OPTIMIZED_DEPLOYMENT.md)
- [Cloudflare DNS配置](../../CLOUDFLARE_DNS_GUIDE.md)

## 🎯 最佳实践

1. **代码组织**
   - 保持lambda_app.py简洁
   - 将复杂逻辑移到service模块
   - 使用类型提示

2. **测试**
   - 本地测试后再部署
   - 编写单元测试
   - 使用测试环境

3. **部署**
   - 使用CI/CD自动化
   - 保留部署历史
   - 监控部署状态

4. **监控**
   - 设置CloudWatch告警
   - 监控Lambda指标
   - 记录错误日志

---

**总结：** 将代码提取到单独文件中使CloudFormation模板更简洁，代码更易于维护，开发更高效！