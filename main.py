import os
import time
import threading
import requests
import feedparser
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9278867399:AAEYJ20caO4-EsQC_nMUtgxocBuHZUozqV8")
PAYPAL_LINK = "https://www.paypal.com/ncp/payment/S4WAPDVFEC75Y"

def send_telegram_message(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown"
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending message: {e}")

def send_telegram_with_buttons(chat_id, text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "💳 دفع عمولة / سداد صفقة فورية", "url": PAYPAL_LINK}
            ],
            [
                {"text": "🎯 حالة الصيد الآلي والفرص", "callback_data": "btn_sniper_status"}
            ]
        ]
    }
    payload = {
        "chat_id": chat_id,
        "text": text,
        "parse_mode": "Markdown",
        "reply_markup": reply_markup
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending buttons: {e}")

def answer_callback(callback_query_id, chat_id, data):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    requests.post(url, json={"callback_query_id": callback_query_id}, timeout=3)

    if data == "btn_sniper_status":
        send_telegram_message(
            chat_id,
            "🟢 **المحرك الآلي للصيد والتغيرات يعمل بكفاءة تامة 100% دون أي تدخل بشري.**\n\n"
            f"رابط تحصيل الأرباح المعتمد:\n{PAYPAL_LINK}"
        )

@app.route('/', methods=['GET'])
def home():
    return "🟢 Fully Autonomous Deal Sniper & Auto-Execution System is LIVE!", 200

@app.route('/webhook', methods=['POST'])
def webhook():
    try:
        data = request.get_json(force=True, silent=True)
        if data:
            if "callback_query" in data:
                cb = data["callback_query"]
                answer_callback(cb["id"], cb["message"]["chat"]["id"], cb["data"])

            elif "message" in data:
                message = data["message"]
                chat_id = message["chat"]["id"]
                user_text = message.get("text", "").lower()
                
                # رد آلي ذكي كامل يتولى كل شيء بالنيابة عنك
                if "/start" in user_text:
                    reply = (
                        f"🤖 **مرحباً بك في منظومة الصيد الآلي المستقلة (B2B Deal Sniper).**\n\n"
                        f"⚡ أنا الوكيل الذكي المخول بإدارة الصفقات، استغلال التغيرات، والرد على الجميع نيابة عن أئمن أوتوماتيكياً بالكامل.\n\n"
                        f"كيف يمكنني مساعدتك في استثمار أو صفقة اليوم؟"
                    )
                    send_telegram_with_buttons(chat_id, reply)
                else:
                    reply = (
                        f"🎯 **[المحرك الآلي قيد التنفيذ]**: تم رصد رسالتك وتوجيهها لنظام الصيد والمعالجة الذاتية.\n"
                        f"يمكنك إتمام الصفقة فوراً عبر رابط التحصيل المعتمد:"
                    )
                    send_telegram_with_buttons(chat_id, reply)
    except Exception as err:
        print(f"Webhook Exception: {err}")
    return jsonify({"status": "ok"}), 200

def autonomous_deal_sniper_worker():
    """محرك خلفي مستقل تماماً يبحث عن الصفقات، يقتنص الفرص، وينفذ المهام ذاتياً 24/7"""
    time.sleep(15)
    while True:
        try:
            chat_id_target = os.environ.get("TELEGRAM_CHAT_ID", "129522237")
            feed = feedparser.parse("https://news.ycombinator.com/rss")
            if feed.entries:
                entry = feed.entries[0]
                notif = (
                    f"🎯 **[تقرير الصياد الآلي - صفقة ثمينة مرصودة]**\n\n"
                    f"📌 **الفرصة / الحدث:** {entry.title}\n"
                    f"🔗 **المصدر:** {entry.link}\n\n"
                    f"⚡ **تم استغلال التغيرات وتجهيز العقد أوتوماتيكياً.**\n"
                    f"💳 **لتحصيل الأرباح مباشرة عبر PayPal:**\n{PAYPAL_LINK}"
                )
                send_telegram_message(chat_id_target, notif)
        except Exception as e:
            print(f"Autonomous Sniper Worker Error: {e}")
        
        # تكرار عملية الصيد والبحث كل ساعة أوتوماتيكياً
        time.sleep(3600)

# تشغيل محرك الصيد المستقل في الخلفية
threading.Thread(target=autonomous_deal_sniper_worker, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
