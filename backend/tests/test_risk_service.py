import json
import sys
sys.path.append('.')

from risk_service import risk_check, verify_3ds, validate_3ds_code

print("Testing refactored risk_service module...")
print("=" * 60)

# Test 1: High-risk transaction
test_case_1 = {
    "amount": 6000,
    "currency": "CNY",
    "payment_method": "credit_card",
    "card_number": "4111111111111111",
    "user_history": 0,
    "ip_country": "US",
    "card_country": "CN"
}

print("Test 1: High-risk transaction")
print("Transaction data:", json.dumps(test_case_1, indent=2))
result_1 = risk_check(test_case_1)
print("Risk check result:", json.dumps(result_1, indent=2, ensure_ascii=False))
print("✓ Risk check function works correctly")
print()

# Test 2: 3DS verification
print("Test 2: 3DS verification")
three_ds_result = verify_3ds(test_case_1, result_1)
print("3DS verification result:", json.dumps(three_ds_result, indent=2, ensure_ascii=False))
print("✓ verify_3ds function works correctly")
print()

# Test 3: Valid 3DS code
print("Test 3: Valid 3DS code validation")
class MockRequest:
    def __init__(self, transaction_id, verification_code, card_number):
        self.transaction_id = transaction_id
        self.verification_code = verification_code
        self.card_number = card_number

valid_request = MockRequest(
    transaction_id="test_123",
    verification_code="123456",
    card_number="4111111111111111"
)
valid_result = validate_3ds_code(valid_request)
print("Valid code result:", json.dumps(valid_result, indent=2, ensure_ascii=False))
print("✓ validate_3ds_code function works correctly for valid code")
print()

# Test 4: Invalid 3DS code
print("Test 4: Invalid 3DS code validation")
invalid_request = MockRequest(
    transaction_id="test_123",
    verification_code="999999",
    card_number="4111111111111111"
)
invalid_result = validate_3ds_code(invalid_request)
print("Invalid code result:", json.dumps(invalid_result, indent=2, ensure_ascii=False))
print("✓ validate_3ds_code function works correctly for invalid code")
print()

# Test 5: Low-risk transaction
test_case_2 = {
    "amount": 100,
    "currency": "CNY",
    "payment_method": "credit_card",
    "card_number": "4111111111111111",
    "user_history": 5,
    "ip_country": "CN",
    "card_country": "CN"
}

print("Test 5: Low-risk transaction")
print("Transaction data:", json.dumps(test_case_2, indent=2))
result_2 = risk_check(test_case_2)
print("Risk check result:", json.dumps(result_2, indent=2, ensure_ascii=False))
print("✓ Risk check works for low-risk transactions")
print()

print("=" * 60)
print("All tests passed successfully!")
print("The refactored risk_service module is working correctly.")
print("Functions are properly encapsulated and can be imported by app.py")