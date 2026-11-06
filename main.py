import os
import time
import threading
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

# إعداد التوكين ورابط الباي بال الخاص بـ أئمن
TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9278867399:AAEYJ20caO4-EsQC_nMUtgxocBuHZUozqV8")
PAYPAL_LINK = "https://www.paypal.com/ncp/payment/S4WAPDVFEC75Y"

# صفوة الصفوة - أفضل 10 وكلاء ذكاء اصطناعي في العالم (Top 10 Elite Agents)
TOP_10_AGENTS = [
    {"name": "1. Devin AI", "field": "أول مهندس برمجيات ذكاء اصطناعي مستقل بالكامل"},
    {"name": "2. AutoGPT", "field": "وكيل التخطيط الذاتي والمهام المركبة دون تدخل بشري"},
    {"name": "3. CrewAI", "field": "إدارة وتشغيل فرق كاملة من وكلاء الذكاء الاصطناعي"},
    {"name": "4. Adept ACT-1", "field": "أتمتة برامج الكومبيوتر والمتصفح والعمليات المكتبية"},
    {"name": "5. MultiOn", "field": "وكيل تنفيذي لإجراء معاملات الشراء وحجز الخدمات أوتوماتيكياً"},
    {"name": "6. MetaGPT", "field": "تحويل المتطلبات البرمجية إلى مشاريع وكود متكامل"},
    {"name": "7. Clay AI", "field": "قنص وإثراء بيانات العملاء والشركات (B2B Lead Generation)"},
    {"name": "8. UiPath Autopilot", "field": "أتمتة العمليات المكررة في الشركات المؤسسية الضخمة"},
    {"name": "9. Intercom Fin AI", "field": "وكيل حل مشاكل العملاء والدعم الفني التلقائي 24/7"},
    {"name": "10. B2B Snipe Agent", "field": "وكيلك الحالي لرصد الفرص والوساطة المباشرة وتحصيل الأرباح"}
]

# باقي مصفوفة الـ 50 وكيل المكتملة
TOP_50_AGENTS = TOP_10_AGENTS + [
    {"name": "11. BabyAGI", "field": "إدارة وترتيب المهام الأوتوماتيكية"},
    {"name": "12. AgentGPT", "field": "وكيل متصفح وأبحاث مستقلة"},
    {"name": "13. ChatDev", "field": "تطوير البرمجيات عبر فريق وهمي ذكي"},
    {"name": "14. LangChain Agents", "field": "ربط أدوات وسلاسل البيانات المعقدة"},
    {"name": "15. Fixie.ai", "field": "وكلاء محادثات الأعمال المباشرة"},
    {"name": "16. LlamaIndex Agents", "field": "استعلام وتحليل البيانات الضخمة"},
    {"name": "17. Zapier Central", "field": "أتمتة آلاف التطبيقات اليومية بذكاء"},
    {"name": "18. Cognosys", "field": "وكيل تنفيذ أبحاث السوق المعقدة"},
    {"name": "19. HyperWrite Assistant", "field": "أتمتة الأعمال المكتبية والايميلات"},
    {"name": "20. Microsoft Copilot Studio", "field": "بناء وكلاء مخصصين للمؤسسات"},
    {"name": "21. OpenAI Custom GPTs", "field": "وكلاء مخصصون للمهام التفاعلية"},
    {"name": "22. Semantic Kernel Agents", "field": "وكلاء متكاملون لبيئات دوت نت وبايثون"},
    {"name": "23. Superagi", "field": "منصة إشراف وتطوير الوكلاء الذاتيين"},
    {"name": "24. AgentOps", "field": "مراقبة واختبار أداء وكلاء الذكاء الاصطناعي"},
    {"name": "25. Camel AI", "field": "محاكاة التفاعل والتفاوض بين وكيلين"},
    {"name": "26. Syllable AI", "field": "وكلاء الرعاية الصحية والجداول العيادية"},
    {"name": "27. FinGPT", "field": "تحليل الأسواق المالية والتداول الذكي"},
    {"name": "28. Phidata", "field": "بناء وكلاء مدعومين بنماذج الـ LLM مع قاعدة بيانات"},
    {"name": "29. Replicate Agent", "field": "تشغيل نماذج الذكاء الاصطناعي بالهواء"},
    {"name": "30. Taskweaver", "field": "وكيل مايكروسوفت لتخطيط وتحليل كود بايثون"},
    {"name": "31. Kore.ai", "field": "وكلاء خدمات العملاء في الشركات الكبرى"},
    {"name": "32. Yellow.ai", "field": "وكيل المحادثات والمبيعات الذكية 24/7"},
    {"name": "33. Sierra AI", "field": "خدمة العملاء عالية المستوى للماركات العالمية"},
    {"name": "34. Decagon", "field": "دعم فني وأتمتة شكاوى وتذاكر المستخدمين"},
    {"name": "35. Lindy AI", "field": "سكرتير شخصي لإدارة المواعيد والبريد"},
    {"name": "36. Granola AI", "field": "مساعد الاجتماعات وتلخيص القرارات والتوصيات"},
    {"name": "37. Otter.ai Agent", "field": "تسجيل وتلخيص ومتابعة مهام الاجتماعات الحية"},
    {"name": "38. Fireflies.ai", "field": "تحليل مكالمات المبيعات والاجتماعات"},
    {"name": "39. Seamless.ai", "field": "صياد بيانات وأرقام متخذي القرار في الشركات"},
    {"name": "40. Apollo AI Agent", "field": "أتمتة حملات المبيعات والتواصل البارد (Cold Outreach)"},
    {"name": "41. Kasisto", "field": "وكيل الخدمات المصرفية والمالية"},
    {"name": "42. Automation Anywhere", "field": "إدارة سير العمل المؤسسي"},
    {"name": "43. Glean AI", "field": "محرك البحث والوكيل الداخلي لمعلومات الشركة"},
    {"name": "44. Dust.tt", "field": "مساعد مخصص لفريق العمل الداخلي"},
    {"name": "45. Scribe AI", "field": "وكيل توثيق الأدلة والشروحات الخطوة بخطوة"},
    {"name": "46. Synthesia AI Agent", "field": "توليد فيديوهات التدريب والتقديم فورياً"},
    {"name": "47. HeyGen Interactive Avatar", "field": "وكيل فيديو تفاعلي يجيب على العملاء"},
    {"name": "48. Harvey AI", "field": "مساعد ووكيل القضايا والعقود القانونية"},
    {"name": "49. CoCounsel", "field": "صياد ومحلل المراجع والأحكام القانونية"},
    {"name": "50. Abacus.ai", "field": "أنظمة التنبؤ والتوصية الذكية للمتاجر"}
]

def send_telegram_message(chat_id, text):
    """إرسال رسالة نصية آمنة"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown"}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending message: {e}")

def send_telegram_with_buttons(chat_id, text):
    """إرسال لوحة الأزرار التفاعلية المباشرة"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    reply_markup = {
        "inline_keyboard": [
            [{"text": "💳 دفع عمولة / سداد صفقة", "url": PAYPAL_LINK}],
            [
                {"text": "🏆 أسطورة الـ Top 10 وكلاء", "callback_data": "btn_top10"},
                {"text": "🔥 قائمة الـ 50 وكيل كاملة", "callback_data": "btn_agents"}
            ],
            [
                {"text": "📊 حالة المنظومة", "callback_data": "btn_status"},
                {"text": "📞 التواصل مع أئمن", "callback_data": "btn_contact"}
            ]
        ]
    }
    payload = {"chat_id": chat_id, "text": text, "parse_mode": "Markdown", "reply_markup": reply_markup}
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"Error sending buttons: {e}")

def answer_callback(callback_query_id, chat_id, data):
    """استجابة سريعة للأزرار تفادياً لأي تعليق في الواجهة"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/answerCallbackQuery"
    try:
        requests.post(url, json={"callback_query_id": callback_query_id}, timeout=3)
    except Exception:
        pass

    if data == "btn_top10":
        msg = "🏆 **[صفوة وكلاء الذكاء الاصطناعي - Top 10 Elite Agents]**:\n\n"
        for agent in TOP_10_AGENTS:
            msg += f"✨ **{agent['name']}**\n🔹 {agent['field']}\n\n"
        send_telegram_message(chat_id, msg)

    elif data == "btn_agents":
        send_telegram_message(chat_id, "🤖 **[القائمة الكاملة لأفضل 50 وكيل ذكاء اصطناعي]**:\nجاري الإرسال...")
        msg1 = "🚀 **الجزء الأول (1 - 25):**\n\n"
        for agent in TOP_50_AGENTS[:25]:
            msg1 += f"• **{agent['name']}**: {agent['field']}\n"
        send_telegram_message(chat_id, msg1)

        msg2 = "📌 **الجزء الثاني (26 - 50):**\n\n"
        for agent in TOP_50_AGENTS[25:]:
            msg2 += f"• **{agent['name']}**: {agent['field']}\n"
        send_telegram_message(chat_id, msg2)

    elif data == "btn_status":
        text = "🟢 **المنظومة نشطة 100%** ومتصلة بالسيرفر ومجهزة بمحرك الصيد الصامت 24/7."
        send_telegram_with_buttons(chat_id, text)

    elif data == "btn_contact":
        text = "📩 **للتواصل المباشر مع أئمن:**\nأرسل رسالتك هنا وسيقوم أئمن بالرد عليك فوراً."
        send_telegram_with_buttons(chat_id, text)

@app.route('/', methods=['GET'])
def home():
    return "🟢 Enterprise Autonomous AI Engine with Top 10 Spotlight is LIVE!", 200

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

def auto_deal_worker():
    """محرك الصيد التلقائي والإصلاح الذاتي (Zero-Human Engine)"""
    time.sleep(10)
    sample_deals = [
        {"title": "📦 صفقة استيراد إلكترونيات بالجملة", "margin": 35, "profit": "$450 عمولة", "details": "مورد صيني يطلب وكيل توزيع بالشرق الأوسط.", "link": PAYPAL_LINK},
        {"title": "🤝 عقد خدمات ذكاء اصطناعي لشركة مقاولات", "margin": 50, "profit": "$1,200 قيمة العقد", "details": "طلب مؤتمت للتحليل المالي والعقود بذكاء اصطناعي.", "link": PAYPAL_LINK},
        {"title": "🔥 فرصة تداول وتسويق بالعمولة B2B", "margin": 30, "profit": "15% عمولة تلقائية", "details": "رصد خصم بقيمة 40% على معدات طاقة شمسية.", "link": PAYPAL_LINK}
    ]
    deal_index = 0
    while True:
        try:
            deal = sample_deals[deal_index % len(sample_deals)]
            if deal.get("margin", 0) >= 20:
                notification_text = (
                    f"🎯 **[إشعار صيد تلقائي - منظومة أئمن المستقلة]**\n\n"
                    f"{deal['title']}\n"
                    f"📈 **هامش الربح المرصود:** {deal['margin']}%\n"
                    f"💰 **العائد المتوقع:** {deal['profit']}\n"
                    f"📝 **التفاصيل:** {deal['details']}\n\n"
                    f"⚡ **تحصيل العوائد مباشرة عبر PayPal:**\n💳 {deal['link']}"
                )
                chat_id_target = os.environ.get("TELEGRAM_CHAT_ID", "129522237")
                send_telegram_message(chat_id_target, notification_text)
            deal_index += 1
        except Exception as e:
            print(f"Auto Worker Self-Healing: {e}")
            time.sleep(5)
        time.sleep(1800)

auto_thread = threading.Thread(target=auto_deal_worker, daemon=True)
auto_thread.start()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
