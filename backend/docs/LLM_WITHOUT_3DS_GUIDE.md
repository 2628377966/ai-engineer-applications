# 如何触发LLM分析但不触发3DS验证

## 📋 概述

本指南详细说明如何配置交易以触发LLM风险分析，同时避免触发3DS验证。

## 🎯 核心原理

### 阈值配置

在 [rules.json](file:///d:\LucyProjects\ai-engineer-applications\backend\rules.json#L33-38) 中定义了两个关键阈值：

```json
"thresholds": {
  "requires_3ds": 40,        // 风险分数 > 40 时触发3DS验证
  "requires_llm_insight": 30   // 风险分数 > 30 时触发LLM分析
}
```

### 触发逻辑

在 [risk_service.py](file:///d:\LucyProjects\ai-engineer-applications\backend\risk_service.py#L102-107) 中：

```python
requires_3ds = risk_score > RULES_CONFIG.get('thresholds', {}).get('requires_3ds', 40)
requires_llm = risk_score > RULES_CONFIG.get('thresholds', {}).get('requires_llm_insight', 30)
```

### 目标风险分数范围

**要触发LLM但不触发3DS：30 < risk_score ≤ 40**

## 📊 风险规则评分

当前风险规则（[rules.json](file:///d:\LucyProjects\ai-engineer-applications\backend\rules.json#L2-28)）：

| 规则名称 | 条件 | 风险分数 |
|---------|-------|----------|
| 大额交易 | amount > 5000 | +20分 |
| 新用户 | user_history == 0 | +15分 |
| 跨境交易 | ip_country != card_country | +25分 |

## ✅ 成功示例

### 示例1：中等风险交易（35分）

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

**风险评分计算：**
- 大额交易 (6000 > 5000): +20分
- 新用户 (user_history == 0): +15分
- 跨境交易 (CN == CN): +0分
- **总分：35分**

**结果：**
- ✅ LLM分析：35 > 30 ✓
- ✅ 3DS验证：35 ≤ 40 ✗
- 📤 支付状态：成功
- 🤖 LLM分析：已触发

**响应示例：**
```json
{
  "status": "success",
  "transaction_id": "CC_999152",
  "risk_score": 35,
  "risk_level": "MEDIUM",
  "reasons": ["大额交易", "新用户"],
  "llm_insight": "基于交易分析，该笔交易风险评分为35，主要风险因素包括：大额交易, 新用户。建议正常处理。",
  "message": "信用卡支付成功"
}
```

## ❌ 失败示例

### 示例1：风险太低（25分）

```json
{
  "amount": 100.0,
  "currency": "CNY",
  "payment_method": "credit_card",
  "card_number": "4111111111111111",
  "card_country": "CN",
  "ip_country": "US",
  "user_history": 10
}
```

**风险评分计算：**
- 大额交易 (100 ≤ 5000): +0分
- 新用户 (10 ≠ 0): +0分
- 跨境交易 (US ≠ CN): +25分
- **总分：25分**

**结果：**
- ❌ LLM分析：25 ≤ 30 ✗
- ❌ 3DS验证：25 ≤ 40 ✗

### 示例2：风险太高（60分）

```json
{
  "amount": 6000.0,
  "currency": "CNY",
  "payment_method": "credit_card",
  "card_number": "4111111111111111",
  "card_country": "CN",
  "ip_country": "US",
  "user_history": 0
}
```

**风险评分计算：**
- 大额交易 (6000 > 5000): +20分
- 新用户 (0 == 0): +15分
- 跨境交易 (US ≠ CN): +25分
- **总分：60分**

**结果：**
- ✅ LLM分析：60 > 30 ✓
- ❌ 3DS验证：60 > 40 ✓

## 🧪 测试方法

### 使用测试脚本

运行 [test_llm_without_3ds.py](file:///d:\LucyProjects\ai-engineer-applications\backend\test_llm_without_3ds.py)：

```bash
cd backend
uv run python test_llm_without_3ds.py
```

### 手动测试

使用curl或Postman：

```bash
curl -X POST http://127.0.0.1:8000/checkout \
  -H "Content-Type: application/json" \
  -d '{
    "amount": 6000.0,
    "currency": "CNY",
    "payment_method": "credit_card",
    "card_number": "4111111111111111",
    "card_country": "CN",
    "ip_country": "CN",
    "user_history": 0
  }'
```

## 🎨 风险分数组合表

| 组合 | 大额 | 新用户 | 跨境 | 总分 | LLM | 3DS |
|-----|------|--------|------|------|------|------|
| 1 | ✓ | ✓ | ✗ | 35 | ✓ | ✗ |
| 2 | ✓ | ✗ | ✓ | 45 | ✓ | ✓ |
| 3 | ✗ | ✓ | ✓ | 40 | ✓ | ✗ |
| 4 | ✓ | ✓ | ✓ | 60 | ✓ | ✓ |
| 5 | ✗ | ✗ | ✓ | 25 | ✗ | ✗ |
| 6 | ✗ | ✓ | ✗ | 15 | ✗ | ✗ |

**推荐组合：组合1（35分）** - 触发LLM但不触发3DS

## 🔧 自定义配置

### 修改阈值

编辑 [rules.json](file:///d:\LucyProjects\ai-engineer-applications\backend\rules.json#L33-38)：

```json
"thresholds": {
  "requires_3ds": 50,        // 提高到50分
  "requires_llm_insight": 20   // 降低到20分
}
```

### 添加新风险规则

在 [rules.json](file:///d:\LucyProjects\ai-engineer-applications\backend\rules.json#L2-28) 中添加：

```json
{
  "name": "suspicious_time",
  "description": "可疑时间交易",
  "field": "hour",
  "threshold": 23,
  "score": 10,
  "message": "深夜交易",
  "operator": "gte"
}
```

## 📝 实际应用场景

### 场景1：新用户大额购买
- **情况**：新用户首次购买高价值商品
- **配置**：amount=6000, user_history=0, 同国家
- **结果**：35分，触发LLM分析，直接支付

### 场景2：跨境小额交易
- **情况**：用户在海外进行小额购买
- **配置**：amount=100, user_history=5, 跨境
- **结果**：25分，不触发LLM和3DS，直接支付

### 场景3：可疑交易
- **情况**：新用户跨境大额交易
- **配置**：amount=6000, user_history=0, 跨境
- **结果**：60分，触发LLM和3DS，需要验证

## 🚀 最佳实践

1. **监控风险分布**：定期检查不同风险分数的交易分布
2. **调整阈值**：根据实际业务需求调整 `requires_llm_insight` 和 `requires_3ds`
3. **LLM优化**：优化提示词以获得更准确的风险分析
4. **A/B测试**：测试不同阈值对业务的影响
5. **日志记录**：记录LLM分析结果用于后续分析

## 🔍 故障排查

### 问题：LLM分析未触发

**检查：**
1. 风险分数是否 > 30
2. API密钥是否正确配置
3. LLM服务是否可用

### 问题：意外触发3DS

**检查：**
1. 风险分数是否 > 40
2. 是否有其他风险规则被触发
3. 阈值配置是否正确

### 问题：响应中缺少llm_insight

**检查：**
1. [app.py](file:///d:\LucyProjects\ai-engineer-applications\backend\app.py#L89-97) 是否正确返回 `llm_insight`
2. 风险分数是否 > 30
3. LLM服务是否正常工作

## 📚 相关文件

- [app.py](file:///d:\LucyProjects\ai-engineer-applications\backend\app.py) - 主应用文件
- [risk_service.py](file:///d:\LucyProjects\ai-engineer-applications\backend\risk_service.py) - 风险评估服务
- [llm_service.py](file:///d:\LucyProjects\ai-engineer-applications\backend\llm_service.py) - LLM分析服务
- [rules.json](file:///d:\LucyProjects\ai-engineer-applications\backend\rules.json) - 风险规则配置
- [test_llm_without_3ds.py](file:///d:\LucyProjects\ai-engineer-applications\backend\test_llm_without_3ds.py) - 测试脚本

## ✨ 总结

要触发LLM分析但不触发3DS验证：

1. **确保风险分数在 30 < score ≤ 40 之间**
2. **推荐组合**：大额交易 (+20) + 新用户 (+15) = 35分
3. **避免跨境交易**：保持同国家交易
4. **验证响应**：检查 `llm_insight` 字段是否存在

这样可以在获得AI驱动的风险分析的同时，保持流畅的用户体验！