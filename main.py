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
MIN_SCORE = int(os.environ.get("MIN_SCORE", "7"))
CHECK_EVERY_MIN = int(os.environ.get("CHECK_EVERY_MIN", "30"))
MAX_PER_CYCLE = int(os.environ.get("MAX_PER_CYCLE", "12"))

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
FEEDS += [
    "https://hackerone.com/hacktivity.rss",
    "https://www.bugcrowd.com/crowdstream/feed/",
    "https://infosec-jobs.com/feed/",
    "https://www.reddit.com/r/bugbounty/new/.rss",
    "https://www.reddit.com/r/netsecjobs/new/.rss",
    "https://remotive.com/remote-jobs/feed",
    "https://himalayas.app/jobs/rss",
]
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
        print("Telegram غير مضبوط")
        return
    try:
        requests.post(
            f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage",
            data={
                "chat_id": TELEGRAM_CHAT_ID,
                "text": text[:4000],
                "disable_web_page_preview": "false"
            },
            timeout=20,
        )
    except Exception:
        print("Telegram error")


def analyze(title, summary, link):
    if not client:
        return None
    content = f"العنوان: {title}\nالملخص: {summary[:700]}\nالرابط: {link}"
    try:
        r = client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": content},
            ],
            response_format={"type": "json_object"},
            temperature=0.2,
        )
        return json.loads(r.choices[0].message.content)
    except Exception:
        return None


def fetch_new_items(seen):
    items = []
    for url in FEEDS:
        try:
            feed = feedparser.parse(url, agent="Mozilla/5.0 OpportunityBot")
            for e in feed.entries[:10]:
                key = e.get("id") or e.get("link") or e.get("title")
                if not key or key in seen:
                    continue
                items.append({
                    "key": key,
                    "title": e.get("title", ""),
                    "summary": e.get("summary", ""),
                    "link": e.get("link", ""),
                })
        except Exception:
            pass
    return items


def run_cycle(seen):
    items = fetch_new_items(seen)
    print(f"عناصر جديدة: {len(items)}")
    for item in items[:MAX_PER_CYCLE]:
        seen.add(item["key"])
        result = analyze(item["title"], item["summary"], item["link"])
        if not result:
            continue
        try:
            score = int(result.get("score", 0))
        except Exception:
            score = 0
        if score >= MIN_SCORE:
            msg = (
                f"🎯 فرصة {score}/10 - {result.get('type', '')}\n\n"
                f"{item['title']}\n\n"
                f"💡 {result.get('why', '')}\n"
                f"👉 {result.get('action', '')}\n\n"
                f"{item['link']}"
            )
            send_telegram(msg)
    for item in items[MAX_PER_CYCLE:]:
        seen.add(item["key"])
    save_seen(seen)


def main():
    threading.Thread(target=run_server, daemon=True).start()
    send_telegram("✅ بوت الفرص اشتغل وبدأ المسح.")
    seen = load_seen()
    while True:
        try:
            run_cycle(seen)
        except Exception as e:
            print("Cycle error:", e)
        time.sleep(CHECK_EVERY_MIN * 60)


if __name__ == "__main__":
    main()
