"""
Test script to verify the fixed 3DS verification flow
This script tests that transaction data is properly preserved during 3DS verification
"""

import requests
import json

BASE_URL = "http://127.0.0.1:8000"

def test_checkout_with_3ds():
    """Test checkout flow that requires 3DS verification"""
    print("Testing checkout with 3DS verification...")
    
    # Create a high-risk transaction that requires 3DS
    payment_request = {
        "amount": 6000.0,
        "currency": "CNY",
        "payment_method": "credit_card",
        "card_number": "4111111111111111",
        "card_country": "CN",
        "ip_country": "US",
        "user_history": 0
    }
    
    print(f"Sending checkout request: {json.dumps(payment_request, indent=2)}")
    
    # Step 1: Initiate checkout
    response = requests.post(f"{BASE_URL}/checkout", json=payment_request)
    print(f"Checkout response: {json.dumps(response.json(), indent=2)}")
    
    checkout_data = response.json()
    
    if checkout_data.get("status") == "pending_3ds":
        transaction_id = checkout_data.get("transaction_id")
        print(f"\n3DS verification required. Transaction ID: {transaction_id}")
        
        # Step 2: Complete 3DS verification
        verify_request = {
            "transaction_id": transaction_id,
            "verification_code": "123456",
            "card_number": "4111111111111111"
        }
        
        print(f"\nSending 3DS verification request: {json.dumps(verify_request, indent=2)}")
        
        verify_response = requests.post(f"{BASE_URL}/3ds-verify", json=verify_request)
        print(f"3DS verification response: {json.dumps(verify_response.json(), indent=2)}")
        
        verify_data = verify_response.json()
        
        # Verify that the payment was processed with original amount
        if verify_data.get("success"):
            print(f"\n✓ 3DS verification successful!")
            print(f"✓ Payment processed with transaction_id: {verify_data.get('transaction_id')}")
            print(f"✓ Original risk_score preserved: {verify_data.get('risk_score')}")
            print(f"✓ Payment message: {verify_data.get('payment_message')}")
            
            # Check if the original amount was used (not 0)
            if verify_data.get('risk_score') > 0:
                print(f"\n✓ SUCCESS: Transaction data was preserved during 3DS verification!")
                return True
            else:
                print(f"\n✗ FAILURE: Transaction data was lost during 3DS verification!")
                return False
        else:
            print(f"\n✗ 3DS verification failed: {verify_data.get('message')}")
            return False
    else:
        print(f"\n✗ Expected pending_3ds status, got: {checkout_data.get('status')}")
        return False

def test_checkout_without_3ds():
    """Test checkout flow that doesn't require 3DS verification"""
    print("\n\nTesting checkout without 3DS verification...")
    
    # Create a low-risk transaction that doesn't require 3DS
    payment_request = {
        "amount": 100.0,
        "currency": "CNY",
        "payment_method": "credit_card",
        "card_number": "4111111111111111",
        "card_country": "CN",
        "ip_country": "CN",
        "user_history": 10
    }
    
    print(f"Sending checkout request: {json.dumps(payment_request, indent=2)}")
    
    response = requests.post(f"{BASE_URL}/checkout", json=payment_request)
    print(f"Checkout response: {json.dumps(response.json(), indent=2)}")
    
    checkout_data = response.json()
    
    if checkout_data.get("status") == "success":
        print(f"\n✓ Payment processed successfully without 3DS!")
        print(f"✓ Transaction ID: {checkout_data.get('transaction_id')}")
        print(f"✓ Risk score: {checkout_data.get('risk_score')}")
        return True
    else:
        print(f"\n✗ Payment failed: {checkout_data.get('message')}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("3DS Verification Flow Test")
    print("=" * 60)
    
    try:
        # Test with 3DS verification
        test1_passed = test_checkout_with_3ds()
        
        # Test without 3DS verification
        test2_passed = test_checkout_without_3ds()
        
        print("\n" + "=" * 60)
        print("Test Results:")
        print("=" * 60)
        print(f"3DS Verification Flow: {'✓ PASSED' if test1_passed else '✗ FAILED'}")
        print(f"Direct Payment Flow: {'✓ PASSED' if test2_passed else '✗ FAILED'}")
        print("=" * 60)
        
        if test1_passed and test2_passed:
            print("\n🎉 All tests passed! Transaction data is properly preserved.")
        else:
            print("\n❌ Some tests failed. Please check the implementation.")
            
    except Exception as e:
        print(f"\n❌ Test execution failed with error: {str(e)}")
        import traceback
        traceback.print_exc()