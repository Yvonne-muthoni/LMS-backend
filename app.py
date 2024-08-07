from flask import Flask, request, redirect, url_for, jsonify
from flask_cors import CORS
import requests
import json
import os

app = Flask(__name__)
CORS(app)  # Enable CORS

app.secret_key = os.getenv('SECRET_KEY', 'your_secret_key')

# PayPal credentials
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_API_BASE = "https://api-m.sandbox.paypal.com"

def get_paypal_access_token():
    auth = (PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET)
    headers = {
        'Accept': 'application/json',
        'Accept-Language': 'en_US',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    response = requests.post(f"{PAYPAL_API_BASE}/v1/oauth2/token",
                             auth=auth,
                             headers=headers,
                             data={'grant_type': 'client_credentials'})
    response.raise_for_status()
    return response.json()['access_token']

@app.route('/create-payment', methods=['POST'])
def create_payment():
    access_token = get_paypal_access_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    payment_data = {
        "intent": "AUTHORIZE",
        "payer": {
            "payment_method": "paypal"
        },
        "transactions": [{
            "amount": {
                "total": "10.00",
                "currency": "USD"
            },
            "description": "Subscription payment"
        }],
        "redirect_urls": {
            "return_url": url_for('execute_payment', _external=True),
            "cancel_url": url_for('cancel', _external=True)
        }
    }
    response = requests.post(f"{PAYPAL_API_BASE}/v1/payments/payment",
                             headers=headers,
                             data=json.dumps(payment_data))
    response.raise_for_status()
    payment = response.json()
    approval_url = next(link['href'] for link in payment['links'] if link['rel'] == 'approval_url')
    
    return jsonify({"success": True, "approvalUrl": approval_url})

@app.route('/execute-payment')
def execute_payment():
    payment_id = request.args.get('paymentId')
    payer_id = request.args.get('PayerID')

    access_token = get_paypal_access_token()
    headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {access_token}'
    }
    execute_data = {
        "payer_id": payer_id
    }
    url = f"{PAYPAL_API_BASE}/v1/payments/payment/{payment_id}/execute"
    response = requests.post(url, headers=headers, data=json.dumps(execute_data))

    if response.status_code == 200:
        payment = response.json()
        if payment['state'] == 'approved':
            return jsonify({"success": True, "message": "Your subscription was successful!"})
        return jsonify({"success": False, "message": "Payment was not approved."})
    else:
        return jsonify({"success": False, "message": "Payment execution failed."})

@app.route('/cancel')
def cancel():
    return jsonify({"success": False, "message": "Your subscription was canceled."})

if __name__ == '__main__':
    app.run(debug=True)
