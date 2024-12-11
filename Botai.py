import os
import requests
import openai
from dotenv import load_dotenv  # إضافة هذا السطر
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
# تحميل المتغيرات من ملف .env
load_dotenv()
# إعداد المتغيرات
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')  # استخدام المتغيرات من .env
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')  # استخدام المتغيرات من .env
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')  # استخدام المتغيرات من .env
openai.api_key = OPENAI_API_KEY
# دالة لتوليد كود برمجي باستخدام ChatGPT
async def query_chatgpt(prompt: str) -> str:
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}]
    )
    return response.choices[0].message.content.strip()
# دالة لإنشاء ملف في GitHub
async def create_file_in_github(repo: str, path: str, content: str) -> str:
    url = f'https://api.github.com/repos/{repo}/contents/{path}'
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {
        'message': 'Creating a new file via Telegram bot',
        'content': content.encode('utf-8').decode('latin1'),
    }
    response = requests.put(url, json=data, headers=headers)
    return response.json()
# دالة لإعادة صياغة الطلب
def rephrase_request(request: str) -> str:
    return f"هل ترغب في إنشاء الكود التالي: {request}؟"
# دالة التعامل مع الأمر /createfile
async def create_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) < 4:
        await update.message.reply_text("يرجى إدخال التنسيق الصحيح: /createfile <repo> <filename> <format> <code>")
        return
    
    repo = context.args[0]
    filename = context.args[1]
    format_type = context.args[2]
    code = " ".join(context.args[3:])
    generated_code = await query_chatgpt(code)
    
    confirmation_message = rephrase_request(generated_code)
    keyboard = [
        [InlineKeyboardButton("نعم", callback_data='confirm'), InlineKeyboardButton("لا", callback_data='cancel')]
    ]
    await update.message.reply_text(confirmation_message, reply_markup=InlineKeyboardMarkup(keyboard))
    # حفظ البيانات في السياق
    context.user_data['repo'] = repo
    context.user_data['full_filename'] = f"{filename}.{format_type}"
    context.user_data['generated_code'] = generated_code
# الاستجابة لتأكيد المستخدم
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'confirm':
        repo = context.user_data['repo']
        full_filename = context.user_data['full_filename']
        generated_code = context.user_data['generated_code']
        
        response = await create_file_in_github(repo, full_filename, generated_code)
        
        if 'content' in response:
            await query.edit_message_text(f"تم إنشاء الملف بنجاح: {response['content']['html_url']}")
        else:
            await query.edit_message_text(f"حدث خطأ: {response}")
    elif query.data == 'cancel':
        await query.edit_message_text("تم إلغاء العملية.")
# إعداد البوت
async def main():
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    application.add_handler(CommandHandler("createfile", create_file))
    application.add_handler(CallbackQueryHandler(button_handler))
    await application.run_polling()
if _name_ == '_main_':
    import asyncio
    asyncio.run(main())
