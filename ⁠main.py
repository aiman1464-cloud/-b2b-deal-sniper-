import os
import time
import requests
import feedparser

# استدعاء المفاتيح من بيئة السيرفر
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")

# ذاكرة السيرفر لحفظ الفرص التي تم مسحها لمنع التكرار
SEEN_JOBS = set()

def send_telegram_alert(message):
    if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID,
            "text": message
        }
        try:
            requests.post(url, json=payload, timeout=10)
        except Exception as e:
            print(f"Error sending Telegram message: {e}")

def analyze_deal_with_openai(title, description):
    if not OPENAI_API_KEY:
        return f"🚨 فرصة جديدة:\n\nالعنوان: {title}\n\nالوصف:\n{description[:300]}..."
    
    url = "https://api.openai.com/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENAI_API_KEY}",
        "Content-Type": "application/json"
    }
    prompt = f"""
    أنت وكيل صيد مناقصات B2B احترافي. حلل المشروع التالي واكتب مقترح عرض فني مبسط:
    العنوان: {title}
    الوصف: {description}
    
    المطلوب:
    1. تقييم جدوى الفرصة (من 10).
    2. صياغة مسودة عرض احترافي وجذاب للعميل.
    """
    payload = {
        "model": "gpt-4o",
        "messages": [{"role": "user", "content": prompt}],
        "max_tokens": 500
    }
    try:
        response = requests.post(url, headers=headers, json=payload, timeout=15)
        res_data = response.json()
        analysis = res_data['choices'][0]['message']['content']
        return f"🎯 فرصة مستهدفة تم اقتناصها:\n\nالعنوان: {title}\n\nالتحليل والعرض الفني:\n{analysis}"
    except Exception as e:
        return f"🚨 فرصة جديدة: {title}\n(تعذر الاتصال بالذكاء الاصطناعي: {e})"

def scan_jobs():
    global SEEN_JOBS
    rss_url = "https://www.upwork.com/ab/feed/jobs/rss?q=python+developer"
    feed = feedparser.parse(rss_url)
    
    print("بدء مسح الفرص...")
    
    for entry in feed.entries[:3]:
        job_id = entry.get('id', entry.link)
        if job_id not in SEEN_JOBS:
            SEEN_JOBS.add(job_id
