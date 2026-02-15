import requests
import json

# Test the checkout endpoint with high-risk transaction
test_data = {
    "amount": 6000,
    "currency": "CNY",
    "payment_method": "credit_card",
    "card_number": "4111111111111111",
    "user_history": 0,
    "ip_country": "US",
    "card_country": "CN"
}

url = "http://127.0.0.1:8000/checkout"
headers = {"Content-Type": "application/json"}

print("Testing high-risk transaction...")
print("Request data:", json.dumps(test_data, indent=2))
print()

try:
    response = requests.post(url, json=test_data, headers=headers, timeout=10)
    print(f"Response status: {response.status_code}")
    print("Response data:", json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")

print()
print("Testing low-risk transaction...")

# Test the checkout endpoint with low-risk transaction
low_risk_data = {
    "amount": 100,
    "currency": "CNY",
    "payment_method": "credit_card",
    "card_number": "4111111111111111",
    "user_history": 5,
    "ip_country": "CN",
    "card_country": "CN"
}

print("Request data:", json.dumps(low_risk_data, indent=2))
print()

try:
    response = requests.post(url, json=low_risk_data, headers=headers, timeout=10)
    print(f"Response status: {response.status_code}")
    print("Response data:", json.dumps(response.json(), indent=2, ensure_ascii=False))
except Exception as e:
    print(f"Error: {e}")