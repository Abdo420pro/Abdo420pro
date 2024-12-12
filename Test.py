import telebot
import openai
from github import Github
from dotenv import load_dotenv
import os
import json
import re

# تحميل المتغيرات البيئية
load_dotenv()

# إعدادات الاتصال
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# تهيئة الخدمات
bot = telebot.TeleBot(TELEGRAM_TOKEN)
github_client = Github(GITHUB_TOKEN)
openai.api_key = OPENAI_API_KEY

# قاموس الذكاء المعرفي
KNOWLEDGE_BASE = {
    "project_types": [
        "web_application", 
        "mobile_app", 
        "machine_learning", 
        "data_analysis", 
        "automation_script"
    ],
    "programming_languages": [
        "python", "javascript", "typescript", 
        "java", "kotlin", "swift", "rust"
    ]
}

class IntelligentProjectManager:
    def __init__(self, chat_id):
        self.chat_id = chat_id
        self.context = {
            "current_stage": "initial",
            "project_details": {},
            "conversation_history": []
        }

    def generate_intelligent_response(self, user_message):
        """توليد استجابة ذكية باستخدام سياق المحادثة"""
        try:
            # دمج التعلم اللغوي والمنطقي
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": """
                    أنت مساعد ذكي متخصص في إدارة المشاريع البرمجية. 
                    تحلل السياق بذكاء، وتقدم اقتراحات منطقية وعملية.
                    """},
                    *self.context["conversation_history"],
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            return f"خطأ في معالجة الاستجابة: {str(e)}"

    def analyze_project_intent(self, message):
        """تحليل نية المستخدم بذكاء"""
        intent_prompt = f"""
        حلل النص التالي واستخرج نية المشروع المحتملة:
        {message}

        أرجع استجابة JSON بالتفاصيل التالية:
        {{
            "project_type": "نوع المشروع",
            "primary_language": "اللغة البرمجية الرئيسية",
            "complexity_level": "مستوى التعقيد (بسيط/متوسط/معقد)",
            "potential_modules": ["قائمة الوحدات المحتملة"]
        }}
        """
        
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "أنت محلل نوايا المشاريع البرمجية الذكي"},
                    {"role": "user", "content": intent_prompt}
                ]
            )
            
            # استخراج JSON من الاستجابة
            json_match = re.search(r'\{.*\}', response.choices[0].message.content, re.DOTALL)
            if json_match:
                return json.loads(json_match.group(0))
            return None
        except Exception as e:
            print(f"خطأ في تحليل النية: {e}")
            return None

    def generate_project_blueprint(self, project_details):
        """إنشاء مخطط المشروع الذكي"""
        blueprint_prompt = f"""
        قم بإنشاء مخطط مفصل للمشروع بناءً على المعلومات التالية:
        {json.dumps(project_details, indent=2)}

        أرجع هيكل مشروع كامل يتضمن:
        1. هيكل المجلدات
        2. الملفات الأساسية
        3. الوصف التقني
        4. اعتبارات التنفيذ
        """
        
        blueprint = self.generate_intelligent_response(blueprint_prompt)
        return blueprint

    def create_github_project(self, project_details):
        """إنشاء مشروع على GitHub بذكاء"""
        try:
            # اختيار اسم المستودع بذكاء
            repo_name = f"{project_details.get('project_type', 'ai_project')}_{os.urandom(4).hex()}"
            
            # إنشاء المستودع
            repo = github_client.get_user().create_repo(
                repo_name, 
                description=f"مشروع {project_details.get('project_type', 'برمجي')}",
                private=True  # خاص افتراضياً
            )
            
            return repo
        except Exception as e:
            print(f"خطأ في إنشاء المستودع: {e}")
            return None

# وحدة معالجة الرسائل الرئيسية
project_managers = {}

@bot.message_handler(commands=['start'])
def start_command(message):
    chat_id = message.chat.id
    project_managers[chat_id] = IntelligentProjectManager(chat_id)
    
    bot.reply_to(message, """
    مرحبًا بك في مساعد المشاريع الذكي! 🚀
    
    يمكنني مساعدتك في:
    • تحليل فكرة مشروعك
    • إنشاء مخططات برمجية
    • توليد كود أولي
    • إدارة مستودعات GitHub
    
    هل لديك فكرة مشروع تريد تطويرها؟
    """)

@bot.message_handler(func=lambda message: True)
def handle_message(message):
    chat_id = message.chat.id
    
    if chat_id not in project_managers:
        project_managers[chat_id] = IntelligentProjectManager(chat_id)
    
    manager = project_managers[chat_id]
    
    # تحليل نية المشروع
    project_intent = manager.analyze_project_intent(message.text)
    
    if project_intent:
        # عرض تفاصيل المشروع المقترحة
        confirmation_message = f"""
        🤔 يبدو أن مشروعك يتضمن:
        • النوع: {project_intent['project_type']}
        • اللغة الرئيسية: {project_intent['primary_language']}
        • مستوى التعقيد: {project_intent['complexity_level']}
        • الوحدات المحتملة: {', '.join(project_intent['potential_modules'])}
        
        هل توافق على هذا التحليل؟ (نعم/لا)
        """
        
        bot.reply_to(message, confirmation_message)
        
        # تحديث سياق المحادثة
        manager.context['project_details'] = project_intent
        manager.context['current_stage'] = 'confirmation'
    else:
        bot.reply_to(message, "عذراً، لم أتمكن من فهم تفاصيل المشروع بشكل دقيق.")

# تشغيل البوت
bot.polling(none_stop=True)
