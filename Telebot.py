import os
import subprocess
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext
from github import Github
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# تهيئة GitHub API
github = Github(GITHUB_TOKEN)

# وظائف عامة
def start(update: Update, context: CallbackContext):
    keyboard = [
        [InlineKeyboardButton("إدارة الملفات", callback_data="file_management")],
        [InlineKeyboardButton("إدارة البيئات البرمجية", callback_data="env_management")],
        [InlineKeyboardButton("إدارة GitHub", callback_data="github_management")],
        [InlineKeyboardButton("إدارة Code Spaces", callback_data="codespace_management")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text("مرحبًا! هذا البوت يدير GitHub، GitHub.dev، وCode Spaces. اختر خيارًا من القائمة:", reply_markup=reply_markup)

def help_command(update: Update, context: CallbackContext):
    commands = """
الأوامر المتاحة:
- /add_file <repo_name> <file_name> <file_content>: إضافة ملف جديد.
- /delete_file <repo_name> <file_name>: حذف ملف.
- /rename_file <repo_name> <old_name> <new_name>: إعادة تسمية ملف.
- /edit_file <repo_name> <file_name> <new_content>: تعديل محتوى الملف.
- /list_files <repo_name>: عرض الملفات في المستودع.
- /view_env_files <env_name>: عرض الملفات داخل البيئة.
- /edit_env_file <env_name> <file_name> <new_content>: تعديل ملف داخل البيئة.
- /open_codespace <codespace_name>: الدخول إلى Code Space.
- /open_github_dev <repo_name>: فتح GitHub.dev.
"""
    update.message.reply_text(commands)

# إدارة الملفات داخل المستودعات
def add_file(update: Update, context: CallbackContext):
    try:
        repo_name, file_name, content = context.args[0], context.args[1], " ".join(context.args[2:])
        repo = github.get_user().get_repo(repo_name)
        repo.create_file(file_name, f"Add {file_name}", content)
        update.message.reply_text(f"تمت إضافة الملف {file_name} إلى المستودع {repo_name}.")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

def edit_file(update: Update, context: CallbackContext):
    try:
        repo_name, file_name, new_content = context.args[0], context.args[1], " ".join(context.args[2:])
        repo = github.get_user().get_repo(repo_name)
        file = repo.get_contents(file_name)
        repo.update_file(file.path, f"Edit {file_name}", new_content, file.sha)
        update.message.reply_text(f"تم تعديل الملف {file_name} في المستودع {repo_name}.")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

def list_files(update: Update, context: CallbackContext):
    try:
        repo_name = context.args[0]
        repo = github.get_user().get_repo(repo_name)
        files = [file.path for file in repo.get_contents("")]
        update.message.reply_text("الملفات:\n" + "\n".join(files))
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

# إدارة البيئات البرمجية
def view_env_files(update: Update, context: CallbackContext):
    try:
        env_name = context.args[0]
        env_path = os.path.join(os.getcwd(), env_name)
        files = [f for f in os.listdir(env_path) if os.path.isfile(os.path.join(env_path, f))]
        update.message.reply_text(f"الملفات داخل البيئة {env_name}:\n" + "\n".join(files))
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

def edit_env_file(update: Update, context: CallbackContext):
    try:
        env_name, file_name, new_content = context.args[0], context.args[1], " ".join(context.args[2:])
        env_path = os.path.join(os.getcwd(), env_name, file_name)
        with open(env_path, "w") as f:
            f.write(new_content)
        update.message.reply_text(f"تم تعديل الملف {file_name} داخل البيئة {env_name}.")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

# إدارة Code Spaces
def open_codespace(update: Update, context: CallbackContext):
    try:
        codespace_name = context.args[0]
        os.system(f"gh codespace ssh -c {codespace_name}")
        update.message.reply_text(f"تم فتح Code Space: {codespace_name}.")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

# إدارة GitHub.dev
def open_github_dev(update: Update, context: CallbackContext):
    try:
        repo_name = context.args[0]
        repo_url = f"https://github.dev/{github.get_user().login}/{repo_name}"
        update.message.reply_text(f"فتح GitHub.dev للمستودع {repo_name}: {repo_url}")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

# تشغيل البوت
updater = Updater(TELEGRAM_TOKEN)

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("help", help_command))
updater.dispatcher.add_handler(CommandHandler("add_file", add_file))
updater.dispatcher.add_handler(CommandHandler("edit_file", edit_file))
updater.dispatcher.add_handler(CommandHandler("list_files", list_files))
updater.dispatcher.add_handler(CommandHandler("view_env_files", view_env_files))
updater.dispatcher.add_handler(CommandHandler("edit_env_file", edit_env_file))
updater.dispatcher.add_handler(CommandHandler("open_codespace", open_codespace))
updater.dispatcher.add_handler(CommandHandler("open_github_dev", open_github_dev))

updater.start_polling()
updater.idle()
