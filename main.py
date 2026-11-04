import os
import time
import requests
import feedparser
import telebot
from openai import OpenAI
from flask import Flask, request, jsonify
import threading

# 1. تهيئة المفاتيح والبيئة للتشغيل السيادي المستقل
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_BOT_TOKEN)
ai_client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

# رابط بايبال الخاص بك المعتمد للاستقبال المالي
PAYPAL_PAYMENT_LINK = "https://www.paypal.com/ncp/payment/S4WAPDVFEC75Y"

# مصادر رصد الفرص والتغيرات (Arbitrage, Deals, Price Shifts)
GLOBAL_TARGET_SOURCES = [
    "https://www.slickdeals.net/newsearch.php?mode=popdeals&searchtech=gnu&f=rss",
    # أضف أي مصادر إضافية هنا لاستهداف أسواق ومجالات أخرى
]

seen_targets = set()

def analyze_opportunity_autonomously(title, description, link):
    """
    الوكيل الذكي للتحليل الفوري وتحديد كيفية استغلال الفرصة وتحويلها لدخل
    """
    prompt = f"""
    أنت العقل التنفيذي لمنظومة وكلاء ذكاء اصطناعي سيادية مستقلة.
    حلل الهدف التالي بدقة تامة:
    العنوان: {title}
    التفاصيل: {description}
    الرابط: {link}

    المطلوب:
    1. ما هي نوعية الفرصة أو التغير المالي (استغلال سعر، أرباح سريعة، أو صفقة)؟
    2. كيف يمكن تحويل هذه الفرصة إلى دخل حقيقي فوري؟

    أجب باختصار شديد ومباشر:
    - الأهمية والربحية: (عالية جداً / متوسطة)
    - التكتيك التنفيذي: (سطر واحد يوضح خطوة الاستغلال الآلي)
    """
    try:
        response = ai_client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=150
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return f"Analysis error: {e}"

def autonomous_sniper_engine():
    """
    محرك الصيد السيادي المستقل (يعمل 24/7 بدون تدخل بشري)
    """
    while True:
        try:
            print("🚀 المنظومة السيادية تمسح الأسواق والفرص بشكل آلي...")
            for source in GLOBAL_TARGET_SOURCES:
                feed = feedparser.parse(source)
                for entry in feed.entries[:5]:
                    target_id = entry.get("id", entry.link)
                    if target_id in seen_targets:
                        continue
                    seen_targets.add(target_id)
                    
                    title = entry.title
                    link = entry.link
                    description = entry.get("summary", "")
                    
                    tactical_report = analyze_opportunity_autonomously(title, description, link)
                    
                    # إرسال التنبيه مرفقاً برابط الدفع المباشر الخاص بك
                    alert_msg = (
                        f"🎯 **[Sovereign Autonomous System] هدف تم رصده!**\n\n"
                        f"📌 **الفرصة:** {title}\n"
                        f"🔗 **رابط الفرصة:** {link}\n\n"
                        f"📊 **التقرير التكتيكي:**\n{tactical_report}\n\n"
                        f"💳 **رابط الدفع الفوري (PayPal):**\n{PAYPAL_PAYMENT_LINK}"
                    )
                    if TELEGRAM_CHAT_ID:
                        bot.send_message(TELEGRAM_CHAT_ID, alert_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Error in autonomous engine loop: {e}")
        time.sleep(180) # فحص مستمر كل 3 دقائق

@app.route('/payment-incoming', methods=['POST'])
def payment_incoming():
    """
    بوابة استقبال الأموال فقط (دخول مالي بحت وأمان تام دون أي صلاحية سحب)
    """
    data = request.json or request.form.to_dict()
    amount = data.get('mc_gross', '0.00')
    currency = data.get('mc_currency', 'USD')
    payer = data.get('payer_email', 'External Client')
    
    msg = (
        f"💰 **تأكيد دخول أموال لحسابك!**\n\n"
        f"💵 المبلغ الوارد: {amount} {currency}\n"
        f"👤 المصدر: {payer}\n"
        f"🔒 (الحالة: تم إيداع الأموال بنجاح في حسابك - أمان كامل ودخول فقط)."
    )
    if TELEGRAM_CHAT_ID:
        bot.send_message(TELEGRAM_CHAT_ID, msg, parse_mode="Markdown")
    return jsonify({"status": "received"}), 200

@bot.message_handler(commands=['start', 'status'])
def send_status(message):
    bot.reply_to(message, "⚡ **المنظومة السيادية تعمل بكامل طاقتها الاستقلالية، ورابط بايبال مرتبط وجاهز.**")

if __name__ == "__main__":
    # تشغيل محرك الصيد في الخلفية المستقلة
    threading.Thread(target=autonomous_sniper_engine, daemon=True).start()
    
    # تشغيل سيرفر الويب على Render للعمل المستمر واستقبال إشعارات الدخول المالي
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
