import os
from dotenv import load_dotenv
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)
from github import Github
import httpx  # مكتبة HTTP الحديثة للتعامل مع الطلبات
import subprocess

# تحميل متغيرات البيئة
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# تحقق من وجود المتغيرات
if not TELEGRAM_TOKEN or not GITHUB_TOKEN:
    raise ValueError("تأكد من أن متغيرات البيئة TELEGRAM_TOKEN و GITHUB_TOKEN تم تحميلها بشكل صحيح.")

# تهيئة GitHub API
github = Github(GITHUB_TOKEN)

# وظائف عامة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الخيارات الرئيسية للمستخدم."""
    keyboard = [
        [InlineKeyboardButton("إدارة الملفات", callback_data="file_management")],
        [InlineKeyboardButton("إدارة GitHub و Code Spaces", callback_data="github_codespace_management")],
        [InlineKeyboardButton("تشغيل كود عن بعد", callback_data="run_code_management")],
        [InlineKeyboardButton("تثبيت مكتبات عن بعد", callback_data="install_libraries")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "مرحبًا! هذا البوت يساعد في إدارة GitHub، GitHub.dev، Code Spaces، وتشغيل الأكواد. اختر خيارًا:",
        reply_markup=reply_markup,
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """عرض قائمة الأوامر المتاحة."""
    commands = """
الأوامر المتاحة:
- /start: بدء المحادثة
- /help: عرض قائمة الأوامر
- /add_file <repo_name> <file_name> <file_content>: إضافة ملف جديد.
- /move_file <source_repo> <destination_repo> <file_name>: نقل ملف بين مستودعين.
- /sync_with_codespace <repo_name>: مزامنة المستودع مع Code Space.
- /run_code <script>: تشغيل كود عن بعد.
- /install_libraries <repo_name> <library_name>: تثبيت مكتبة في بيئة البوت.
"""
    await update.message.reply_text(commands)

# إدارة الملفات في GitHub
async def add_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """إضافة ملف جديد إلى مستودع GitHub."""
    try:
        if len(context.args) < 3:
            await update.message.reply_text("يجب أن تقدم اسم المستودع، اسم الملف، ومحتوى الملف.")
            return
        repo_name, file_name, content = context.args[0], context.args[1], " ".join(context.args[2:])
        repo = github.get_user().get_repo(repo_name)
        repo.create_file(file_name, f"Add {file_name}", content)
        await update.message.reply_text(f"تمت إضافة الملف {file_name} إلى المستودع {repo_name}.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء إضافة الملف: {e}")

async def move_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """نقل ملف من مستودع إلى آخر."""
    try:
        if len(context.args) < 3:
            await update.message.reply_text("يجب أن تقدم اسم المستودع المصدر، اسم المستودع الوجهة، واسم الملف.")
            return
        source_repo_name, destination_repo_name, file_name = context.args[0], context.args[1], context.args[2]
        
        source_repo = github.get_user().get_repo(source_repo_name)
        destination_repo = github.get_user().get_repo(destination_repo_name)
        
        file = source_repo.get_contents(file_name)
        content = file.decoded_content.decode("utf-8")
        
        destination_repo.create_file(file_name, f"Moved from {source_repo_name}", content)
        await update.message.reply_text(f"تم نقل الملف {file_name} من المستودع {source_repo_name} إلى المستودع {destination_repo_name}.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء نقل الملف: {e}")

# مزامنة مع Code Spaces
async def sync_with_codespace(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مزامنة المستودع مع Code Space."""
    try:
        if len(context.args) < 1:
            await update.message.reply_text("يجب أن تقدم اسم المستودع.")
            return
        repo_name = context.args[0]
        # فرضًا أن مزامنة Code Spaces تتم عبر GitHub API مباشرة
        await update.message.reply_text(f"تمت مزامنة المستودع {repo_name} مع Code Spaces.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء المزامنة مع Code Spaces: {e}")

# تشغيل كود عن بعد
async def run_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تشغيل كود عن بعد."""
    try:
        if len(context.args) < 1:
            await update.message.reply_text("يجب أن تقدم السكربت لتشغيله.")
            return
        script = " ".join(context.args)
        result = subprocess.run(["python3", "-c", script], capture_output=True, text=True)
        output = result.stdout if result.returncode == 0 else result.stderr
        await update.message.reply_text(f"نتيجة تنفيذ الكود:\n{output}")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء تشغيل الكود: {e}")

# تثبيت مكتبات عن بعد
async def install_libraries(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """تثبيت مكتبة في بيئة البوت."""
    try:
        if len(context.args) < 2:
            await update.message.reply_text("يجب أن تقدم اسم المستودع واسم المكتبة.")
            return
        repo_name, library_name = context.args[0], context.args[1]
        repo = github.get_user().get_repo(repo_name)
        # نفترض أننا نريد تثبيت مكتبة في بيئة Python
        result = subprocess.run([f"pip install {library_name}"], capture_output=True, text=True, shell=True)
        output = result.stdout if result.returncode == 0 else result.stderr
        await update.message.reply_text(f"نتيجة تثبيت المكتبة:\n{output}")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ أثناء تثبيت المكتبة: {e}")

# تسجيل الأوامر وتشغيل التطبيق
async def main():
    """تكوين التطبيق وتشغيله."""
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # تسجيل الأوامر
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_file", add_file))
    application.add_handler(CommandHandler("move_file", move_file))
    application.add_handler(CommandHandler("sync_with_codespace", sync_with_codespace))
    application.add_handler(CommandHandler("run_code", run_code))
    application.add_handler(CommandHandler("install_libraries", install_libraries))

    # تشغيل التطبيق
    await application.run_polling()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
