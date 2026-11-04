import os
import time
import requests
import feedparser
from openai import OpenAI
from flask import Flask
from threading import Thread

# 1. Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PAYPAL_LINK = "https://www.paypal.com/ncp/payment/S4WAPDVFEC75Y"

client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

@app.route('/')
def home():
    return "Sovereign AI Enterprise System is LIVE and Active."

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def run_instant_test():
    """توليد تجربة حية فورية لرؤية تحليل الذكاء الاصطناعي ورابط بايبال"""
    print("Executing instant diagnostic test...")
    prompt = """
    أنت وكيل تحليل سيادي متقدم (Sovereign AI Analyst). 
    قم بإنشاء مثال حي وتكتيكي لصفقة/فرصة عمل رقمية عالية الربحية (B2B Arbitrage or High-Value Job).
    قدم التحليل بالشكل التالي:
    - 📌 عنوان الفرصة
    - 💡 التحليل التكتيكي وهامش الربح المتوقع
    - ⚡ خطة التنفيذ الذاتية
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=300
        )
        analysis = response.choices[0].message.content
        
        message = (
            "🚀 **[اختبار تشغيلي حي - إثبات كفاءة المنظومة]**\n\n"
            f"{analysis}\n\n"
            f"💳 **رابط تحصيل الأرباح المباشر:**\n{PAYPAL_LINK}\n\n"
            "STATUS: المنظومة تعمل الآن بكامل طاقتها وتراقب الأسواق 24/7."
        )
        send_telegram(message)
        print("Instant test sent to Telegram successfully.")
    except Exception as e:
        print(f"Test failed: {e}")

def monitor_loop():
    # تشغيل الاختبار الفوري مرة واحدة عند الإقلاع لرؤية النتيجة مباشرة
    time.sleep(5)
    run_instant_test()
    
    # الحلقة الدائمة للمراقبة
    seen_links = set()
    feed_urls = [
        "https://weworkremotely.com/remote-jobs.rss",
        "https://remoteok.com/index.xml"
    ]
    
    while True:
        for url in feed_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:3]:
                    if entry.link not in seen_links:
                        seen_links.add(entry.link)
                        
                        # تحليل الفرصة عبر GPT-4o-mini
                        ai_prompt = f"حلل الفرصة التالية باختصار واذكر كيف يمكن الاستفادة منها تجارياً:\nالعنوان: {entry.title}\nالرابط: {entry.link}"
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": ai_prompt}],
                            max_tokens=200
                        )
                        ai_analysis = res.choices[0].message.content
                        
                        alert = (
                            f"🎯 **فرصة جديدة مكتشفة!**\n\n"
                            f"**العنوان:** {entry.title}\n"
                            f"**الرابط:** {entry.link}\n\n"
                            f"📊 **تحليل الذكاء الاصطناعي:**\n{ai_analysis}\n\n"
                            f"💳 **رابط الإيداع والدفع:**\n{PAYPAL_LINK}"
                        )
                        send_telegram(alert)
            except Exception as e:
                print(f"Error in monitor loop: {e}")
        time.sleep(300)

if __name__ == "__main__":
    t = Thread(target=monitor_loop)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
