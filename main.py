import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN", "9278867399:AAEYJ20caO4-EsQC_nMUtgxocBuHZUozqV8")
PAYPAL_LINK = "https://www.paypal.com/ncp/payment/S4WAPDVFEC75Y"

# قائمة أفضل 50 وكيل ذكاء اصطناعي لبيئة الأعمال (Top 50 AI Agents)
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
    {"name": "Clay AI", "field": "اثراء واستخراج بيانات العملاء المحتملين (B2B Lead Generation)"},
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
    """إرسال رسالة نصية بسيطة"""
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
    """إرسال رسالة احترافية تحتوي على أزرار تفاعلية"""
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    reply_markup = {
        "inline_keyboard": [
            [
                {"text": "💳 دفع عمولة / سداد صفقة", "url": PAYPAL_LINK}
            ],
            [
                {"text": "🔥 استعراض أفضل 50 وكيل عمل", "callback_data": "btn_agents"},
                {"text": "📊 حالة المنظومة", "callback_data": "btn_status"}
            ],
            [
                {"
