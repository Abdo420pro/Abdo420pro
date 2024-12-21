import os
import subprocess
from dotenv import load_dotenv
from github import Github
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
import httpx  # استبدال urllib3 بـ httpx

# تحميل متغيرات البيئة
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# تهيئة GitHub API
github = Github(GITHUB_TOKEN)

# وظائف عامة
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("إدارة الملفات", callback_data="file_management")],
        [InlineKeyboardButton("إدارة البيئات البرمجية", callback_data="env_management")],
        [InlineKeyboardButton("إدارة GitHub", callback_data="github_management")],
        [InlineKeyboardButton("إدارة Code Spaces", callback_data="codespace_management")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        "مرحبًا! هذا البوت يدير GitHub، GitHub.dev، وCode Spaces. اختر خيارًا من القائمة:",
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    commands = """
الأوامر المتاحة:
- /start: بدء المحادثة
- /help: عرض قائمة الأوامر
- /add_file <repo_name> <file_name> <file_content>: إضافة ملف جديد.
- /edit_file <repo_name> <file_name> <new_content>: تعديل محتوى الملف.
- /list_files <repo_name>: عرض الملفات في المستودع.
- /view_env_files <env_name>: عرض الملفات داخل البيئة.
- /edit_env_file <env_name> <file_name> <new_content>: تعديل ملف داخل البيئة.
- /open_codespace <codespace_name>: الدخول إلى Code Space.
- /open_github_dev <repo_name>: فتح GitHub.dev.
"""
    await update.message.reply_text(commands)

# إدارة الملفات داخل المستودعات
async def add_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        repo_name, file_name, content = context.args[0], context.args[1], " ".join(context.args[2:])
        repo = github.get_user().get_repo(repo_name)
        repo.create_file(file_name, f"Add {file_name}", content)
        await update.message.reply_text(f"تمت إضافة الملف {file_name} إلى المستودع {repo_name}.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

async def edit_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        repo_name, file_name, new_content = context.args[0], context.args[1], " ".join(context.args[2:])
        repo = github.get_user().get_repo(repo_name)
        file = repo.get_contents(file_name)
        repo.update_file(file.path, f"Edit {file_name}", new_content, file.sha)
        await update.message.reply_text(f"تم تعديل الملف {file_name} في المستودع {repo_name}.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

async def list_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        repo_name = context.args[0]
        repo = github.get_user().get_repo(repo_name)
        files = [file.path for file in repo.get_contents("")]
        await update.message.reply_text("الملفات:\n" + "\n".join(files))
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# إدارة البيئات البرمجية
async def view_env_files(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        env_name = context.args[0]
        # إضافة منطق لعرض الملفات في البيئة البرمجية هنا
        await update.message.reply_text(f"عرض ملفات البيئة: {env_name}")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

async def edit_env_file(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        env_name, file_name, new_content = context.args[0], context.args[1], " ".join(context.args[2:])
        # إضافة منطق لتعديل ملف في البيئة البرمجية هنا
        await update.message.reply_text(f"تم تعديل الملف {file_name} في البيئة {env_name}.")
    except Exception as e:
        await update.message.reply_text(f"حدث خطأ: {e}")

# طلب من خلال httpx (استبدال urllib3)
async def make_request(url: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        return response.text

# تسجيل الأوامر
async def main():
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("add_file", add_file))
    application.add_handler(CommandHandler("edit_file", edit_file))
    application.add_handler(CommandHandler("list_files", list_files))
    application.add_handler(CommandHandler("view_env_files", view_env_files))
    application.add_handler(CommandHandler("edit_env_file", edit_env_file))

    await application.run_polling()

# تشغيل البوت
if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
