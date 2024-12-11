import os
import base64
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import requests
# تحميل المتغيرات من ملف .env
load_dotenv()
GITHUB_TOKEN = os.getenv('GITHUB_TOKEN')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
GITHUB_USERNAME = os.getenv('GITHUB_USERNAME')
GITHUB_API_URL = 'https://api.github.com'
COMMANDS = {
    "create_repo": "أنشئ مستودعًا باسم",
    "delete_repo": "احذف المستودع",
    "create_file": "أنشئ ملف",
    "create_codespace": "أنشئ كود سبيس باسم",
    "delete_codespace": "احذف كود سبيس",
    "list_codespaces": "اعرض كود سبيس",
}
def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('مرحبًا! أنا بوت لإدارة مستودعات GitHub و Codespaces. يمكنك إعطائي أوامر لأقوم بتنفيذها.\n\nمثال: "أنشئ مستودعًا باسم [اسم المستودع]"')
def handle_message(update: Update, context: CallbackContext) -> None:
    user_message = update.message.text.lower()
    
    if COMMANDS["create_repo"] in user_message:
        repo_name = user_message.split(COMMANDS["create_repo"])[-1].strip().replace(" ", "")
        create_repository(update, repo_name)
    elif COMMANDS["delete_repo"] in user_message:
        repo_name = user_message.split(COMMANDS["delete_repo"])[-1].strip().replace(" ", "")
        delete_repository(update, repo_name)
    elif COMMANDS["create_file"] in user_message:
        file_request = get_file_request(user_message)
        create_file(update, file_request)
    elif COMMANDS["create_codespace"] in user_message:
        codespace_name = user_message.split(COMMANDS["create_codespace"])[-1].strip().replace(" ", "")
        create_codespace(update, codespace_name)
    elif COMMANDS["delete_codespace"] in user_message:
        codespace_name = user_message.split(COMMANDS["delete_codespace"])[-1].strip().replace(" ", "")
        delete_codespace(update, codespace_name)
    elif COMMANDS["list_codespaces"] in user_message:
        list_codespaces(update)
    else:
        update.message.reply_text('عذرًا، لم أفهم الطلب. يُرجى المحاولة مجددًا.')
# إدارة المستودعات
def create_repository(update: Update, repo_name: str) -> None:
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    data = {'name': repo_name}
    response = requests.post(f'{GITHUB_API_URL}/user/repos', headers=headers, json=data)
    
    if response.status_code == 201:
        update.message.reply_text(f'تم إنشاء المستودع "{repo_name}" بنجاح!')
    else:
        update.message.reply_text(f'فشل في إنشاء المستودع: {response.json().get("message")}')
def delete_repository(update: Update, repo_name: str) -> None:
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.delete(f'{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}', headers=headers)
    
    if response.status_code == 204:
        update.message.reply_text(f'تم حذف المستودع "{repo_name}" بنجاح!')
    else:
        update.message.reply_text(f'فشل في حذف المستودع: {response.json().get("message")}')
def get_file_request(message: str):
    parts = message.split("أنشئ ملف")
    filename = parts[1].split("في المستودع")[-1].strip().split(" ")[0]  # الحصول على اسم الملف
    repo_name = parts[1].split("في المستودع")[-1].split(" ")[-1]  # الحصول على اسم المستودع
    return filename, repo_name
def create_file(update: Update, file_request: tuple) -> None:
    filename, repo_name = file_request
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    content = "print('Hello, World!')"  # محتويات الملف (يمكن تعديلها حسب الحاجة)
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')  # تشفير المحتوى
    data = {
        "message": f"إضافة الملف {filename}",
        "content": encoded_content,
        "branch": "main"  # تأكد من استخدام فرع صحيح
    }
    response = requests.put(f"{GITHUB_API_URL}/repos/{GITHUB_USERNAME}/{repo_name}/contents/{filename}", headers=headers, json=data)
    if response.status_code in [201, 200]:
        update.message.reply_text(f'تم إنشاء الملف "{filename}" في المستودع "{repo_name}" بنجاح!')
    else:
        update.message.reply_text(f'فشل في إنشاء الملف: {response.json().get("message")}')
# إدارة Codespaces
def create_codespace(update: Update, codespace_name: str) -> None:
    headers = {
        'Authorization': f'token {GITHUB_TOKEN}',
        'Accept': 'application/vnd.github.v3+json'
    }
    data = {
        "repository_id": "REPOSITORY_ID",  # حدد ID المستودع المناسب
        "ref": "main",
        "devcontainer": {},  # يمكنك تحديد إعدادات devcontainer هنا
        "name": codespace_name
    }
    response = requests.post(f'{GITHUB_API_URL}/user/codespaces', headers=headers, json=data)
    
    if response.status_code == 201:
        update.message.reply_text(f'تم إنشاء كود سبيس "{codespace_name}" بنجاح!')
    else:
        update.message.reply_text(f'فشل في إنشاء كود سبيس: {response.json().get("message")}')
def delete_codespace(update: Update, codespace_name: str) -> None:
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.delete(f'{GITHUB_API_URL}/user/codespaces/{codespace_name}', headers=headers)
    
    if response.status_code == 204:
        update.message.reply_text(f'تم حذف كود سبيس "{codespace_name}" بنجاح!')
    else:
        update.message.reply_text(f'فشل في حذف كود سبيس: {response.json().get("message")}')
def list_codespaces(update: Update) -> None:
    headers = {'Authorization': f'token {GITHUB_TOKEN}'}
    response = requests.get(f'{GITHUB_API_URL}/user/codespaces', headers=headers)
    
    if response.status_code == 200:
        codespaces = response.json()
        if codespaces:
            codespace_names = "\n".join([cs['name'] for cs in codespaces])
            update.message.reply_text(f'الكودات السبيس المتاحة:\n{codespace_names}')
        else:
            update.message.reply_text('لا توجد كودات سبيس متاحة!')
    else:
        update.message.reply_text(f'فشل في جلب كودات سبيس: {response.json().get("message")}')
def handle_docs(update: Update, context: CallbackContext) -> None:
    document = update.message.document
    new_file = context.bot.getFile(document.file_id)
    new_file.download(document.file_name)
    
    update.message.reply_text(f'تم تحميل الملف {document.file_name} بنجاح! يمكنك إدخال اسم الملف كجزء من الأمر لإنشاءه في مستودع GitHub.')
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN)
    
    dp = updater.dispatcher
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))
    dp.add_handler(MessageHandler(Filters.document.mime_type("application/octet-stream"), handle_docs))
    updater.start_polling()
    updater.idle()
if _name_ == '_main_':
    main()
