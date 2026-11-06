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
                {"text": "💳 دفع عمولة / سداد صفقة", "url": PAYPAL_LINK}
            ],
            [
                {"text": "🔍 فحص الويب والصفقات الحية", "callback_data": "btn_live_search"},
                {"text": "📊 حالة النظام", "callback_data": "btn_status"}
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

    if data == "btn_live_search":
        send_telegram_message(chat_id, "🔍 **جاري البحث الحي في مصادر الإنترنت وخوارزميات الويب...**")
        try:
            feed = feedparser.parse("https://news.ycombinator.com/rss")
            if feed.entries:
                msg = "🌐 **أحدث النتائج الحية المرصودة من الإنترنت:**\n\n"
                for entry in feed.entries[:3]:
                    msg += f"• [{entry.title}]({entry.link})\n\n"
                send_telegram_with_buttons(chat_id, msg)
            else:
                send_telegram_with_buttons(chat_id, "⚠️ لا توجد نتائج جديدة حالياً، جارٍ إعادة المحاولة تلقائياً.")
        except Exception as e:
            send_telegram_message(chat_id, f"❌ حدث خطأ أثناء جلب النتائج: {e}")

    elif data == "btn_status":
        send_telegram_with_buttons(chat_id, "🟢 **المحرك الحقيقي نشط 24/7** ويرصد الويب والصفقات تلقائياً بدون تدخل بشري.")

@app.route('/', methods=['GET'])
def home():
    return "🟢 Fully Autonomous Live Sniper Engine is LIVE!", 200

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
                reply = (
                    f"🤖 **محرك البحث الحي والصفقات الافتراضية نشط ومستقل!**\n\n"
                    f"⚡ البوت يعمل الآن في الخلفية لوحده ويرسل لك الفرص والنتائج أوتوماتيكياً."
                )
                send_telegram_with_buttons(chat_id, reply)
    except Exception as err:
        print(f"Webhook Exception: {err}")
    return jsonify({"status": "ok"}), 200

def autonomous_background_worker():
    """محرك خلفي مستقل تماماً يعمل 24/7 لجلب الفرص والنتائج الحية دون أسئلة"""
    time.sleep(20)
    while True:
        try:
            chat_id_target = os.environ.get("TELEGRAM_CHAT_ID", "129522237")
            feed = feedparser.parse("https://news.ycombinator.com/rss")
            if feed.entries:
                entry = feed.entries[0]
                notif = (
                    f"🎯 **[تقرير الصياد الذاتي - نتيجة حية جديدة]**\n\n"
                    f"📌 **العنوان:** {entry.title}\n"
                    f"🔗 **الرابط:** {entry.link}\n\n"
                    f"💳 **لتحصيل العوائد والأرباح:**\n{PAYPAL_LINK}"
                )
                send_telegram_message(chat_id_target, notif)
        except Exception as e:
            print(f"Autonomous Worker Error: {e}")
        
        # الانتظار والدورة التلقائية كل ساعة
        time.sleep(3600)

# تشغيل المحرك المستقل في الخلفية
threading.Thread(target=autonomous_background_worker, daemon=True).start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
