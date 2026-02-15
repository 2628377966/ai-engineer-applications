import json
import os
from mangum import Mangum
from fastapi import FastAPI
from pydantic import BaseModel
import random
import uuid
from risk_service import risk_check, verify_3ds, validate_3ds_code

app = FastAPI()

# In-memory storage for pending 3DS transactions
pending_transactions = {}

class PaymentRequest(BaseModel):
    amount: float
    currency: str = "CNY"
    payment_method: str
    card_number: str = None
    card_country: str = None
    ip_country: str = "CN"
    user_history: int = 0

class ThreeDSVerifyRequest(BaseModel):
    transaction_id: str
    verification_code: str
    card_number: str

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
            # Generate transaction ID and store payment data
            transaction_id = str(uuid.uuid4())
            pending_transactions[transaction_id] = {
                "payment_request": payment_request,
                "risk": risk,
                "timestamp": random.randint(100000, 999999)
            }
            return {
                "status": "pending_3ds",
                "transaction_id": transaction_id,
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
        "risk_level": risk['risk_level'],
        "reasons": risk['reasons'],
        "llm_insight": risk['llm_insight'],
        "message": result['message']
    }

@app.get("/health")
def health():
    """Health check endpoint"""
    return {"status": "ok", "service": "smart-checkout"}

@app.post("/checkout")
def checkout(request: PaymentRequest):
    """Checkout endpoint"""
    result = process_payment(request.dict())
    return result

@app.post("/3ds-verify")
def verify_3ds_code(request: ThreeDSVerifyRequest):
    """3DS verification endpoint"""
    result = validate_3ds_code(request)
    
    if result['success']:
        # Retrieve stored transaction data
        if request.transaction_id not in pending_transactions:
            return {
                "success": False,
                "message": "交易ID无效或已过期"
            }
        
        stored_data = pending_transactions[request.transaction_id]
        payment_request = stored_data["payment_request"]
        risk = stored_data["risk"]
        
        # Process payment with original transaction data
        method = payment_request['payment_method']
        if method == 'credit_card':
            payment_result = mock_credit_card_processor(payment_request)
        elif method == 'alipay':
            payment_result = mock_alipay_processor(payment_request)
        elif method == 'wechat_pay':
            payment_result = mock_wechat_processor(payment_request)
        else:
            return {
                "success": False,
                "message": "不支持的支付方式"
            }
        
        # Clean up stored transaction data
        del pending_transactions[request.transaction_id]
        
        result.update({
            "status": "success",
            "transaction_id": payment_result['id'],
            "payment_message": payment_result['message'],
            "risk_score": risk['risk_score']
        })
    
    return result

# Lambda handler
lambda_handler = Mangum(app)