# DeepSeek LLM Integration Guide

## Overview
The risk assessment system now uses real LLM analysis via OpenAI API with the DeepSeek model (`deepseek-chat`) for enhanced risk assessment.

## Configuration

### 1. Install Dependencies
The OpenAI package has been added to `pyproject.toml`. Install it using:

```bash
uv sync
```

### 2. Set Up Environment Variables

Create a `.env` file in the backend directory with your DeepSeek API credentials:

```bash
# Copy the example file
cp .env.example .env

# Edit .env and add your actual API key
OPENAI_API_KEY=your_actual_deepseek_api_key_here
OPENAI_BASE_URL=https://api.deepseek.com
OPENAI_MODEL=deepseek-chat
```

### 3. Get DeepSeek API Key

1. Visit [DeepSeek Platform](https://platform.deepseek.com/)
2. Sign up or log in
3. Navigate to API Keys section
4. Create a new API key
5. Copy the API key to your `.env` file

## How It Works

### LLM Analysis Flow

1. **Risk Assessment**: Transaction is evaluated using configurable rules
2. **Score Calculation**: Risk score is computed based on rule violations
3. **LLM Enhancement**: If risk score > 30, LLM analysis is triggered
4. **API Call**: DeepSeek API is called with transaction context
5. **Response Processing**: LLM provides detailed risk analysis in Chinese

### Prompt Structure

The LLM receives a structured prompt containing:
- Transaction amount and currency
- Payment method
- User transaction history
- IP address country
- Card country
- Calculated risk score
- Identified risk factors

The LLM is instructed to provide:
1. Assessment of main risk factors
2. Potential fraud risks
3. Recommended processing measures

## Features

### Smart Fallback
- If API key is not configured, falls back to mock analysis
- If API call fails, provides error message and fallback analysis
- Ensures system continues to work without interruption

### Configuration Options
- **OPENAI_API_KEY**: Your DeepSeek API key
- **OPENAI_BASE_URL**: API endpoint (default: https://api.deepseek.com)
- **OPENAI_MODEL**: Model to use (default: deepseek-chat)

### API Parameters
- **Temperature**: 0.7 (balanced creativity and consistency)
- **Max Tokens**: 500 (sufficient for detailed analysis)
- **Language**: Chinese responses

## Testing

### Without API Key (Mock Mode)
The system will work with mock analysis:
```python
"基于交易分析，该笔交易风险评分为60，主要风险因素包括：大额交易, 新用户, 跨境交易。建议加强监控。"
```

### With API Key (Real LLM)
The system will provide detailed AI analysis:
```python
"根据交易分析，该笔交易风险评分为60/100。主要风险因素包括：
1. 大额交易风险：6000元超过正常交易阈值，存在资金异常风险
2. 新用户风险：用户历史交易次数为0，缺乏行为数据参考
3. 跨境交易风险：IP地址国家(US)与卡片国家(CN)不一致，可能存在卡片盗用风险

建议措施：
- 启动3D Secure验证
- 加强交易监控
- 设置交易限额
- 进行用户身份二次验证"
```

## Usage Example

```python
from risk_service import risk_check

# High-risk transaction that triggers LLM analysis
transaction = {
    "amount": 6000,
    "currency": "CNY",
    "payment_method": "credit_card",
    "card_number": "4111111111111111",
    "user_history": 0,
    "ip_country": "US",
    "card_country": "CN"
}

result = risk_check(transaction)
# result will include 'llm_insight' with DeepSeek analysis
```

## Error Handling

### API Connection Issues
- Error logged to console: "LLM API调用失败: [error details]"
- System continues with mock analysis
- No service interruption

### Invalid API Key
- Client not initialized
- Mock analysis used instead
- System remains functional

## Benefits

### Enhanced Risk Assessment
- AI-powered analysis beyond rule-based scoring
- Context-aware risk evaluation
- Detailed recommendations

### Improved Security
- Better fraud detection
- Proactive risk mitigation
- Actionable insights

### Scalability
- Easy to switch between different LLM providers
- Configurable prompts and parameters
- Flexible fallback mechanisms

## Troubleshooting

### Issue: LLM analysis not appearing
**Solution**: Check if risk score > 30 (LLM threshold)
**Verify**: API key is properly set in `.env`
**Check**: Backend server is restarted after configuration changes

### Issue: API errors in logs
**Solution**: Verify API key is valid and has sufficient credits
**Check**: DeepSeek API service status
**Test**: API connectivity using curl or similar tool

### Issue: Slow response times
**Solution**: Consider reducing max_tokens or adjusting temperature
**Optimize**: Cache common transaction patterns
**Monitor**: API response times and set appropriate timeouts

## Production Considerations

1. **API Rate Limits**: Monitor and respect DeepSeek API rate limits
2. **Cost Management**: Track API usage and costs
3. **Error Handling**: Implement retry logic for transient failures
4. **Logging**: Comprehensive logging for debugging and monitoring
5. **Caching**: Consider caching LLM responses for similar transactions
6. **Fallback**: Always maintain fallback mechanisms for service continuity

## Next Steps

To further enhance the system:
1. Implement request/response caching
2. Add retry logic with exponential backoff
3. Monitor API usage and costs
4. Add A/B testing for different prompts
5. Implement custom model fine-tuning if needed