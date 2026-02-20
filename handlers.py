from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from sqlalchemy import select
from datetime import datetime
import asyncio
import json
import os

from config import config
from database import get_db
from models import User, SupportMessage
from keyboards import *
from utils import *

router = Router()

# Состояния
class Registration(StatesGroup):
    first_name = State()
    last_name = State()
    age = State()
    job_category = State()
    custom_job = State()
    skills = State()
    photo = State()
    phone = State()
    salary = State()
    resume_type = State()
    resume_text = State()
    resume_file = State()
    confirm = State()
    edit_field = State()
    edit_field_value = State()

class Support(StatesGroup):
    waiting_message = State()

# ===== СТАРТ =====
@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "👋 **Добро пожаловать в Job Seeker Bot!**\n\n"
        "Я помогу вам создать профессиональную анкету для поиска работы.\n"
        "Давайте начнем!",
        reply_markup=get_main_menu()
    )

# ===== ГЛАВНОЕ МЕНЮ =====
@router.message(F.text == "📋 Заполнить анкету")
async def start_registration(message: Message, state: FSMContext):
    await state.set_state(Registration.first_name)
    await message.answer(
        "📝 **Шаг 1 из 9**\n\n"
        "Введите ваше **имя** (только буквы):",
        reply_markup=get_cancel_keyboard()
    )

@router.message(F.text == "❓ FAQ")
async def show_faq(message: Message):
    faqs = get_faq()
    
    if not faqs:
        text = "❓ **Часто задаваемые вопросы**\n\n" \
               "1. Как создать резюме?\n   Заполните анкету в боте!\n\n" \
               "2. Кто увидит мою анкету?\n   Администратор компании.\n\n" \
               "3. Сколько ждать ответа?\n   До 24 часов."
    else:
        text = "❓ **Часто задаваемые вопросы**\n\n"
        for i, faq in enumerate(faqs, 1):
            text += f"{i}. **{faq['question']}**\n   {faq['answer']}\n\n"
    
    await message.answer(text, reply_markup=get_faq_keyboard())

@router.message(F.text == "📞 Связаться с нами")
async def start_support(message: Message, state: FSMContext):
    """Начало обращения в поддержку"""
    await state.set_state(Support.waiting_message)
    await message.answer(
        "📝 **Напишите ваше сообщение или вопрос**\n\n"
        "Опишите вашу проблему или задайте вопрос.\n"
        "Администратор свяжется с вами в ближайшее время.",
        reply_markup=get_cancel_keyboard()
    )

@router.message(Support.waiting_message)
async def process_support_message(message: Message, state: FSMContext):
    """Обработка сообщения в поддержку"""
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("❌ Действие отменено.", reply_markup=get_main_menu())
        return
    
    # Проверяем, что сообщение не пустое
    if not message.text or len(message.text.strip()) < 2:
        await message.answer("❌ Пожалуйста, напишите более подробное сообщение (минимум 2 символа).")
        return
    
    message_text = message.text.strip()
    
    # Сохраняем в БД и отправляем админам
    async for db in get_db():
        try:
            # Сохраняем в базу данных
            support_msg = SupportMessage(
                user_id=message.from_user.id,
                user_tg_id=message.from_user.id,
                user_name=message.from_user.full_name or "Неизвестно",
                message=message_text
            )
            db.add(support_msg)
            await db.commit()
            
            # Формируем информацию о пользователе
            user_info = (
                f"👤 **От:** {message.from_user.full_name}\n"
                f"🆔 **ID:** {message.from_user.id}\n"
                f"📝 **Username:** @{message.from_user.username if message.from_user.username else 'нет'}"
            )
            
            # Отправляем админам
            for admin_id in config.ADMIN_IDS:
                try:
                    await message.bot.send_message(
                        admin_id,
                        f"📨 **НОВОЕ СООБЩЕНИЕ В ПОДДЕРЖКУ**\n\n"
                        f"{user_info}\n\n"
                        f"💬 **Сообщение:**\n{message_text}"
                    )
                except Exception as e:
                    print(f"Не удалось отправить админу {admin_id}: {e}")
            
            # Подтверждение пользователю
            await message.answer(
                "✅ **Сообщение отправлено!**\n\n"
                "Администратор свяжется с вами в течение 24 часов.\n"
                "Спасибо за обращение!",
                reply_markup=get_main_menu()
            )
            
        except Exception as e:
            await message.answer(
                "❌ Произошла ошибка при отправке сообщения. Попробуйте позже.",
                reply_markup=get_main_menu()
            )
            print(f"Ошибка в support: {e}")
        break
    
    await state.clear()

@router.callback_query(F.data == "support")
async def support_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка инлайн кнопки поддержки"""
    await callback.message.delete()
    await state.set_state(Support.waiting_message)
    await callback.message.answer(
        "📝 **Напишите ваше сообщение или вопрос**\n\n"
        "Опишите вашу проблему или задайте вопрос.\n"
        "Администратор свяжется с вами в ближайшее время.",
        reply_markup=get_cancel_keyboard()
    )
    await callback.answer()

@router.callback_query(F.data == "back_to_main")
async def back_to_main(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer("Главное меню:", reply_markup=get_main_menu())
    await callback.answer()

# ===== РЕГИСТРАЦИЯ =====
@router.message(Registration.first_name)
async def process_first_name(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    name = message.text.strip()
    if not is_valid_name(name):
        await message.answer("❌ Имя должно содержать только буквы (минимум 2 символа). Попробуйте снова:")
        return
    
    await state.update_data(first_name=name)
    await state.set_state(Registration.last_name)
    await message.answer(
        "📝 **Шаг 2 из 9**\n\n"
        "Введите вашу **фамилию**:",
        reply_markup=get_cancel_keyboard()
    )

@router.message(Registration.last_name)
async def process_last_name(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    last_name = message.text.strip()
    if not is_valid_name(last_name):
        await message.answer("❌ Фамилия должна содержать только буквы. Попробуйте снова:")
        return
    
    await state.update_data(last_name=last_name)
    await state.set_state(Registration.age)
    await message.answer(
        "📝 **Шаг 3 из 9**\n\n"
        "Введите ваш **возраст** (от 14 до 100 лет):",
        reply_markup=get_cancel_keyboard()
    )
    
def get_job_keyboard():
    """Кнопки для выбора профессии"""
    from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
    
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

@router.message(Registration.age)
async def process_age(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    age = message.text.strip()
    if not is_valid_age(age):
        await message.answer("❌ Введите корректный возраст (число от 14 до 100):")
        return
    
    await state.update_data(age=int(age))
    await state.set_state(Registration.job_category)
    
    # ПОКАЗЫВАЕМ КНОПКИ С ПРОФЕССИЯМИ
    await message.answer(
        "💼 **Шаг 4 из 9**\n\n"
        "Выберите вашу профессию из списка или нажмите 'Другое...':",
        reply_markup=get_job_keyboard()  # Кнопки с профессиями
    )

@router.message(Registration.job_category)
async def process_job_category(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    # Если выбрали "Другое..."
    if message.text == "📝 Другое...":
        await state.set_state(Registration.custom_job)
        await message.answer(
            "📝 Введите вашу профессию вручную:",
            reply_markup=get_cancel_keyboard()
        )
        return
    
    # Если выбрали профессию из списка
    job = message.text.strip()
    # Убираем эмодзи из текста для сохранения
    job_clean = job.split(' ', 1)[-1] if ' ' in job else job
    
    await state.update_data(desired_job=job_clean)
    await state.set_state(Registration.skills)
    await message.answer(
        "📝 **Шаг 5 из 9**\n\n"
        "Введите ваши **навыки** через запятую.\n"
        "Например: Python, Excel, Photoshop, вождение",
        reply_markup=get_skip_keyboard()
    )

@router.message(Registration.custom_job)
async def process_custom_job(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    job = message.text.strip()
    if len(job) < 2:
        await message.answer("❌ Введите корректное название профессии (минимум 2 символа):")
        return
    
    await state.update_data(desired_job=job)
    await state.set_state(Registration.skills)
    await message.answer(
        "📝 **Шаг 5 из 9**\n\n"
        "Введите ваши **навыки** через запятую.\n"
        "Например: Python, Excel, Photoshop, вождение",
        reply_markup=get_skip_keyboard()
    )

@router.message(Registration.skills)
async def process_skills(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    if message.text == "⏭️ Пропустить":
        skills = "Не указаны"
    else:
        skills = message.text.strip()
    
    await state.update_data(skills=skills)
    await state.set_state(Registration.photo)
    await message.answer(
        "📸 **Шаг 6 из 9**\n\n"
        "Отправьте ваше **фото** (не файл, а именно фото):",
        reply_markup=get_cancel_keyboard()
    )

@router.message(Registration.photo, F.photo)
async def process_photo(message: Message, state: FSMContext):
    photo_id = message.photo[-1].file_id
    await state.update_data(photo=photo_id)
    await state.set_state(Registration.phone)
    await message.answer(
        "📞 **Шаг 7 из 9**\n\n"
        "Введите ваш **номер телефона**.\n\n"
        "Форматы для Таджикистана:\n"
        "• +992 123 456 789\n"
        "• 992 123 456 789\n"
        "• 8 123 456 789\n"
        "• 123 456 789",
        reply_markup=get_cancel_keyboard()
    )   
    
@router.message(Registration.phone)
async def process_phone(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer(
            "❌ Неверный формат телефона.\n\n"
            "Введите номер в одном из форматов:\n"
            "• +992 123 456 789\n"
            "• 992 123 456 789\n"
            "• 8 123 456 789\n"
            "• 123 456 789\n\n"
            "Попробуйте снова:"
        )
        return
    
    formatted_phone = format_phone(phone)
    await state.update_data(phone=formatted_phone)
    await state.set_state(Registration.salary)
    await message.answer(
        "💰 **Шаг 8 из 9**\n\n"
        "Укажите желаемую **зарплату** (в сомони) или нажмите 'Договорная':",
        reply_markup=get_salary_keyboard()
    )

@router.message(Registration.photo)
async def process_photo_invalid(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    await message.answer("❌ Пожалуйста, отправьте именно фото (изображение), а не файл.")

@router.message(Registration.phone)
async def process_phone(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    phone = message.text.strip()
    if not is_valid_phone(phone):
        await message.answer(
            "❌ Неверный формат телефона. Попробуйте снова:\n"
            "Примеры: +79991234567, 89991234567, 9991234567"
        )
        return
    
    formatted_phone = format_phone(phone)
    await state.update_data(phone=formatted_phone)
    await state.set_state(Registration.salary)
    await message.answer(
        "💰 **Шаг 8 из 9**\n\n"
        "Укажите желаемую **зарплату** (в рублях) или нажмите 'Договорная':",
        reply_markup=get_salary_keyboard()
    )

@router.message(Registration.salary)
async def process_salary(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    if message.text == "🤝 Договорная":
        salary = "договорная"
    else:
        salary_text = message.text.strip()
        if not salary_text.isdigit():
            await message.answer("❌ Введите число или нажмите 'Договорная':")
            return
        salary = f"{salary_text} сомони"  # ИСПРАВЛЕНО
    
    await state.update_data(salary=salary)
    await state.set_state(Registration.resume_type)
    
    await message.answer(
        "📎 **Шаг 9 из 9**\n\n"
        "Добавьте ваше **резюме**.\n"
        "Вы можете отправить:\n"
        "• Текст\n"
        "• Документ (PDF, DOC, DOCX)\n"
        "• Фото\n"
        "• Видео\n\n"
        "Или нажмите 'Пропустить', если нет резюме.",
        reply_markup=get_skip_keyboard()
    )

@router.message(Registration.resume_type)
async def process_resume(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        await state.clear()
        await message.answer("Регистрация отменена.", reply_markup=get_main_menu())
        return
    
    if message.text == "⏭️ Пропустить":
        await state.update_data(resume=None)
        await show_preview(message, state)
        return
    
    # Определяем тип контента
    if message.text:
        # Текст
        await state.update_data(resume={"type": "text", "content": message.text})
        await show_preview(message, state)
    elif message.document:
        # Документ
        file_id = message.document.file_id
        file_name = message.document.file_name
        await state.update_data(resume={"type": "document", "file_id": file_id, "name": file_name})
        await show_preview(message, state)
    elif message.photo:
        # Фото
        file_id = message.photo[-1].file_id
        await state.update_data(resume={"type": "photo", "file_id": file_id})
        await show_preview(message, state)
    elif message.video:
        # Видео
        file_id = message.video.file_id
        await state.update_data(resume={"type": "video", "file_id": file_id})
        await show_preview(message, state)
    else:
        await message.answer("❌ Пожалуйста, отправьте текст, документ, фото или видео.")
        return

@router.message(Registration.resume_type, F.document)
async def process_resume_document(message: Message, state: FSMContext):
    file_id = message.document.file_id
    file_name = message.document.file_name
    await state.update_data(resume={"type": "document", "file_id": file_id, "name": file_name})
    await show_preview(message, state)

@router.message(Registration.resume_type, F.photo)
async def process_resume_photo(message: Message, state: FSMContext):
    file_id = message.photo[-1].file_id
    await state.update_data(resume={"type": "photo", "file_id": file_id})
    await show_preview(message, state)

@router.message(Registration.resume_type, F.video)
async def process_resume_video(message: Message, state: FSMContext):
    file_id = message.video.file_id
    await state.update_data(resume={"type": "video", "file_id": file_id})
    await show_preview(message, state)

async def show_preview(message: Message, state: FSMContext):
    data = await state.get_data()
    
    # Формируем анкету
    resume_text = format_resume({
        'tg_id': message.from_user.id,
        'first_name': data.get('first_name'),
        'last_name': data.get('last_name'),
        'age': data.get('age'),
        'desired_job': data.get('desired_job'),
        'skills': data.get('skills'),
        'phone': data.get('phone'),
        'salary': data.get('salary'),
        'photo': data.get('photo'),
        'resume': data.get('resume')
    })
    
    # Отправляем фото с анкетой
    if data.get('photo'):
        await message.answer_photo(
            photo=data['photo'],
            caption=resume_text,
            reply_markup=get_confirm_keyboard()
        )
    else:
        await message.answer(
            resume_text,
            reply_markup=get_confirm_keyboard()
        )
    
    await state.set_state(Registration.confirm)

# ===== ПОДТВЕРЖДЕНИЕ =====
@router.callback_query(Registration.confirm, F.data == "confirm_send")
async def confirm_send(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    
    # Сохраняем в БД
    async for db in get_db():
        user = User(
            tg_id=callback.from_user.id,
            username=callback.from_user.username,
            first_name=data.get('first_name'),
            last_name=data.get('last_name'),
            age=data.get('age'),
            desired_job=data.get('desired_job'),
            skills=data.get('skills'),
            photo_file_id=data.get('photo'),
            phone=data.get('phone'),
            salary_expectation=data.get('salary'),
            resume=data.get('resume'),
            is_completed=True
        )
        db.add(user)
        await db.commit()
        
        # Отправляем админам
        resume_info = format_resume({
            'tg_id': callback.from_user.id,
            'first_name': data.get('first_name'),
            'last_name': data.get('last_name'),
            'age': data.get('age'),
            'desired_job': data.get('desired_job'),
            'skills': data.get('skills'),
            'phone': data.get('phone'),
            'salary': data.get('salary'),
            'photo': '✅' if data.get('photo') else '❌',
            'resume': '✅' if data.get('resume') else '❌'
        })
        
        admin_text = f"📋 **Новая анкета!**\n\n{resume_info}"
        
        for admin_id in config.ADMIN_IDS:
            try:
                if data.get('photo'):
                    await callback.bot.send_photo(
                        admin_id,
                        data['photo'],
                        caption=admin_text
                    )
                else:
                    await callback.bot.send_message(admin_id, admin_text)
                
                # Если есть резюме, отправляем
                if data.get('resume'):
                    resume = data['resume']
                    if resume['type'] == 'text':
                        await callback.bot.send_message(admin_id, f"📎 **Резюме (текст):**\n\n{resume['content']}")
                    elif resume['type'] == 'document':
                        await callback.bot.send_document(admin_id, resume['file_id'], caption="📎 Резюме")
                    elif resume['type'] == 'photo':
                        await callback.bot.send_photo(admin_id, resume['file_id'], caption="📎 Резюме")
                    elif resume['type'] == 'video':
                        await callback.bot.send_video(admin_id, resume['file_id'], caption="📎 Резюме")
            except:
                pass
    
    # Отправляем совет
    tip = get_random_tip()
    await callback.message.delete()
    await callback.message.answer(
        f"✅ **Анкета успешно отправлена!**\n\n"
        f"Спасибо за доверие! Администратор свяжется с вами в ближайшее время.\n\n"
        f"💫 **Совет от бота:**\n{tip}",
        reply_markup=get_main_menu()
    )
    
    await state.clear()
    await callback.answer()

@router.callback_query(Registration.confirm, F.data == "confirm_edit")
async def confirm_edit(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "✏️ **Что хотите изменить?**",
        reply_markup=get_edit_keyboard()
    )
    await state.set_state(Registration.edit_field)
    await callback.answer()

@router.callback_query(Registration.confirm, F.data == "confirm_cancel")
async def confirm_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.delete()
    await callback.message.answer(
        "❌ Анкета удалена. Вы можете начать заново в любой момент.",
        reply_markup=get_main_menu()
    )
    await callback.answer()

# ===== РЕДАКТИРОВАНИЕ =====
@router.callback_query(Registration.edit_field)
async def edit_field(callback: CallbackQuery, state: FSMContext):
    field = callback.data
    
    if field == "edit_done":
        await show_preview(callback.message, state)
        await callback.answer()
        return
    
    field_map = {
        "edit_name": ("first_name", "Введите новое имя:"),
        "edit_lastname": ("last_name", "Введите новую фамилию:"),
        "edit_age": ("age", "Введите новый возраст:"),
        "edit_job": ("desired_job", "Введите новую профессию:"),
        "edit_skills": ("skills", "Введите новые навыки:"),
        "edit_photo": ("photo", "Отправьте новое фото:"),
        "edit_phone": ("phone", "Введите новый номер телефона:"),
        "edit_salary": ("salary", "Укажите новую зарплату:"),
        "edit_resume": ("resume", "Отправьте новое резюме (текст/документ/фото/видео):")
    }
    
    if field in field_map:
        key, prompt = field_map[field]
        await state.update_data(edit_field=key)
        await state.set_state(Registration.edit_field_value)
        await callback.message.delete()
        await callback.message.answer(f"✏️ {prompt}", reply_markup=get_cancel_keyboard())
    
    await callback.answer()

@router.message(Registration.edit_field_value)
async def process_edit_value(message: Message, state: FSMContext):
    if message.text == "❌ Отмена":
        data = await state.get_data()
        await show_preview(message, state)
        return
    
    data = await state.get_data()
    field = data.get('edit_field')
    
    if field in ['first_name', 'last_name']:
        if not is_valid_name(message.text.strip()):
            await message.answer("❌ Имя должно содержать только буквы. Попробуйте снова:")
            return
        await state.update_data({field: message.text.strip()})
        await show_preview(message, state)
        
    elif field == 'age':
        if not is_valid_age(message.text.strip()):
            await message.answer("❌ Введите корректный возраст (14-100):")
            return
        await state.update_data({field: int(message.text.strip())})
        await show_preview(message, state)
        
    elif field == 'phone':
        if not is_valid_phone(message.text.strip()):
            await message.answer("❌ Неверный формат телефона. Попробуйте снова:")
            return
        await state.update_data({field: format_phone(message.text.strip())})
        await show_preview(message, state)
        
    elif field == 'salary':
        if message.text == "🤝 Договорная":
            await state.update_data({field: "договорная"})
        elif message.text.isdigit():
            await state.update_data({field: f"{message.text} сомони"})
        else:
            await message.answer("❌ Введите число или нажмите 'Договорная':")
            return
        await show_preview(message, state)
        
    elif field == 'photo':
        if not message.photo:
            await message.answer("❌ Пожалуйста, отправьте фото:")
            return
        await state.update_data({field: message.photo[-1].file_id})
        await show_preview(message, state)
        
    elif field == 'resume':
        if message.text:
            await state.update_data({field: {"type": "text", "content": message.text}})
        elif message.document:
            await state.update_data({field: {"type": "document", "file_id": message.document.file_id, "name": message.document.file_name}})
        elif message.photo:
            await state.update_data({field: {"type": "photo", "file_id": message.photo[-1].file_id}})
        elif message.video:
            await state.update_data({field: {"type": "video", "file_id": message.video.file_id}})
        else:
            await message.answer("❌ Пожалуйста, отправьте текст, документ, фото или видео:")
            return
        await show_preview(message, state)
        
    else:
        await state.update_data({field: message.text.strip()})
        await show_preview(message, state)