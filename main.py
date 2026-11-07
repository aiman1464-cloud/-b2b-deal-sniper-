import os
import time
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# Token and Payment Configuration
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9278867399:AAEYJ20caO4-EsQC_nMUtgxocBuHZUozqV8")
PAYPAL_LINK = "https://www.paypal.com/ncp/payment/S4WAPDVFEC75Y"

# Top 50 AI Agents List for B2B Operations
TOP_50_AGENTS = [
    {"name": "Devin AI", "field": "تطوير وبرمجة كاملة (First AI Software Engineer)"},
    {"name": "AutoGPT", "field": "وكيل مهام ذاتية وتخطيط معقد"},
    {"name": "BabyAGI", "field": "إدارة وترتيب المهام الأوتوماتيكية"},
    {"name": "AgentGPT", "field": "وكيل متصفح وأبحاث مستقلة"},
    {"name": "CrewAI", "field": "إدارة فرق العمل المتعددة من الوكلاء"},
    {"name": "ChatDev", "field": "تطوير البرمجيات عبر فريق وهمي ذكي"},
    {"name": "MetaGPT", "field": "تحويل المتطلبات إلى مخططات وكود متكامل"},
    {"name": "LangChain Agents", "field": "ربط أدوات وسلاسل البيانات المعقدة"},
    {"name": "Fixie.ai", "field": "وكلاء محادثات الأعمال المباشرة"},
    {"name": "Adept ACT-1", "field": "أتمتة برامج الكومبيوتر والمجالات المكتبية"},
    {"name": "MultiOn", "field": "وكيل إجراء المعاملات وحجز التذاكر بالمتصفح"},
    {"name": "LlamaIndex Agents", "field": "استعلام وتحليل البيانات الضخمة"},
    {"name": "Zapier Central", "field": "أتمتة آلاف التطبيقات اليومية بذكاء"},
    {"name": "Cognosys", "field": "وكيل تنفيذ أبحاث السوق المعقدة"},
    {"name": "HyperWrite Personal Assistant", "field": "أتمتة الأعمال المكتبية والايميلات"},
    {"name": "Microsoft Copilot Studio", "field": "بناء وكلاء مخصصين للمؤسسات"},
    {"name": "OpenAI Custom GPTs", "field": "وكلاء مخصصون للمهام التفاعلية"},
    {"name": "Semantic Kernel Agents", "field": "وكلاء متكاملون لبيئات دوت نت وبايثون"},
    {"name": "Superagi", "field": "منصة إشراف وتطوير الوكلاء الذاتيين"},
    {"name": "AgentOps", "field": "مراقبة واختبار أداء وكلاء الذكاء الاصطناعي"},
    {"name": "Camel AI", "field": "محاكاة التفاعل والتفاوض بين وكيلين"},
    {"name": "Syllable AI", "field": "وكلاء الرعاية الصحية والجداول العيادية"},
    {"name": "FinGPT", "field": "تحليل الأسواق المالية والتداول الذكي"},
    {"name": "Phidata", "field": "بناء وكلاء مدعومين بنماذج الـ LLM مع قاعدة بيانات"},
    {"name": "Replicate Agent", "field": "تشغيل نماذج الذكاء الاصطناعي بالهواء"},
    {"name": "Taskweaver", "field": "وكيل مايكروسوفت لتخطيط وتحليل كود بايثون"},
    {"name": "Kore.ai", "field": "وكلاء خدمات العملاء في الشركات الكبرى"},
    {"name": "Yellow.ai", "field": "وكيل المحادثات والمبيعات الذكية 24/7"},
    {"name": "Sierra AI", "field": "خدمة العملاء عالية المستوى للماركات العالمية"},
    {"name": "Decagon", "field": "دعم فني وأتمتة شكاوى وتذاكر المستخدمين"},
    {"name": "Intercom Fin AI", "field": "حلال المشاكل التلقائي للعملاء"},
    {"name": "Lindy AI", "field": "سكرتير شخصي لإدارة المواعيد والبريد"},
    {"name": "Granola AI", "field": "مساعد الاجتماعات وتلخيص القرارات والتوصيات"},
    {"name": "Otter.ai Agent", "field": "تسجيل وتلخيص ومتابعة مهام الاجتماعات الحية"},
    {"name": "Fireflies.ai", "field": "تحليل مكالمات المبيعات والاجتماعات"},
    {"name": "Clay AI", "field": "إثراء واستخراج بيانات العملاء المحتملين (B2B Lead Generation)"},
    {"name": "Seamless.ai", "field": "صياد بيانات وأرقام متخذي القرار في الشركات"},
    {"name": "Apollo AI Agent", "field": "أتمتة حملات المبيعات والتواصل البارد (Cold Outreach)"},
    {"name": "Kasisto", "field": "وكيل الخدمات المصرفية والمالية"},
    {"name": "UiPath Autopilot", "field": "أتمتة العمليات المكررة في الشركات (RPA + AI)"},
    {"name": "Automation Anywhere Enterprise Agent", "field": "إدارة سير العمل المؤسسي"},
    {"name": "Glean AI", "field": "محرك البحث والوكيل الداخلي لمعلومات الشركة"},
    {"name": "Dust.tt", "field": "مساعد مخصص لفريق العمل الداخلي"},
    {"name": "Scribe AI", "field": "وكيل توثيق الأدلة والشروحات الخطوة بخطوة"},
    {"name": "Synthesia AI Agent", "field": "توليد فيديوهات التدريب والتقديم فورياً"},
    {"name": "HeyGen Interactive Avatar", "field": "وكيل فيديو تفاعلي يجيب على العملاء"},
    {"name": "Harvey AI", "field": "مساعد ووكيل القضايا والعقود القانونية"},
    {"name": "CoCounsel (Thomson Reuters)", "field": "صياد ومحلل المراجع والأحكام القانونية"},
    {"name": "Abacus.ai", "field": "أنظمة التنبؤ والتوصية الذكية للمتاجر"},
    {"name": "B2B Snipe Agent", "field": "وكيلك الحالي لرصد الفرص وتسهيل عمليات الدفع والتسويق"}
]

def send_telegram_message(chat_id, text):
    """إرسال رسالة نصية بسيطة عبر API تيليجرام"""
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
    """إرسال رسالة احترافية تحتوي على أزرار تفاعلية بروابط سداد مباشرة"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "💳 دفع عمولة / سداد صفقة", "url": PAYPAL_LINK}
            ],
            [
                {"text": "🔥 قائمة الـ 50 وكيل كاملة", "callback_data": "btn_agents"},
                {"text": "🏆 أسطورة الـ Top 10 وكلاء", "callback_data": "btn_top10"}
            ],
            [
                {"text": "📊 حالة المنظومة", "callback_data": "btn_status"},
                {"text": "📞 التواصل مع أئمن", "callback_data": "btn_contact"}
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
    """معالجة الضغط على الأزرار واستجابة فورية دون تأخير"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    try:
        requests.post(url, json={"callback_query_id": callback_query_id}, timeout=3)
    except Exception as e:
        print(f"Error answering callback: {e}")

    if data == "btn_agents":
        send_telegram_message(chat_id, "🤖 **[قائمة أفضل 50 وكيل ذكاء اصطناعي لتطوير الأعمال]**:\n\nجاري إرسال القائمة الكاملة...")
        
        msg1 = "🚀 **أفضل الوكلاء الذكاء الاصطناعي عالمياً (الجزء الأول):**\n\n"
        for idx, agent in enumerate(TOP_50_AGENTS[:25], 1):
            msg1 += f"{idx}. **{agent['name']}**: {agent['field']}\n"
        send_telegram_message(chat_id, msg1)

        msg2 = "📌 **بقية القائمة (الجزء الثاني من 26 إلى 50):**\n\n"
        for idx, agent in enumerate(TOP_50_AGENTS[25:], 26):
            msg2 += f"{idx}. **{agent['name']}**: {agent['field']}\n"
        send_telegram_message(chat_id, msg2)

    elif data == "btn_top10":
        msg = "🏆 **[قائمة النخبة - Top 10 AI Agents]**:\n\n"
        for idx, agent in enumerate(TOP_50_AGENTS[:10], 1):
            msg += f"✨ {idx}. **{agent['name']}**: {agent['field']}\n"
        send_telegram_with_buttons(chat_id, msg)

    elif data == "btn_status":
        text = "🟢 **المنظومة نشطة 100%** ومتصلة بالسيرفر ومجهزة بمحرك الصيد الصامت 24/7."
        send_telegram_with_buttons(chat_id, text)

    elif data == "btn_contact":
        text = "📩 **للتواصل المباشر مع أئمن:**\nأرسل رسالتك هنا وسيقوم أئمن بالرد عليك فوراً."
        send_telegram_with_buttons(chat_id, text)

@app.route('/', methods=['GET'])
def home():
    return "🟢 B2B Snipe Autonomous AI Engine is LIVE 24/7!", 200

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
                    f"🤖 **أهلاً بك يا أئمن في لوحة تحكم وكلاء العمل الذكية!**\n\n"
                    f"⚡ تم تفعيل مصفوفة أفضل 10 وكلاء نخبة + الـ 50 وكيل الكاملة لصيد وتطوير الأعمال أوتوماتيكياً.\n\n"
                    f"اختر من الأزرار بالأسفل لتنفيذ العمليات:"
                )
                send_telegram_with_buttons(chat_id, reply)

    except Exception as err:
        print(f"Webhook Exception: {err}")

    return jsonify({"status": "ok"}), 200

# ==========================================
# 🚀 محرك الصيد الآلي والتثبت المباشر (Live Real-World Engine)
# ==========================================
def auto_deal_worker():
    """محرك الاستعلام الصامت واستخراج البيانات الحية من الإنترنت بدون محاكاة وهمية"""
    time.sleep(15)
    
    while True:
        try:
            # استعلام حي ومباشر من واجهات بيانات البرمجة والفرص
            response = requests.get(
                "https://api.github.com/search/repositories?q=b2b+automation+or+freelance+topic:freelance&sort=updated&order=desc",
                headers={"User-Agent": "Mozilla/5.0"},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                items = data.get("items", [])
                
                if items:
                    top_item = items[0]
                    repo_name = top_item.get("full_name", "فرصة B2B حقيقية")
                    repo_url = top_item.get("html_url", PAYPAL_LINK)
                    description = top_item.get("description", "طلب مشروع أو خدمة حقيقية مرصودة عبر الويب.")

                    notification_text = (
                        f"🎯 **[رصد حي ومباشر من الإنترنت]**\n\n"
                        f"📦 **الفرصة المرصودة:** {repo_name}\n"
                        f"📝 **الوصف:** {description[:120]}...\n\n"
                        f"🌐 **رابط المصدر الحي:** {repo_url}\n\n"
                        f"⚡ **تحصيل العوائد مباشرة عبر PayPal:**\n{PAYPAL_LINK}"
                    )
                    
                    chat_id_target = os.environ.get("TELEGRAM_CHAT_ID", "129522237")
                    send_telegram_message(chat_id_target, notification_text)

        except Exception as auto_healing_error:
            print(f"Live Engine Auto-Recovery: {auto_healing_error}")
            time.sleep(10)
            
        # حلقة مسح دورية كل 30 دقيقة
        time.sleep(1800)

auto_thread = threading.Thread(target=auto_deal_worker, daemon=True)
auto_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
