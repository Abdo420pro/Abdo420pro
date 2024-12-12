import telebot
from github import Github
import openai  # مكتبة ChatGPT
from dotenv import load_dotenv
import os

# تحميل التوكنات من ملف .env
load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

bot = telebot.TeleBot(TELEGRAM_TOKEN)
github = Github(GITHUB_TOKEN)
openai.api_key = OPENAI_API_KEY

# تخزين حالة المستخدم
user_data = {}

@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "مرحبًا! أنا البوت الخاص بك لإدارة مستودعات GitHub وتحليل الأكواد باستخدام ChatGPT. أرسل /help لعرض الأوامر المتاحة.")

@bot.message_handler(commands=['help'])
def help_command(message):
    help_text = """
    **الأوامر المتاحة:**
    /start - بدء المحادثة
    /help - عرض قائمة الأوامر
    /upload_code - رفع كود إلى مستودع GitHub
    /analyze_code - تحليل الكود باستخدام ChatGPT
    /retrieve_file - استرجاع ملف من مستودع GitHub
    """
    bot.reply_to(message, help_text)

@bot.message_handler(commands=['upload_code'])
def upload_code(message):
    user_data[message.chat.id] = {'action': 'upload'}
    bot.reply_to(message, "يرجى إرسال اسم المستودع الذي تريد رفع الكود إليه:")

@bot.message_handler(commands=['analyze_code'])
def analyze_code(message):
    user_data[message.chat.id] = {'action': 'analyze'}
    bot.reply_to(message, "يرجى إرسال الكود الذي تريد تحليله:")

@bot.message_handler(commands=['retrieve_file'])
def retrieve_file(message):
    user_data[message.chat.id] = {'action': 'retrieve'}
    bot.reply_to(message, "يرجى إرسال اسم المستودع الذي تريد استرجاع الملف منه:")

@bot.message_handler(func=lambda msg: msg.chat.id in user_data)
def handle_user_input(message):
    chat_id = message.chat.id
    action = user_data[chat_id]['action']

    if action == 'upload' and 'repo_name' not in user_data[chat_id]:
        user_data[chat_id]['repo_name'] = message.text.strip()
        bot.reply_to(message, "يرجى إرسال اسم الملف (أو كتابة 'افتراضي' لاستخدام اسم افتراضي):")
    elif action == 'upload' and 'file_name' not in user_data[chat_id]:
        file_name = message.text.strip()
        if file_name.lower() == "افتراضي":
            file_name = "generated_code.py"
        user_data[chat_id]['file_name'] = file_name
        bot.reply_to(message, "يرجى الآن إرسال الكود:")
    elif action == 'upload' and 'code' not in user_data[chat_id]:
        user_data[chat_id]['code'] = message.text
        bot.reply_to(message, "جاري رفع الكود إلى المستودع...")
        upload_to_github(message)
    elif action == 'analyze':
        analyze_code_with_gpt(message.text, message)
    elif action == 'retrieve' and 'repo_name' not in user_data[chat_id]:
        user_data[chat_id]['repo_name'] = message.text.strip()
        bot.reply_to(message, "يرجى إرسال اسم الملف الذي تريد استرجاعه:")
    elif action == 'retrieve':
        retrieve_file_from_github(message)

def upload_to_github(message):
    chat_id = message.chat.id
    repo_name = user_data[chat_id]['repo_name']
    file_name = user_data[chat_id]['file_name']
    code_content = user_data[chat_id]['code']

    try:
        # البحث عن المستودع
        repo = github.get_user().get_repo(repo_name)

        # التحقق إذا كان الملف موجوداً مسبقًا
        try:
            existing_file = repo.get_contents(file_name)
            # تحديث الملف إذا كان موجودًا
            repo.update_file(
                path=existing_file.path,
                message=f"Updating {file_name}",
                content=code_content,
                sha=existing_file.sha
            )
            bot.reply_to(message, f"تم تحديث الملف {file_name} في المستودع {repo_name}.")
        except:
            # إنشاء الملف إذا لم يكن موجودًا
            repo.create_file(
                path=file_name,
                message=f"Adding {file_name}",
                content=code_content
            )
            bot.reply_to(message, f"تم إنشاء الملف {file_name} ورفعه بنجاح إلى المستودع {repo_name}.")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء رفع الكود: {e}")
    finally:
        if chat_id in user_data:
            del user_data[chat_id]

def analyze_code_with_gpt(code, message):
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "أنت مساعد برمجي لتحليل الأكواد."},
                {"role": "user", "content": code}
            ]
        )
        analysis = response['choices'][0]['message']['content']
        bot.reply_to(message, f"تحليل الكود:\n{analysis}")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء تحليل الكود: {e}")
    finally:
        del user_data[message.chat.id]

def retrieve_file_from_github(message):
    chat_id = message.chat.id
    repo_name = user_data[chat_id]['repo_name']
    file_name = message.text.strip()

    try:
        repo = github.get_user().get_repo(repo_name)
        file_content = repo.get_contents(file_name).decoded_content.decode()
        bot.reply_to(message, f"محتويات الملف {file_name}:\n{file_content}")
    except Exception as e:
        bot.reply_to(message, f"حدث خطأ أثناء استرجاع الملف: {e}")
    finally:
        del user_data[chat_id]

# تشغيل البوت
bot.polling()
