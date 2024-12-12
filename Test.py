import os
import requests
from dotenv import load_dotenv
import openai

# تحميل ملفات البيئة
load_dotenv()

# مفاتيح الوصول
GITHUB_API_TOKEN = os.getenv("GITHUB_API_TOKEN")
openai.api_key = os.getenv("OPENAI_API_KEY")

# إعداد الرأس للتعامل مع GitHub API
HEADERS = {"Authorization": f"token {GITHUB_API_TOKEN}"}

# 1. وظائف GitHub API
def list_codespaces():
    """قائمة بجميع Codespaces الخاصة بالمستخدم."""
    url = "https://api.github.com/user/codespaces"
    response = requests.get(url, headers=HEADERS)
    if response.status_code == 200:
        codespaces = response.json()
        for cs in codespaces:
            print(f"Name: {cs['name']}, State: {cs['state']}, Repository: {cs['repository']['full_name']}")
    else:
        print(f"Failed to fetch codespaces: {response.status_code} - {response.text}")

def create_codespace(repo_name):
    """إنشاء Codespace جديد على مستودع محدد."""
    url = f"https://api.github.com/repos/{repo_name}/codespaces"
    payload = {"machine": "standardLinux", "devcontainer_path": ".devcontainer/devcontainer.json"}
    response = requests.post(url, headers=HEADERS, json=payload)
    if response.status_code == 201:
        print(f"Codespace created successfully: {response.json()['name']}")
    else:
        print(f"Failed to create codespace: {response.status_code} - {response.text}")

def sync_file_to_repo(repo_name, file_name, content, commit_message="Add file"):
    """رفع ملف إلى مستودع GitHub."""
    url = f"https://api.github.com/repos/{repo_name}/contents/{file_name}"
    payload = {
        "message": commit_message,
        "content": content.encode("utf-8").decode("utf-8"),
    }
    response = requests.put(url, headers=HEADERS, json=payload)
    if response.status_code in [200, 201]:
        print(f"File '{file_name}' synced successfully.")
    else:
        print(f"Failed to sync file: {response.status_code} - {response.text}")

# 2. وظائف ChatGPT
def generate_code(prompt):
    """توليد كود باستخدام ChatGPT."""
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "You are a helpful assistant specialized in generating code."},
            {"role": "user", "content": prompt}
        ]
    )
    return response['choices'][0]['message']['content']

# 3. جلسة تفاعلية
def start_interactive_session():
    print("Welcome to the GitHub Codespaces Manager with ChatGPT.")
    while True:
        command = input("Enter command (codespaces, generate, sync, exit): ").strip().lower()
        if command == "codespaces":
            action = input("Enter action (list, create): ").strip().lower()
            if action == "list":
                list_codespaces()
            elif action == "create":
                repo_name = input("Enter repository name (user/repo): ").strip()
                create_codespace(repo_name)
            else:
                print("Unknown action. Try 'list' or 'create'.")
        elif command == "generate":
            prompt = input("Describe the code you want to generate: ").strip()
            code = generate_code(prompt)
            print("Generated code:\n", code)
            save = input("Do you want to save this code to a GitHub repo? (yes/no): ").strip().lower()
            if save == "yes":
                repo_name = input("Enter repository name (user/repo): ").strip()
                file_name = input("Enter file name (e.g., script.py): ").strip()
                commit_message = input("Enter commit message: ").strip()
                sync_file_to_repo(repo_name, file_name, code, commit_message)
        elif command == "sync":
            repo_name = input("Enter repository name (user/repo): ").strip()
            file_name = input("Enter file name to sync (e.g., script.py): ").strip()
            with open(file_name, "r") as f:
                content = f.read()
            commit_message = input("Enter commit message: ").strip()
            sync_file_to_repo(repo_name, file_name, content, commit_message)
        elif command == "exit":
            print("Exiting interactive session.")
            break
        else:
            print("Unknown command. Try 'codespaces', 'generate', 'sync', or 'exit'.")

# بدء التفاعل
if __name__ == "__main__":
    start_interactive_session()
