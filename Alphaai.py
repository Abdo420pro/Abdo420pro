import logging
import requests
from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import schedule
import time
from datetime import datetime
from dotenv import load_dotenv
import os

# تحميل المتغيرات البيئية من ملف .env
load_dotenv()

# إعداد سجل الأخطاء
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

# قراءة المتغيرات من ملف .env
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
CLAUDE_API_KEY = os.getenv('CLAUDE_API_KEY')
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
DEFAULT_MODEL = os.getenv('DEFAULT_MODEL', 'ChatGPT')

# دوال النماذج الذكية
def send_to_model(query: str, model: str) -> str:
    """إرسال استفسار إلى النموذج المختار"""
    try:
        if model == "ChatGPT":
            response = requests.post(
                "https://api.openai.com/v1/completions",
                headers={"Authorization": f"Bearer {OPENAI_API_KEY}"},
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 300
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json()['choices'][0]['message']['content']
        elif model == "ClaudeAI":
            response = requests.post(
                "https://api.anthropic.com/v1/messages",
                headers={
                    "x-api-key": CLAUDE_API_KEY,
                    "Content-Type": "application/json"
                },
                json={
                    "model": "claude-2",
                    "messages": [{"role": "user", "content": query}],
                    "max_tokens": 300
                },
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("content", "استجابة غير متوقعة من ClaudeAI")
        elif model == "Gemini":
            response = requests.post(
                "https://api.gemini.ai/endpoint",
                headers={"Authorization": f"Bearer {GEMINI_API_KEY}"},
                json={"query": query},
                timeout=10
            )
            response.raise_for_status()
            return response.json().get("result", "استجابة غير متوقعة من Gemini")
        else:
            return "النموذج المحدد غير مدعوم"
    except requests.exceptions.Timeout:
        return "انتهت مهلة الاتصال بالخادم. يرجى المحاولة لاحقًا."
    except requests.exceptions.RequestException as e:
        return f"خطأ أثناء الاتصال: {str(e)}"

# بوت Telegram
def start(update: Update, context: CallbackContext) -> None:
    """أمر بدء المحادثة مع البوت"""
    update.message.reply_text('مرحبًا! كيف يمكنني مساعدتك اليوم؟')

def select_model(update: Update, context: CallbackContext) -> None:
    """اختيار النموذج للتفاعل معه"""
    model = ' '.join(context.args) or DEFAULT_MODEL
    update.message.reply_text(f'تم اختيار النموذج: {model}')

def ask_model(update: Update, context: CallbackContext) -> None:
    """إرسال استفسار إلى النموذج المختار"""
    query = ' '.join(context.args)
    model = DEFAULT_MODEL
    if len(context.args) > 1:
        model = context.args[0]  # تحديد النموذج من المدخلات
        query = ' '.join(context.args[1:])
    response = send_to_model(query, model)
    update.message.reply_text(response)

# دوال الجدولة
def schedule_training():
    """جدولة تدريبات دورية للنماذج"""
    schedule.every().day.at("10:00").do(train_models)
    while True:
        schedule.run_pending()
        time.sleep(1)

def train_models():
    """دالة تدريب النماذج الذكية"""
    print("تدريب النماذج...")

# الإعداد الأساسي للبوت
def main():
    """الإعداد الأساسي للبوت"""
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # إضافة الأوامر للبوت
    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(CommandHandler("select", select_model))
    dispatcher.add_handler(CommandHandler("ask", ask_model))

    # بدء البوت
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
