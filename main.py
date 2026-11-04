import os
import time
import requests
import feedparser
from openai import OpenAI
from flask import Flask
from threading import Thread

# 1. التكوين الأساسي للسيادة والتشغيل
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
PAYPAL_LINK = "https://www.paypal.com/ncp/payment/S4WAPDVFEC75Y"

client = OpenAI(api_key=OPENAI_API_KEY)
app = Flask(__name__)

@app.route('/')
def home():
    return "Sovereign AI Enterprise Core System is LIVE and Fully Operational."

def send_telegram(text):
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload)
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def autonomous_enterprise_engine():
    """محرك المنظومة المستقل: رصد، تحليل بحت، وتنفيذ آلي"""
    print("Autonomous Enterprise Engine started...")
    
    # رسالة بدء تشغيل المنظومة كمنظمة مستقلة
    startup_msg = (
        "🏢 **[تشغيل منظومة الأعمال السيادية]**\n\n"
        "⚡ تم تفعيل فريق الوكلاء الذكيين بنجاح.\n"
        "🔍 الرصد المستمر للأسواق والفرص: **نشط (24/7)**\n"
        "📊 التحليل المالي والاستراتيجي: **جاهز**\n"
        "💳 تحصيل الأرباح الآلي: **مربوط**\n\n"
        f"🔗 رابط التحصيل المعتمد:\n{PAYPAL_LINK}"
    )
    send_telegram(startup_msg)

    seen_links = set()
    feed_urls = [
        "https://weworkremotely.com/remote-jobs.rss",
        "https://remoteok.com/index.xml"
    ]
    
    while True:
        for url in feed_urls:
            try:
                feed = feedparser.parse(url)
                for entry in feed.entries[:2]:
                    if entry.link not in seen_links:
                        seen_links.add(entry.link)
                        
                        # وكيل التحليل البحت (Analyst Agent)
                        ai_prompt = (
                            "أنت وكيل التحليل الاستراتيجي الأعلى في منظومة أعمال سيادية. "
                            "قم بتحليل الفرصة التالية تحليلاً بحتاً وصارماً:\n"
                            f"العنوان: {entry.title}\n"
                            f"الرابط: {entry.link}\n\n"
                            "حدد باختصار شديد:\n"
                            "1. قيمة الفرصة وهامش الربح.\n"
                            "2. خطوة التنفيذ الفورية."
                        )
                        
                        res = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": ai_prompt}],
                            max_tokens=250
                        )
                        analysis_result = res.choices[0].message.content
                        
                        # التقرير التنفيذي النهائي الموجه لك على تيليجرام
                        enterprise_report = (
                            "🎯 **[فرصة جديدة رصدتها المنظومة]**\n\n"
                            f"📌 **المشروع:** {entry.title}\n"
                            f"🔗 **الرابط:** {entry.link}\n\n"
                            f"📊 **تقرير التحليل البحت:**\n{analysis_result}\n\n"
                            f"💳 **بوابة تحصيل العوائد والأرباح:**\n{PAYPAL_LINK}"
                        )
                        send_telegram(enterprise_report)
                        
            except Exception as e:
                print(f"Error in enterprise loop: {e}")
                
        # فترة استراحة بين عمليات الفحص المتكررة للحفاظ على استقرار السيرفر
        time.sleep(300)

if __name__ == "__main__":
    t = Thread(target=autonomous_enterprise_engine)
    t.daemon = True
    t.start()
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
