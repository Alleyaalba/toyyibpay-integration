from flask import Flask, request, redirect
import requests

app = Flask(__name__)

# Toyyibpay API Credentials
USER_SECRET_KEY = '70mpdq70-kub2-ly4b-ugdx-04wn4peurx10'
CATEGORY_CODE = '4sgntdmo'

@app.route('/pay')
def create_bill():
    order_id = request.args.get('order_id')
    amount = request.args.get('amount')  # example: 100.00

    if not order_id or not amount:
        return "Missing order_id or amount!"

    try:
        bill_amount = int(float(amount) * 100)  # Convert to sen
    except ValueError:
        return "Invalid amount format!"

    payload = {
        'userSecretKey': USER_SECRET_KEY,
        'categoryCode': CATEGORY_CODE,
        'billName': f"Order #{order_id}",
        'billDescription': f"Payment for Order #{order_id}",
        'billPriceSetting': 1,
        'billPayorInfo': 1,
        'billAmount': bill_amount,
        'returnUrl': 'https://edu-ecoshop1.odoo.com/payment/confirmation',
        'callbackUrl': 'https://toyyibpay-integration.onrender.com/toyyibpay-webhook'
    }

    response = requests.post('https://toyyibpay.com/index.php/api/createBill', data=payload)
    result = response.json()

    if isinstance(result, list) and 'BillCode' in result[0]:
        bill_code = result[0]['BillCode']
        payment_url = f"https://toyyibpay.com/{bill_code}"
        return redirect(payment_url)

    return f"Error creating bill: {result}"

@app.route('/toyyibpay-webhook', methods=['POST'])
def webhook_handler():
    data = request.form.to_dict()
    print("Webhook received:", data)
    return "Webhook received OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
