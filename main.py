from flask import Flask, request, redirect
import requests

app = Flask(__name__)

# Toyyibpay API Credentials
USER_SECRET_KEY = '70mpdq70-kub2-ly4b-ugdx-04wn4peurx10'
CATEGORY_CODE = '4sgntdmo'

ODOO_WEBHOOK_URL = 'https://edu-ecoshop1.odoo.com/payment/webhook'  # <-- (Optional) URL Odoo kalau nak sambung

@app.route('/pay')
def create_bill():
    order_id = request.args.get('order_id')
    amount = request.args.get('amount')  # contoh: 10.00

    if not order_id or not amount:
        return "Missing order_id or amount!"

    try:
        bill_amount = int(float(amount) * 100)  # Convert ke sen
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
        'billTo': f"Customer {order_id}",
        'billEmail': 'customer@example.com',
        'billPhone': '01112345678',
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
    print("🔔 Webhook received from Toyyibpay:", data)

    # Extract info penting
    billcode = data.get('billcode')
    payment_status = data.get('status')  # 1 = Paid, 2 = Unpaid, 3 = Pending
    pay_amount = data.get('amount')
    order_id = data.get('order_id')  # Optional, jika hantar dalam customField

    # Check kalau payment berjaya
    if payment_status == '1':
        print(f"✅ Payment SUCCESS for BillCode: {billcode}")
        
        # (Optional) Hantar ke Odoo Webhook kalau nak update order
        try:
            odoo_payload = {
                "billcode": billcode,
                "amount": pay_amount,
                "order_id": order_id,
                "payment_status": "paid"
            }
            odoo_response = requests.post(ODOO_WEBHOOK_URL, json=odoo_payload)
            print("📡 Odoo Response:", odoo_response.status_code, odoo_response.text)
        except Exception as e:
            print(f"Error sending to Odoo: {str(e)}")
    
    else:
        print(f"❌ Payment FAILED or UNPAID for BillCode: {billcode}")

    return "Webhook processed OK", 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=10000)
