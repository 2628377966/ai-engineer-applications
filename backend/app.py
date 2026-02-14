from fastapi import FastAPI
from pydantic import BaseModel
import random

app = FastAPI()

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "CNY"
    payment_method: str
    card_number: str = None
    card_country: str = None
    ip_country: str = "CN"
    user_history: int = 0

def generate_llm_analysis(transaction, risk_score, reasons):
    """Mock LLM analysis for risk assessment"""
    return f"基于交易分析，该笔交易风险评分为{risk_score}，主要风险因素包括：{', '.join(reasons)}。建议{'加强监控' if risk_score > 50 else '正常处理'}。"

def risk_check(transaction):
    """Risk assessment function"""
    risk_score = 0
    reasons = []
    
    # Rule 1: Amount
    if transaction['amount'] > 5000:
        risk_score += 20
        reasons.append("大额交易")
    
    # Rule 2: New user
    if transaction.get('user_history') == 0:
        risk_score += 15
        reasons.append("新用户")
    
    # Rule 3: Cross-border
    if transaction.get('ip_country') != transaction.get('card_country'):
        risk_score += 25
        reasons.append("跨境交易")
    
    # LLM enhancement
    if risk_score > 30:
        llm_insight = generate_llm_analysis(transaction, risk_score, reasons)
    else:
        llm_insight = None
    
    return {
        "risk_score": risk_score,
        "risk_level": "HIGH" if risk_score > 60 else "MEDIUM" if risk_score > 30 else "LOW",
        "requires_3ds": risk_score > 40,
        "reasons": reasons,
        "llm_insight": llm_insight
    }

def verify_3ds(transaction, risk_result):
    """Mock 3DS verification"""
    if not risk_result['requires_3ds']:
        return {"status": "skipped", "reason": "低风险交易"}
    
    return {
        "status": "challenge",
        "method": "3DS2.0",
        "issuer_bank": "Mock Bank",
        "verification_url": "/3ds-challenge-page"
    }

def mock_credit_card_processor(payment_request):
    """Mock credit card payment processor"""
    return {
        "success": True,
        "id": f"CC_{random.randint(100000, 999999)}",
        "message": "信用卡支付成功"
    }

def mock_alipay_processor(payment_request):
    """Mock Alipay payment processor"""
    return {
        "success": True,
        "id": f"ALI_{random.randint(100000, 999999)}",
        "message": "支付宝支付成功"
    }

def mock_wechat_processor(payment_request):
    """Mock WeChat Pay payment processor"""
    return {
        "success": True,
        "id": f"WX_{random.randint(100000, 999999)}",
        "message": "微信支付成功"
    }

def process_payment(payment_request):
    """Process payment with risk assessment and routing"""
    # 1. Risk check
    risk = risk_check(payment_request)
    
    # 2. 3DS verification
    if risk['requires_3ds']:
        three_ds_result = verify_3ds(payment_request, risk)
        if three_ds_result['status'] == 'challenge':
            return {
                "status": "pending_3ds",
                "risk": risk,
                "next_step": "complete_3ds_verification"
            }
    
    # 3. Route to payment channel
    method = payment_request['payment_method']
    if method == 'credit_card':
        result = mock_credit_card_processor(payment_request)
    elif method == 'alipay':
        result = mock_alipay_processor(payment_request)
    elif method == 'wechat_pay':
        result = mock_wechat_processor(payment_request)
    else:
        return {
            "status": "failed",
            "transaction_id": None,
            "risk_score": risk['risk_score'],
            "message": "不支持的支付方式"
        }
    
    return {
        "status": "success" if result['success'] else "failed",
        "transaction_id": result['id'],
        "risk_score": risk['risk_score'],
        "message": result['message']
    }

@app.post("/checkout")
def checkout(request: PaymentRequest):
    """Checkout endpoint"""
    result = process_payment(request.dict())
    return result

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "smart-checkout"}
