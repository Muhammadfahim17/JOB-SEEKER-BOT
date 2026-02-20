from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder


def get_main_menu():
    buttons = [
        [KeyboardButton(text="📋 Заполнить анкету")],
        [KeyboardButton(text="❓ FAQ"), KeyboardButton(text="📞 Связаться с нами")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_cancel_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def get_skip_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="⏭️ Пропустить"), KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )

def get_salary_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="🤝 Договорная")], [KeyboardButton(text="❌ Отмена")]],
        resize_keyboard=True
    )
    

def get_job_keyboard():
    """Кнопки для выбора профессии"""
    buttons = [
        [KeyboardButton(text="💻 Программист")],
        [KeyboardButton(text="🎨 Дизайнер")],
        [KeyboardButton(text="📊 Маркетолог")],
        [KeyboardButton(text="📚 Менеджер")],
        [KeyboardButton(text="💰 Бухгалтер")],
        [KeyboardButton(text="🚚 Водитель")],
        [KeyboardButton(text="🏗️ Строитель")],
        [KeyboardButton(text="🏥 Врач")],
        [KeyboardButton(text="📝 Другое...")]
    ]
    return ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)

def get_confirm_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Всё верно, отправить", callback_data="confirm_send"))
    builder.add(InlineKeyboardButton(text="✏️ Изменить анкету", callback_data="confirm_edit"))
    builder.add(InlineKeyboardButton(text="❌ Отменить и удалить", callback_data="confirm_cancel"))
    builder.adjust(1)
    return builder.as_markup()

def get_edit_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="👤 Имя", callback_data="edit_name"))
    builder.add(InlineKeyboardButton(text="👥 Фамилия", callback_data="edit_lastname"))
    builder.add(InlineKeyboardButton(text="🎂 Возраст", callback_data="edit_age"))
    builder.add(InlineKeyboardButton(text="💼 Должность", callback_data="edit_job"))
    builder.add(InlineKeyboardButton(text="🛠 Навыки", callback_data="edit_skills"))
    builder.add(InlineKeyboardButton(text="📸 Фото", callback_data="edit_photo"))
    builder.add(InlineKeyboardButton(text="📞 Телефон", callback_data="edit_phone"))
    builder.add(InlineKeyboardButton(text="💰 Зарплата", callback_data="edit_salary"))
    builder.add(InlineKeyboardButton(text="📎 Резюме", callback_data="edit_resume"))
    builder.add(InlineKeyboardButton(text="✅ Готово", callback_data="edit_done"))
    builder.adjust(2)
    return builder.as_markup()

def back_button(callback_data="back"):
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data=callback_data))
    return builder.as_markup()

def get_faq_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📞 Связаться с нами", callback_data="support"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    builder.adjust(1)
    return builder.as_markup()

def get_support_keyboard():
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="✅ Отправить", callback_data="support_send"))
    builder.add(InlineKeyboardButton(text="❌ Отмена", callback_data="support_cancel"))
    builder.adjust(2)
    return builder.as_markup()


def get_faq_keyboard():
    """Клавиатура для FAQ"""

    
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="📞 Связаться с нами", callback_data="support"))
    builder.add(InlineKeyboardButton(text="🔙 Назад", callback_data="back_to_main"))
    builder.adjust(1)
    return builder.as_markup()