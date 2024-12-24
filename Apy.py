import streamlit as st
import time
import random
import openai
from collections import defaultdict
from typing import List

# إعداد تكامل ChatGPT API
openai.api_key = 'YOUR_OPENAI_API_KEY'

class Task:
    def __init__(self, task_id: str, name: str, description: str, dependencies: List[str] = []):
        self.task_id = task_id
        self.name = name
        self.description = description
        self.dependencies = dependencies
        self.completed = False
        self.start_time = None
        self.end_time = None

    def start(self):
        self.start_time = time.time()

    def complete(self):
        self.end_time = time.time()
        self.completed = True

    def duration(self):
        if self.start_time and self.end_time:
            return self.end_time - self.start_time
        return 0

class AIManager:
    def __init__(self):
        self.user_tasks = {}
        self.reports = {}

    def add_task(self, task: Task):
        self.user_tasks[task.task_id] = task

    def get_task(self, task_id: str) -> Task:
        return self.user_tasks.get(task_id)

    def generate_report(self, task_id: str):
        task = self.get_task(task_id)
        if task:
            report = {
                'task_id': task.task_id,
                'name': task.name,
                'status': 'Completed' if task.completed else 'In Progress',
                'duration': task.duration(),
            }
            self.reports[task_id] = report
            return report
        return {}

    def automate_task(self, task_id: str):
        task = self.get_task(task_id)
        if task and not task.completed:
            task.start()
            time.sleep(random.randint(1, 3))  # محاكاة تنفيذ المهمة
            task.complete()

class WorkflowManager:
    def __init__(self, ai_manager: AIManager):
        self.ai_manager = ai_manager

    def create_task(self, name: str, description: str, dependencies: List[str] = []):
        task_id = str(random.randint(1000, 9999))
        task = Task(task_id, name, description, dependencies)
        self.ai_manager.add_task(task)
        return task

    def manage_workflow(self):
        """إدارة سير العمل وتنفيذ المهام المكتملة"""
        for task in self.ai_manager.user_tasks.values():
            if not task.completed and all(self.ai_manager.get_task(dep).completed for dep in task.dependencies):
                self.ai_manager.automate_task(task.task_id)

class ChatGPTHandler:
    def __init__(self):
        self.ai_manager = AIManager()
        self.workflow_manager = WorkflowManager(self.ai_manager)

    def generate_ai_suggestions(self, task_name: str, task_description: str):
        """تقديم اقتراحات باستخدام ChatGPT"""
        prompt = f"Task Name: {task_name}\nTask Description: {task_description}\n\nProvide suggestions and improvements:"
        response = openai.Completion.create(
            model="gpt-4",
            prompt=prompt,
            max_tokens=150,
        )
        return response.choices[0].text.strip()

# إعداد الواجهة باستخدام Streamlit
st.title("نظام إدارة المهام الذكي")
st.sidebar.header("القائمة الجانبية")

# إنشاء مدير النظام
chatgpt_handler = ChatGPTHandler()
workflow_manager = chatgpt_handler.workflow_manager

# إضافة المهام من خلال الواجهة
st.header("إضافة مهمة جديدة")
task_name = st.text_input("اسم المهمة")
task_description = st.text_area("وصف المهمة")
dependencies = st.text_input("معرفات المهام المعتمدة (مفصولة بفاصلة)")

if st.button("إضافة المهمة"):
    deps = dependencies.split(",") if dependencies else []
    new_task = workflow_manager.create_task(task_name, task_description, deps)
    st.success(f"تمت إضافة المهمة: {new_task.name} (ID: {new_task.task_id})")

# عرض المهام الحالية
st.header("المهام الحالية")
if workflow_manager.ai_manager.user_tasks:
    for task_id, task in workflow_manager.ai_manager.user_tasks.items():
        st.subheader(f"المهمة: {task.name} (ID: {task.task_id})")
        st.write(f"الوصف: {task.description}")
        st.write(f"الحالة: {'مكتملة' if task.completed else 'قيد التنفيذ'}")
        if st.button(f"إكمال المهمة {task.task_id}"):
            workflow_manager.ai_manager.automate_task(task_id)
            st.success(f"تمت إكمال المهمة: {task.name}")
else:
    st.write("لا توجد مهام مضافة حاليًا.")

# اقتراحات الذكاء الاصطناعي
st.header("اقتراحات الذكاء الاصطناعي")
if task_name and task_description:
    if st.button("الحصول على اقتراحات"):
        suggestions = chatgpt_handler.generate_ai_suggestions(task_name, task_description)
        st.subheader("اقتراحات:")
        st.write(suggestions)

# إدارة سير العمل
if st.sidebar.button("إدارة سير العمل"):
    workflow_manager.manage_workflow()
    st.sidebar.success("تمت إدارة سير العمل وإكمال المهام الممكنة.")

# التقارير
st.sidebar.header("التقارير")
if st.sidebar.button("عرض جميع التقارير"):
    st.header("تقارير المهام")
    for task_id in workflow_manager.ai_manager.user_tasks:
        report = workflow_manager.ai_manager.generate_report(task_id)
        st.subheader(f"تقرير المهمة {task_id}")
        st.json(report)
