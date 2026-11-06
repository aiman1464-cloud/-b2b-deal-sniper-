import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9278867399:AAEYJ20caO4-EsQC_nMUtgxocBuHZUozqV8")
PAYPAL_LINK = "https://www.paypal.com/ncp/payment/S4WAPDVFEC75Y"

def send_telegram(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error: {e}")

@app.route('/', methods=['GET'])
def home():
    return "🟢 Server is LIVE & Running!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        if data and "message" in data:
            message = data["message"]
            chat_id = message["chat"]["id"]
            user_text = message.get("text", "").strip()

            if user_text.startswith("/start"):
                reply = (
                    "🤖 **أهلاً بك يا أئمن!**\n\n"
                    "⚡ المنظومة نشطة وجاهزة 100% للعمل والتطوير.\n\n"
                    f"💳 **رابط تحصيل الأرباح PayPal:**\n{PAYPAL_LINK}"
                )
                send_telegram(chat_id, reply)
            else:
                send_telegram(chat_id, f"📥 تم استلام رسالتك: `{user_text}`\nجاري التطوير وإضافة ميزات جديدة...")
    except Exception as err:
        print(f"Webhook Error: {err}")

    return jsonify({"status": "ok"}), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
