import json
import random
import re
from datetime import datetime

# Загрузка советов
def get_random_tip():
    try:
        with open("data/tips.json", "r", encoding="utf-8") as f:
            tips = json.load(f)
        return random.choice(tips)
    except:
        return "🌟 Верь в себя! У тебя всё получится!"

# Загрузка FAQ
def get_faq():
    try:
        with open("data/faq.json", "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# Проверка имени (только буквы)
def is_valid_name(name):
    return bool(re.match(r'^[а-яА-Яa-zA-Z\s\-]+$', name)) and len(name) >= 2

# Проверка возраста
def is_valid_age(age):
    return age.isdigit() and 14 <= int(age) <= 100

# Проверка телефона
def is_valid_phone(phone):
    """Проверяет номер телефона для Таджикистана (+992)"""
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    # Форматы: +992XXXXXXXXX, 992XXXXXXXXX, 8XXXXXXXXX, 9XXXXXXXXX
    if phone.startswith('+992') and len(phone) == 13:
        return True
    elif phone.startswith('992') and len(phone) == 12:
        return True
    elif phone.startswith('8') and len(phone) == 10:
        return True
    elif phone.startswith('9') and len(phone) == 9:
        return True
    return False

# Форматирование номера
def format_phone(phone):
    """Приводит номер к формату +992XXXXXXXXX"""
    phone = phone.replace(' ', '').replace('-', '').replace('(', '').replace(')', '')
    
    if phone.startswith('+992'):
        return phone  # уже в правильном формате
    elif phone.startswith('992'):
        return '+' + phone  # +992XXXXXXXX
    elif phone.startswith('8') and len(phone) == 10:
        # 8XXXXXXXXX -> +992XXXXXXXXX
        return '+992' + phone[1:]
    elif phone.startswith('9') and len(phone) == 9:
        # 9XXXXXXXX -> +9929XXXXXXXX
        return '+992' + phone
    else:
        # Если ничего не подходит, просто добавляем +992
        return '+992' + phone

# Форматирование анкеты
def format_resume(user_data):
    resume = f"""
╔══════════════════════════════╗
║        📋 **АНКЕТА**         ║
╚══════════════════════════════╝

👤 **Личные данные:**
┌──────────────────────────────┐
│ 🆔 ID: {user_data.get('tg_id', '—')}
│ 📝 Имя: {user_data.get('first_name', '—')} {user_data.get('last_name', '')}
│ 🎂 Возраст: {user_data.get('age', '—')}
│ 📞 Телефон: {user_data.get('phone', '—')}
└──────────────────────────────┘

💼 **Профессия:**
┌──────────────────────────────┐
│ 🎯 Желаемая должность: {user_data.get('desired_job', '—')}
│ 💰 Зарплата: {user_data.get('salary', 'договорная')}
└──────────────────────────────┘

🛠 **Навыки:**
┌──────────────────────────────┐
│ {user_data.get('skills', '—')}
└──────────────────────────────┘

📎 **Резюме:** {'✅ Приложено' if user_data.get('resume') else '❌ Не приложено'}
📸 **Фото:** {'✅ Есть' if user_data.get('photo') else '❌ Нет'}

⏰ **Дата создания:** {datetime.now().strftime('%d.%m.%Y %H:%M')}
"""
    return resume