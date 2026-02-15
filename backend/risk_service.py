import json
import os
from llm_service import generate_llm_analysis

# Load risk rules from JSON file
RULES_FILE = "rules.json"

if os.path.exists(RULES_FILE):
    with open(RULES_FILE, 'r', encoding='utf-8') as f:
        RULES_CONFIG = json.load(f)
else:
    # Default rules if file not found
    RULES_CONFIG = {
        "risk_rules": [
            {
                "name": "amount",
                "description": "大额交易风险",
                "field": "amount",
                "threshold": 5000,
                "score": 20,
                "message": "大额交易",
                "operator": "gt"
            },
            {
                "name": "user_history",
                "description": "新用户风险",
                "field": "user_history",
                "threshold": 0,
                "score": 15,
                "message": "新用户",
                "operator": "eq"
            },
            {
                "name": "cross_border",
                "description": "跨境交易风险",
                "threshold": None,
                "score": 25,
                "message": "跨境交易",
                "operator": "not_eq",
                "fields": ["ip_country", "card_country"]
            }
        ],
        "risk_levels": {
            "high": 60,
            "medium": 30,
            "low": 0
        },
        "thresholds": {
            "requires_3ds": 40,
            "requires_llm_insight": 30
        },
        "max_score": 100
    }


def risk_check(transaction):
    """Risk assessment function using configurable rules"""
    risk_score = 0
    reasons = []
    
    # Apply risk rules from configuration
    for rule in RULES_CONFIG.get('risk_rules', []):
        rule_name = rule.get('name')
        operator = rule.get('operator')
        field = rule.get('field')
        threshold = rule.get('threshold')
        score = rule.get('score', 0)
        message = rule.get('message')
        fields = rule.get('fields', [])
        
        # Evaluate rule based on operator
        rule_applies = False
        
        if operator == 'gt' and field and field in transaction:
            rule_applies = transaction[field] > threshold
        elif operator == 'lt' and field and field in transaction:
            rule_applies = transaction[field] < threshold
        elif operator == 'eq' and field and field in transaction:
            rule_applies = transaction[field] == threshold
        elif operator == 'not_eq' and fields:
            if len(fields) == 2 and all(f in transaction for f in fields):
                rule_applies = transaction[fields[0]] != transaction[fields[1]]
        elif operator == 'gte' and field and field in transaction:
            rule_applies = transaction[field] >= threshold
        elif operator == 'lte' and field and field in transaction:
            rule_applies = transaction[field] <= threshold
        
        if rule_applies:
            risk_score += score
            if message:
                reasons.append(message)
    
    # Calculate risk level
    risk_levels = RULES_CONFIG.get('risk_levels', {})
    if risk_score > risk_levels.get('high', 60):
        risk_level = "HIGH"
    elif risk_score > risk_levels.get('medium', 30):
        risk_level = "MEDIUM"
    else:
        risk_level = "LOW"
    
    # Check if 3DS is required
    requires_3ds = risk_score > RULES_CONFIG.get('thresholds', {}).get('requires_3ds', 40)
    
    # LLM enhancement
    requires_llm = risk_score > RULES_CONFIG.get('thresholds', {}).get('requires_llm_insight', 30)
    if requires_llm:
        llm_insight = generate_llm_analysis(transaction, risk_score, reasons)
    else:
        llm_insight = None
    
    # Cap risk score at max
    max_score = RULES_CONFIG.get('max_score', 100)
    risk_score = min(risk_score, max_score)
    
    return {
        "risk_score": risk_score,
        "risk_level": risk_level,
        "requires_3ds": requires_3ds,
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


def validate_3ds_code(verification_request):
    """Validate 3DS verification code"""
    verification_code = verification_request.verification_code
    card_number = verification_request.card_number
    
    # Mock validation logic
    # For testing purposes, accept any 6-digit code that starts with '1'
    if len(verification_code) == 6 and verification_code.isdigit():
        if verification_code.startswith('1'):
            return {
                "success": True,
                "message": "3DS验证成功",
                "transaction_id": verification_request.transaction_id
            }
        else:
            return {
                "success": False,
                "message": "验证码错误，请重试"
            }
    else:
        return {
            "success": False,
            "message": "验证码格式错误"
        }