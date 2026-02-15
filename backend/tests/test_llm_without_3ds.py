"""
Test script to demonstrate LLM analysis without 3DS verification
This shows how to trigger LLM insight while avoiding 3DS verification
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_llm_without_3ds():
    """
    Test transaction that triggers LLM analysis but NOT 3DS verification
    Target risk score: 30 < score <= 40
    """
    print("=" * 70)
    print("测试：触发LLM分析但不触发3DS验证")
    print("=" * 70)
    
    # Calculate risk score:
    # - amount > 5000: +20分 (大额交易)
    # - user_history == 0: +15分 (新用户)
    # Total: 35分 (30 < 35 <= 40) ✓
    
    payment_request = {
        "amount": 6000.0,           # 触发大额交易规则 (+20分)
        "currency": "CNY",
        "payment_method": "credit_card",
        "card_number": "4111111111111111",
        "card_country": "CN",        # 同国家，不触发跨境交易
        "ip_country": "CN",
        "user_history": 0            # 触发新用户规则 (+15分)
    }
    
    print(f"\n📊 风险评分计算:")
    print(f"   - 大额交易 (amount > 5000): +20分")
    print(f"   - 新用户 (user_history == 0): +15分")
    print(f"   - 跨境交易 (IP != Card): +0分")
    print(f"   总风险分数: 35分")
    print(f"\n🎯 目标范围: 30 < 分数 <= 40")
    print(f"   - LLM分析触发: 35 > 30 ✓")
    print(f"   - 3DS验证触发: 35 > 40 ✗")
    
    print(f"\n📝 发送支付请求:")
    print(json.dumps(payment_request, indent=2))
    
    response = requests.post(f"{BASE_URL}/checkout", json=payment_request)
    result = response.json()
    
    print(f"\n📥 支付响应:")
    print(json.dumps(result, indent=2))
    
    print(f"\n✅ 验证结果:")
    status = result.get("status")
    risk_score = result.get("risk_score")
    llm_insight = result.get("llm_insight")
    
    if status == "success":
        print(f"   ✓ 支付状态: 成功 (无需3DS验证)")
        print(f"   ✓ 风险分数: {risk_score}")
        if llm_insight:
            print(f"   ✓ LLM分析: 已触发")
            print(f"\n🤖 LLM分析内容:")
            print(f"   {llm_insight}")
        else:
            print(f"   ✗ LLM分析: 未触发")
        
        if risk_score > 30 and risk_score <= 40:
            print(f"\n🎉 成功！风险分数{risk_score}在目标范围内(30 < {risk_score} <= 40)")
            print(f"   - 触发了LLM分析 (分数 > 30)")
            print(f"   - 没有触发3DS验证 (分数 <= 40)")
            return True
        else:
            print(f"\n⚠️  警告：风险分数{risk_score}不在目标范围内")
            return False
    elif status == "pending_3ds":
        print(f"   ✗ 支付状态: 等待3DS验证")
        print(f"   ✗ 风险分数: {risk_score} (太高，触发了3DS)")
        print(f"\n❌ 失败：风险分数{risk_score} > 40，触发了3DS验证")
        return False
    else:
        print(f"   ✗ 支付状态: {status}")
        return False

def test_boundary_cases():
    """Test boundary cases for LLM and 3DS thresholds"""
    print("\n\n" + "=" * 70)
    print("边界情况测试")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "低风险 (20分) - 不触发LLM和3DS",
            "amount": 100,
            "user_history": 10,
            "card_country": "CN",
            "ip_country": "CN",
            "expected_llm": False,
            "expected_3ds": False
        },
        {
            "name": "刚好触发LLM (31分) - 触发LLM但不触发3DS",
            "amount": 5200,
            "user_history": 10,
            "card_country": "CN",
            "ip_country": "CN",
            "expected_llm": True,
            "expected_3ds": False
        },
        {
            "name": "刚好触发3DS (41分) - 同时触发LLM和3DS",
            "amount": 5200,
            "user_history": 0,
            "card_country": "CN",
            "ip_country": "CN",
            "expected_llm": True,
            "expected_3ds": True
        }
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n测试 {i}: {test_case['name']}")
        
        payment_request = {
            "amount": test_case['amount'],
            "currency": "CNY",
            "payment_method": "credit_card",
            "card_number": "4111111111111111",
            "card_country": test_case['card_country'],
            "ip_country": test_case['ip_country'],
            "user_history": test_case['user_history']
        }
        
        response = requests.post(f"{BASE_URL}/checkout", json=payment_request)
        result = response.json()
        
        risk_score = result.get("risk_score", 0)
        has_llm = bool(result.get("llm_insight"))
        has_3ds = result.get("status") == "pending_3ds"
        
        print(f"   实际风险分数: {risk_score}")
        print(f"   LLM分析: {'✓' if has_llm else '✗'} (预期: {'✓' if test_case['expected_llm'] else '✗'})")
        print(f"   3DS验证: {'✓' if has_3ds else '✗'} (预期: {'✓' if test_case['expected_3ds'] else '✗'})")
        
        llm_match = has_llm == test_case['expected_llm']
        ds_match = has_3ds == test_case['expected_3ds']
        
        if llm_match and ds_match:
            print(f"   ✅ 测试通过")
        else:
            print(f"   ❌ 测试失败")

if __name__ == "__main__":
    try:
        # Main test: LLM without 3DS
        success = test_llm_without_3ds()
        
        # Boundary tests
        test_boundary_cases()
        
        print("\n" + "=" * 70)
        print("总结")
        print("=" * 70)
        print("要触发LLM分析但不触发3DS验证：")
        print("1. 风险分数必须在 30 < score <= 40 之间")
        print("2. 当前配置：")
        print("   - requires_llm_insight: 30")
        print("   - requires_3ds: 40")
        print("3. 示例组合：")
        print("   - 大额交易 (+20分) + 新用户 (+15分) = 35分 ✓")
        print("   - 跨境交易 (+25分) = 25分 ✗ (太低)")
        print("   - 大额 (+20) + 新用户 (+15) + 跨境 (+25) = 60分 ✗ (太高)")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ 测试执行失败: {str(e)}")
        import traceback
        traceback.print_exc()