import os
from dotenv import load_dotenv
from openai import OpenAI

# Load environment variables
load_dotenv()

# Initialize OpenAI client with DeepSeek configuration
openai_api_key = os.getenv("OPENAI_API_KEY")
openai_base_url = os.getenv("OPENAI_BASE_URL", "https://api.deepseek.com")
openai_model = os.getenv("OPENAI_MODEL", "deepseek-chat")

# Only initialize client if API key is available
client = None
if openai_api_key and openai_api_key != "your_openai_api_key_here":
    client = OpenAI(
        api_key=openai_api_key,
        base_url=openai_base_url
    )


def generate_llm_analysis(transaction, risk_score, reasons):
    """Generate LLM analysis for risk assessment using DeepSeek"""
    if not client:
        # Fallback to mock analysis if client not initialized
        return f"基于交易分析，该笔交易风险评分为{risk_score}，主要风险因素包括：{', '.join(reasons)}。建议{'加强监控' if risk_score > 50 else '正常处理'}。"
    
    try:
        # Prepare transaction context for LLM
        transaction_context = {
            "amount": transaction.get('amount', 0),
            "currency": transaction.get('currency', 'CNY'),
            "payment_method": transaction.get('payment_method', 'unknown'),
            "user_history": transaction.get('user_history', 0),
            "ip_country": transaction.get('ip_country', 'unknown'),
            "card_country": transaction.get('card_country', 'unknown')
        }
        
        # Create prompt for LLM
        prompt = f"""
你是一个专业的支付风控分析师。请分析以下交易的风险情况：

交易信息：
- 金额: {transaction_context['amount']} {transaction_context['currency']}
- 支付方式: {transaction_context['payment_method']}
- 用户历史交易次数: {transaction_context['user_history']}
- IP地址国家: {transaction_context['ip_country']}
- 卡片国家: {transaction_context['card_country']}

风险评分: {risk_score}/100
风险因素: {', '.join(reasons)}

请提供详细的风险分析，包括：
1. 对主要风险因素的评估
2. 潜在的欺诈风险
3. 建议的处理措施

请用中文回答，保持专业和简洁。
"""
        
        # Call DeepSeek API
        response = client.chat.completions.create(
            model=openai_model,
            messages=[
                {
                    "role": "system",
                    "content": "你是一个专业的支付风控分析师，擅长识别交易风险和提供风控建议。"
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        # Extract and return analysis
        analysis = response.choices[0].message.content.strip()
        return analysis
        
    except Exception as e:
        # Fallback to mock analysis if API call fails
        print(f"LLM API调用失败: {str(e)}")
        return f"基于交易分析，该笔交易风险评分为{risk_score}，主要风险因素包括：{', '.join(reasons)}。建议{'加强监控' if risk_score > 50 else '正常处理'}。"


def get_llm_status():
    """Check if LLM is properly configured"""
    return {
        "configured": bool(client),
        "model": openai_model,
        "base_url": openai_base_url,
        "api_key_provided": bool(openai_api_key and openai_api_key != "your_openai_api_key_here")
    }