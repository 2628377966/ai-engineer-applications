# Smart Payment Checkout - Backend

智能支付结算系统后端，包含风险评估、3DS验证和LLM分析功能。

## 📁 项目结构

```
backend/
├── app.py                      # FastAPI主应用文件
├── risk_service.py              # 风险评估服务
├── llm_service.py               # LLM分析服务
├── rules.json                  # 风险规则配置
├── .env.example                # 环境变量示例
├── pyproject.toml              # 项目配置和依赖
├── requirements.txt             # Python依赖列表
├── uv.lock                   # uv锁文件
│
├── tests/                     # 测试文件目录
│   ├── test_3ds_fix.py              # 3DS验证流程测试
│   ├── test_field_rules.py          # 字段规则测试
│   ├── test_llm_without_3ds.py    # LLM分析测试
│   ├── test_risk_check.py           # 风险检查测试
│   ├── test_risk_local.py          # 本地风险测试
│   └── test_risk_service.py        # 风险服务测试
│
└── docs/                      # 文档目录
    ├── DEEPSEEK_LLM_GUIDE.md       # DeepSeek LLM集成指南
    ├── LLM_WITHOUT_3DS_GUIDE.md    # LLM分析不触发3DS指南
    └── SETUP.md                    # 项目设置指南
```

## 🚀 快速开始

### 1. 安装依赖

```bash
cd backend
uv sync
```

### 2. 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件，添加你的API密钥
```

### 3. 启动服务器

```bash
uv run uvicorn app:app --reload
```

服务器将在 http://127.0.0.1:8000 启动

## 🧪 运行测试

所有测试文件都在 `tests/` 目录中：

### 运行单个测试

```bash
# 测试3DS验证流程
uv run python tests/test_3ds_fix.py

# 测试LLM分析（不触发3DS）
uv run python tests/test_llm_without_3ds.py

# 测试风险规则
uv run python tests/test_field_rules.py

# 测试风险检查
uv run python tests/test_risk_check.py

# 测试风险服务
uv run python tests/test_risk_service.py

# 本地风险测试
uv run python tests/test_risk_local.py
```

### 运行所有测试

```bash
cd tests
for file in test_*.py; do uv run python "$file"; done
```

## 📚 文档

所有文档都在 `docs/` 目录中：

### [DEEPSEEK_LLM_GUIDE.md](docs/DEEPSEEK_LLM_GUIDE.md)
DeepSeek LLM集成完整指南，包括：
- 配置说明
- 使用示例
- 错误处理
- 生产环境考虑

### [LLM_WITHOUT_3DS_GUIDE.md](docs/LLM_WITHOUT_3DS_GUIDE.md)
如何触发LLM分析但不触发3DS验证的详细指南：
- 风险评分机制
- 示例组合
- 测试方法
- 故障排查

### [SETUP.md](docs/SETUP.md)
项目设置和配置指南

## 🔧 核心功能

### 1. 风险评估
- 基于可配置规则的风险评分
- 支持多种风险因素（大额交易、新用户、跨境交易）
- 动态规则评估

### 2. 3DS验证
- 高风险交易自动触发3DS验证
- 交易数据完整保存
- 验证后自动完成支付

### 3. LLM分析
- 集成DeepSeek模型进行智能风险分析
- 专业的中文风控建议
- 降级机制确保服务可用性

### 4. 支付路由
- 支持信用卡、支付宝、微信支付
- 根据风险等级自动路由
- 模拟支付处理器

## 📊 API端点

### POST /checkout
处理支付请求，包括风险评估和支付路由。

**请求体：**
```json
{
  "amount": 6000.0,
  "currency": "CNY",
  "payment_method": "credit_card",
  "card_number": "4111111111111111",
  "card_country": "CN",
  "ip_country": "CN",
  "user_history": 0
}
```

**响应：**
```json
{
  "status": "success",
  "transaction_id": "CC_999152",
  "risk_score": 35,
  "risk_level": "MEDIUM",
  "reasons": ["大额交易", "新用户"],
  "llm_insight": "基于交易分析，该笔交易风险评分为35...",
  "message": "信用卡支付成功"
}
```

### POST /3ds-verify
完成3DS验证并处理支付。

**请求体：**
```json
{
  "transaction_id": "uuid-here",
  "verification_code": "123456",
  "card_number": "4111111111111111"
}
```

### GET /health
健康检查端点。

## ⚙️ 配置

### 风险规则配置 (rules.json)

```json
{
  "risk_rules": [
    {
      "name": "amount",
      "description": "大额交易风险",
      "field": "amount",
      "threshold": 5000,
      "score": 20,
      "message": "大额交易",
      "operator": "gt"
    }
  ],
  "thresholds": {
    "requires_3ds": 40,
    "requires_llm_insight": 30
  }
}
```

### 环境变量 (.env)

```bash
# OpenAI API配置
OPENAI_API_KEY=your_deepseek_api_key
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

## 🎯 使用场景

### 场景1：低风险直接支付
- 风险分数：0-30
- 处理：直接支付，无需验证
- LLM分析：不触发

### 场景2：中等风险 + LLM分析
- 风险分数：31-40
- 处理：直接支付，包含LLM分析
- LLM分析：触发

### 场景3：高风险 + 3DS验证
- 风险分数：>40
- 处理：3DS验证，然后支付
- LLM分析：触发

## 🔍 故障排查

### 问题：LLM分析未触发
**解决方案：**
1. 检查风险分数是否 > 30
2. 验证API密钥配置
3. 查看服务器日志

### 问题：3DS验证失败
**解决方案：**
1. 确认交易ID有效
2. 检查验证码格式（6位数字，以1开头）
3. 验证交易数据是否正确存储

### 问题：测试失败
**解决方案：**
1. 确保服务器正在运行
2. 检查依赖是否正确安装
3. 查看测试脚本中的错误信息

## 📝 开发指南

### 添加新的风险规则

编辑 `rules.json`，添加新规则：

```json
{
  "name": "new_rule",
  "description": "新风险规则",
  "field": "field_name",
  "threshold": 100,
  "score": 10,
  "message": "风险描述",
  "operator": "gt"
}
```

### 修改LLM提示词

编辑 `llm_service.py` 中的 `generate_llm_analysis` 函数。

### 添加新的支付方式

在 `app.py` 中添加新的处理器函数并更新路由逻辑。

## 🤝 贡献

欢迎贡献！请遵循以下步骤：

1. Fork项目
2. 创建特性分支
3. 提交更改
4. 推送到分支
5. 创建Pull Request

## 📄 许可证

本项目采用MIT许可证。

## 📞 联系方式

如有问题或建议，请创建Issue或联系维护者。

---

**注意：** 这是一个演示项目，用于展示智能支付结算系统的架构和功能。在生产环境中使用前，请确保进行充分的安全审查和测试。