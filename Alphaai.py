import openai
from notion_client import Client
import sqlite3
import json
from datetime import datetime
import telebot

# إعداد مفاتيح API
openai.api_key = "your_openai_api_key"
notion = Client(auth="your_notion_api_key")
bot = telebot.TeleBot("your_telegram_bot_token")

# إعداد قاعدة البيانات
def setup_database():
    conn = sqlite3.connect("smart_templates.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS templates (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            description TEXT,
            structure TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()

setup_database()

# توليد قالب ذكي مع تفرعات متعددة
def generate_template(title, description, levels=7, branches=7):
    def recursive_generate(level, max_levels):
        if level > max_levels:
            return []

        branches_data = []
        for i in range(1, branches + 1):
            branch_title = f"فرع {level}-{i}"
            branch_description = f"هذا هو التفرع رقم {i} في المستوى {level}."
            
            # إنشاء قدرات لكل فرع
            capabilities = [f"قدرة {i}-{j}" for j in range(1, branches + 1)]

            branches_data.append({
                "title": branch_title,
                "description": branch_description,
                "capabilities": capabilities,
                "sub_branches": recursive_generate(level + 1, max_levels)
            })
        
        return branches_data

    template_structure = {
        "title": title,
        "description": description,
        "structure": recursive_generate(1, levels)
    }

    # حفظ القالب في قاعدة البيانات
    conn = sqlite3.connect("smart_templates.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO templates (title, description, structure) VALUES (?, ?, ?)
    """, (title, description, json.dumps(template_structure)))
    conn.commit()
    conn.close()

    return template_structure

# تصدير القالب إلى Notion
def export_to_notion(template):
    notion_page = notion.pages.create(
        parent={"database_id": "your_notion_database_id"},
        properties={
            "Name": {"title": [{"text": {"content": template['title']}}]}
        },
        children=[
            {
                "object": "block",
                "type": "heading_2",
                "heading_2": {"text": [{"type": "text", "text": {"content": template['title']}}]}
            },
            {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"text": [{"type": "text", "text": {"content": template['description']}}]}
            }
        ]
    )

    def add_structure_to_notion(parent_id, structure, level=1):
        for branch in structure:
            branch_block = {
                "object": "block",
                "type": "heading_3",
                "heading_3": {"text": [{"type": "text", "text": {"content": branch['title']}}]}
            }
            notion.blocks.children.append(parent_id, branch_block)

            description_block = {
                "object": "block",
                "type": "paragraph",
                "paragraph": {"text": [{"type": "text", "text": {"content": branch['description']}}]}
            }
            notion.blocks.children.append(parent_id, description_block)

            for capability in branch['capabilities']:
                capability_block = {
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {"text": [{"type": "text", "text": {"content": capability}}]}
                }
                notion.blocks.children.append(parent_id, capability_block)

            if branch['sub_branches']:
                add_structure_to_notion(parent_id, branch['sub_branches'], level + 1)

    add_structure_to_notion(notion_page["id"], template['structure'])
    return notion_page["url"]

# ربط النظام مع بوت Telegram
@bot.message_handler(commands=['start'])
def start(message):
    bot.reply_to(message, "مرحباً بك في نظام إنشاء القوالب الذكية! أرسل /create لإنشاء قالب جديد.")

@bot.message_handler(commands=['create'])
def create_template(message):
    bot.reply_to(message, "يرجى إدخال اسم القالب:")
    bot.register_next_step_handler(message, get_template_description)

def get_template_description(message):
    title = message.text
    bot.reply_to(message, "يرجى إدخال وصف القالب:")
    bot.register_next_step_handler(message, process_template_request, title)

def process_template_request(message, title):
    description = message.text
    bot.reply_to(message, "جارٍ إنشاء القالب...")
    template = generate_template(title, description)
    notion_url = export_to_notion(template)
    bot.reply_to(message, f"تم إنشاء القالب بنجاح! يمكنك الوصول إليه عبر الرابط التالي:\n{notion_url}")

bot.polling()
