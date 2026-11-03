import os
import json
import time
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler

import feedparser
import requests
from openai import OpenAI

# ====== الإعدادات (تُضاف في Render > Environment) ======
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID", "")
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
OPENAI_MODEL = os.environ.get("OPENAI_MODEL", "gpt-4o-mini")
MIN_SCORE = int(os.environ.get("MIN_SCORE", "7"))          # أقل تقييم يُرسل لك
CHECK_EVERY_MIN = int(os.environ.get("CHECK_EVERY_MIN", "30"))
MAX_PER_CYCLE = int(os.environ.get("MAX_PER_CYCLE", "12"))  # حد التحليل كل دورة (يوفر المال)

# ====== المصادر: فرص، وظائف، مشاريع، أفكار، مشاكل ======
FEEDS = [
    "https://hnrss.org/newest?points=60",
    "https://hnrss.org/whoishiring/jobs",
    "https://www.producthunt.com/feed",
    "https://techcrunch.com/feed/",
    "https://weworkremotely.com/remote-jobs.rss",
    "https://remoteok.com/remote-jobs.rss",
    "https://www.reddit.com/r/forhire/new/.rss",
    "https://www.reddit.com/r/SideProject/new/.rss",
    "https://www.reddit.com/r/startups/new/.rss",
    "https://www.reddit.com/r/Entrepreneur/new/.rss",
    "https://www.reddit.com/r/SaaS/new/.rss",
]
# مصادر حسب التخصص: ذكاء اصطناعي، برمجة، هندسة، عمل حر، أتمتة
FEEDS += [
    "http://export.arxiv.org/rss/cs.AI",
    "https://hnrss.org/show",
    "https://dev.to/feed",
    "https://lobste.rs/rss",
    "https://www.reddit.com/r/MachineLearning/new/.rss",
    "https://www.reddit.com/r/LocalLLaMA/new/.rss",
    "https://www.reddit.com/r/artificial/new/.rss",
    "https://www.reddit.com/r/programming/new/.rss",
    "https://www.reddit.com/r/freelance/new/.rss",
    "https://www.reddit.com/r/slavelabour/new/.rss",
    "https://www.reddit.com/r/microsaas/new/.rss",
    "https://www.reddit.com/r/automation/new/.rss",
    "https://www.reddit.com/r/engineering/new/.rss",
    "https://www.reddit.com/r/webdev/new/.rss",
]
# مصادر Bug Bounty رسمية (تقارير وثغرات معلنة قانونياً) + صفحات توظيف عامة
FEEDS += [
    "https://hackerone.com/hacktivity.rss",
    "https://www.bugcrowd.com/crowdstream/feed/",
    "https://infosec-jobs.com/feed/",
    "https://www.reddit.com/r/bugbounty/new/.rss",
    "https://www.reddit.com/r/netsecjobs/new/.rss",
    "https://remotive.com/remote-jobs/feed",
    "https://himalayas.app/jobs/rss",
]
# مصادر إضافية (مناقصات، منح، الخ) افصل بينها بفاصلة في متغير EXTRA_FEEDS
FEEDS += [u.strip() for u in os.environ.get("EXTRA_FEEDS", "").split(",") if u.strip()]

SEEN_FILE = "seen.json"
client = OpenAI(api_key=OPENAI_API_KEY) if OPENAI_API_KEY else None

SYSTEM_PROMPT = (
    "أنت مستشار فرص ذكي. تقيّم منشورات من الإنترنت وتبحث عن: "
    "فرص دخل، مشاكل حقيقية يمكن حلها بمنتج أو خدمة، شراكات في الذكاء الاصطناعي، "
    "وظائف أو عمل حر عن بعد، مناقصات ومنح، وثغرات سوق صغيرة يمكن استغلالها. "
    "في أي تخصص (برمجة، هندسة، أتمتة، تصميم، ذكاء اصطناعي، تسويق، غيرها). "
    "يشمل برامج Bug Bounty الرسمية المعلنة (HackerOne, Bugcrowd) وصفحات توظيف عامة فقط، "
    "ولا تقترح أبداً أي اختراق أو وصول غير مصرّح به. "
    "فكّر كمهندس وقناص: ما أسرع طريقة لبناء حل بسيط وبيعه أو التقديم قبل غيري؟ "
    "ردّ بـ JSON فقط بهذه المفاتيح: "
    "score (رقم 1 إلى 10)، type (نوع الفرصة بكلمتين)، "
    "why (سبب بسطر واحد بالعربي)، action (أول خطوة عملية بسطر واحد بالعربي). "
    "كن صارماً: أعطِ 7 فأكثر فقط للفرص الحقيقية والقابلة للتنفيذ."
)


# ====== سيرفر صغير ليبقى Render شغالاً ======
class SimpleHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"Bot is alive!")

    def do_HEAD(self):
        self.send_response(200)
        self.end_headers()

    def log_message(self, format, *args):
        pass


def run_server():
    port = int(os.environ.get("PORT", 10000))
    server = HTTPServer(("0.0.0.0", port), SimpleHandler)
    server.serve_forever()


# ====== أدوات ======
def load_seen():
    try:
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    except Exception:
        return set()


def save_seen(seen):
    try:
        with open(SEEN_FILE, "w") as f:
            json.dump(list(seen)[-5000:], f)
    except Exception:
        pass


def send_telegram(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        print("Telegram
