
import os
from telegram import Update, InputFile
from telegram.ext import Updater, CommandHandler, CallbackContext
from github import Github
from dotenv import load_dotenv

# تحميل متغيرات البيئة
load_dotenv()
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# تهيئة GitHub API
github = Github(GITHUB_TOKEN)

# وظائف البوت

def start(update: Update, context: CallbackContext):
    update.message.reply_text("مرحبًا بك في بوت إدارة GitHub وCode Spaces. اكتب /help للحصول على الأوامر المتاحة.")

def help_command(update: Update, context: CallbackContext):
    commands = """
الأوامر المتاحة:
- /add_file <repo_name> <file_name> <file_content>: إضافة ملف جديد.
- /delete_file <repo_name> <file_name>: حذف ملف.
- /rename_file <repo_name> <old_name> <new_name>: إعادة تسمية ملف.
- /move_file <source_repo> <file_name> <destination_repo>: نقل ملف بين المستودعات.
- /upload_file <repo_name>: رفع ملف من جهازك.
- /download_file <repo_name> <file_name>: تنزيل ملف.
- /list_files <repo_name>: عرض قائمة الملفات.
"""
    update.message.reply_text(commands)

def add_file(update: Update, context: CallbackContext):
    try:
        repo_name, file_name, content = context.args[0], context.args[1], " ".join(context.args[2:])
        repo = github.get_user().get_repo(repo_name)
        repo.create_file(file_name, f"Add {file_name}", content)
        update.message.reply_text(f"تمت إضافة الملف {file_name} إلى المستودع {repo_name}.")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

def delete_file(update: Update, context: CallbackContext):
    try:
        repo_name, file_name = context.args[0], context.args[1]
        repo = github.get_user().get_repo(repo_name)
        file = repo.get_contents(file_name)
        repo.delete_file(file.path, f"Delete {file_name}", file.sha)
        update.message.reply_text(f"تم حذف الملف {file_name} من المستودع {repo_name}.")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

def rename_file(update: Update, context: CallbackContext):
    try:
        repo_name, old_name, new_name = context.args[0], context.args[1], context.args[2]
        repo = github.get_user().get_repo(repo_name)
        file = repo.get_contents(old_name)
        repo.create_file(new_name, f"Rename {old_name} to {new_name}", file.decoded_content.decode())
        repo.delete_file(file.path, f"Rename {old_name} to {new_name}", file.sha)
        update.message.reply_text(f"تمت إعادة تسمية الملف {old_name} إلى {new_name}.")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

def move_file(update: Update, context: CallbackContext):
    try:
        source_repo, file_name, destination_repo = context.args[0], context.args[1], context.args[2]
        source = github.get_user().get_repo(source_repo)
        destination = github.get_user().get_repo(destination_repo)
        file = source.get_contents(file_name)
        destination.create_file(file_name, f"Move {file_name}", file.decoded_content.decode())
        source.delete_file(file.path, f"Move {file_name} to {destination_repo}", file.sha)
        update.message.reply_text(f"تم نقل الملف {file_name} من {source_repo} إلى {destination_repo}.")
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

def upload_file(update: Update, context: CallbackContext):
    try:
        repo_name = context.args[0]
        if not context.bot_data.get("upload_file"):
            update.message.reply_text("يرجى إرسال الملف بعد هذا الأمر.")
            context.bot_data["upload_file"] = repo_name
        else:
            repo_name = context.bot_data["upload_file"]
            file = update.message.document
            file_name = file.file_name
            file_content = file.get_file().download_as_bytearray()
            repo = github.get_user().get_repo(repo_name)
            repo.create_file(file_name, f"Upload {file_name}", file_content)
            update.message.reply_text(f"تم رفع الملف {file_name} إلى المستودع {repo_name}.")
            del context.bot_data["upload_file"]
    except Exception as e:
        update.message.reply_text(f"حدث خطأ: {e}")

def download_file(update: Update, context: CallbackContext):
    try:
        repo_name, file_name = context.args[0], context.args[1]
        repo = github.get_user().get_repo(repo_name)
        file = repo.get_contents(file_name)
        update.message.reply_document(InputFile(file.decoded_content.decode(), file_name))
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

# تشغيل البوت
updater = Updater(TELEGRAM_TOKEN)

updater.dispatcher.add_handler(CommandHandler("start", start))
updater.dispatcher.add_handler(CommandHandler("help", help_command))
updater.dispatcher.add_handler(CommandHandler("add_file", add_file))
updater.dispatcher.add_handler(CommandHandler("delete_file", delete_file))
updater.dispatcher.add_handler(CommandHandler("rename_file", rename_file))
updater.dispatcher.add_handler(CommandHandler("move_file", move_file))
updater.dispatcher.add_handler(CommandHandler("upload_file", upload_file))
updater.dispatcher.add_handler(CommandHandler("download_file", download_file))
updater.dispatcher.add_handler(CommandHandler("list_files", list_files))

updater.start_polling()
updater.idle()
