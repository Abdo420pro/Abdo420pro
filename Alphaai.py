import os
import openai
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from dotenv import load_dotenv

# تحميل المفاتيح من .env
load_dotenv()

# إعداد مفاتيح API
openai.api_key = os.getenv("OPENAI_API_KEY")
ALPHA_AI_KEY = os.getenv("ALPHA_AI_KEY")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# إعداد Flask
app = Flask(__name__)

# دالة لتحميل الكتاب
def load_book(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        book_text = file.read()
    return book_text

# دالة لتدريب النموذج على نصوص الكتاب
def train_model_on_book(book_text):
    # هنا يمكن إضافة منطق التدريب باستخدام النصوص التي تم تحميلها
    # على سبيل المثال، استخدام OpenAI API لتدريب النموذج بناءً على النصوص
    try:
        response = openai.Completion.create(
            engine="gpt-3.5-turbo",  # أو النموذج المناسب
            prompt=book_text,
            max_tokens=2000
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"حدث خطأ: {e}"

# إعداد Telegram bot
def start(update, context):
    update.message.reply_text('مرحبا! كيف يمكنني مساعدتك اليوم؟')

def handle_message(update, context):
    user_message = update.message.text
    # إرسال الرسالة إلى OpenAI API أو Alpha AI API
    response = generate_response(user_message)
    update.message.reply_text(response)

def generate_response(user_message):
    # مثال لإرسال رسالة إلى OpenAI GPT-4
    try:
        response = openai.Completion.create(
            engine="gpt-4",
            prompt=user_message,
            max_tokens=150
        )
        return response.choices[0].text.strip()
    except Exception as e:
        return f"حدث خطأ: {e}"

# إضافة الأوامر والمستمعين
def setup_bot():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

# نقطة الدخول لFlask
@app.route('/webhook', methods=['POST'])
def webhook():
    update = request.get_json()
    # التعامل مع رسالة Telegram من هنا
    return jsonify({"status": "ok"})

if __name__ == "__main__":
    setup_bot()
    app.run(debug=True, host='0.0.0.0', port=5000)
