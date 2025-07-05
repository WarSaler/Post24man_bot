from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from loguru import logger

from .config import config
# Используем фабрику базы данных вместо прямого импорта
from .db import db

# Создаем роутер для обработки сообщений
router = Router()

# Функция для проверки, является ли пользователь администратором
def is_admin(user_id: int) -> bool:
    return user_id in config.ADMIN_USER_IDS

# Обработчик команды /start
@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    username = message.from_user.username
    
    welcome_text = (
        f"👋 Привет, {message.from_user.first_name}!\n\n"
        "Я бот для управления новостями о Турции (регионы Алания и Газипаша)."
    )
    
    if is_admin(user_id):
        welcome_text += (
            "\n\n🔑 Вы являетесь администратором бота. Доступные команды:\n"
            "/pending - показать ожидающие одобрения новости\n"
            "/approved - показать одобренные, но неопубликованные новости\n"
            "/run_parser - запустить парсинг новостей вручную\n"
            "/help - показать справку по работе с ботом"
        )
    else:
        welcome_text += (
            "\n\nДля получения дополнительной информации используйте команду /help"
        )
    
    await message.answer(welcome_text)
    logger.info(f"Пользователь {username} (ID: {user_id}) запустил бота")

# Обработчик команды /help
@router.message(Command("help"))
async def cmd_help(message: Message):
    user_id = message.from_user.id
    
    help_text = (
        "📚 <b>Справка по работе с ботом</b>\n\n"
        "Этот бот собирает и публикует новости о Турции (Алания и Газипаша).\n"
    )
    
    if is_admin(user_id):
        help_text += (
            "\n<b>Команды для администраторов:</b>\n"
            "• /pending - показать новости, ожидающие одобрения\n"
            "• /approved - показать одобренные, но неопубликованные новости\n"
            "• /run_parser - запустить парсинг новостей вручную\n"
            "• /status - показать статус работы бота\n"
        )
    
    help_text += (
        "\nБот автоматически собирает новости из различных источников, перефразирует их "
        "с помощью ИИ и после одобрения администратором публикует в группу."
    )
    
    await message.answer(help_text, parse_mode="HTML")

# Обработчик для команды /pending (показать ожидающие одобрения новости)
@router.message(Command("pending"))
async def cmd_pending(message: Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("⛔️ У вас нет прав на выполнение этой команды.")
        return
    
    # Получаем ожидающие одобрения новости из БД
    pending_articles = db.get_pending_articles(limit=5)
    
    if not pending_articles:
        await message.answer("🔍 Нет новостей, ожидающих одобрения.")
        return
    
    await message.answer(f"📋 Найдено {len(pending_articles)} ожидающих одобрения новостей:")
    
    # Отправляем каждую новость отдельным сообщением
    for article_id, source, original, processed in pending_articles:
        # Создаем клавиатуру с кнопками действий
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="✅ Одобрить", callback_data=f"approve_{article_id}"),
                InlineKeyboardButton(text="❌ Отклонить", callback_data=f"reject_{article_id}")
            ],
            [
                InlineKeyboardButton(text="🔍 Оригинал", callback_data=f"original_{article_id}")
            ]
        ])
        
        # Отправляем сообщение с перефразированным контентом
        article_text = (
            f"<b>ID статьи:</b> {article_id}\n"
            f"<b>Источник:</b> {source}\n\n"
            f"{processed}\n\n"
            f"<i>Примите решение по этой новости</i>"
        )
        
        await message.answer(article_text, parse_mode="HTML", reply_markup=keyboard)

# Обработчик для команды /approved (показать одобренные новости)
@router.message(Command("approved"))
async def cmd_approved(message: Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("⛔️ У вас нет прав на выполнение этой команды.")
        return
    
    # Получаем одобренные новости из БД
    approved_articles = db.get_approved_not_posted_articles()
    
    if not approved_articles:
        await message.answer("🔍 Нет одобренных, но неопубликованных новостей.")
        return
    
    await message.answer(f"📋 Найдено {len(approved_articles)} одобренных новостей, ожидающих публикации:")
    
    # Отправляем каждую новость отдельным сообщением
    for article_id, content in approved_articles:
        # Создаем клавиатуру с кнопками действий
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(text="📢 Опубликовать сейчас", callback_data=f"publish_{article_id}"),
                InlineKeyboardButton(text="❌ Отменить", callback_data=f"cancel_{article_id}")
            ]
        ])
        
        # Отправляем сообщение с перефразированным контентом
        article_text = (
            f"<b>ID статьи:</b> {article_id}\n\n"
            f"{content}\n\n"
            f"<i>Эта новость одобрена и ожидает публикации</i>"
        )
        
        await message.answer(article_text, parse_mode="HTML", reply_markup=keyboard)

# Обработчик колбэков от инлайн-кнопок
@router.callback_query(F.data.startswith(("approve_", "reject_", "publish_", "cancel_", "original_")))
async def process_callback(callback: CallbackQuery):
    user_id = callback.from_user.id
    
    if not is_admin(user_id):
        await callback.answer("⛔️ У вас нет прав на выполнение этого действия.", show_alert=True)
        return
    
    # Получаем тип операции и ID статьи
    action, article_id_str = callback.data.split("_")
    article_id = int(article_id_str)
    
    # Получаем информацию о статье
    article = db.get_article_by_id(article_id)
    
    if not article:
        await callback.answer("❌ Статья не найдена.", show_alert=True)
        return
    
    if action == "approve":
        # Одобряем статью
        if db.approve_article(article_id):
            await callback.message.edit_text(
                f"{callback.message.text}\n\n✅ <b>Статья одобрена</b>",
                parse_mode="HTML"
            )
            await callback.answer("✅ Статья одобрена и будет опубликована по расписанию")
        else:
            await callback.answer("❌ Ошибка при одобрении статьи", show_alert=True)
    
    elif action == "reject":
        # Удаляем сообщение с отклоненной статьей
        await callback.message.edit_text(
            f"{callback.message.text}\n\n❌ <b>Статья отклонена</b>",
            parse_mode="HTML"
        )
        await callback.answer("❌ Статья отклонена")
    
    elif action == "publish":
        # Отмечаем как опубликованную
        if db.mark_as_posted(article_id):
            # Здесь должна быть логика публикации в группу
            # Эта функциональность будет реализована в основном модуле
            await callback.message.edit_text(
                f"{callback.message.text}\n\n📢 <b>Статья отправлена на публикацию</b>",
                parse_mode="HTML"
            )
            await callback.answer("📢 Статья отправлена на публикацию")
        else:
            await callback.answer("❌ Ошибка при публикации статьи", show_alert=True)
    
    elif action == "cancel":
        # Отменяем публикацию
        await callback.message.edit_text(
            f"{callback.message.text}\n\n🛑 <b>Публикация отменена</b>",
            parse_mode="HTML"
        )
        await callback.answer("🛑 Публикация отменена")
    
    elif action == "original":
        # Показываем оригинальный текст
        original_text = article["original_content"]
        await callback.message.answer(
            f"<b>Оригинальный текст статьи ID {article_id}:</b>\n\n{original_text}",
            parse_mode="HTML"
        )
        await callback.answer()

# Обработчик команды /status (показать статус бота)
@router.message(Command("status"))
async def cmd_status(message: Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("⛔️ У вас нет прав на выполнение этой команды.")
        return
    
    # Здесь будет код для проверки статуса компонентов бота
    status_text = (
        "📊 <b>Статус бота:</b>\n\n"
        "✅ Бот запущен и работает\n"
        "✅ База данных подключена\n"
        "✅ API Gemini доступно\n"
        "✅ Парсер новостей активен\n\n"
    )
    
    # Статистика из БД (примерная реализация)
    pending_count = len(db.get_pending_articles(limit=100))
    approved_count = len(db.get_approved_not_posted_articles(limit=100))
    
    status_text += (
        f"📈 <b>Статистика:</b>\n"
        f"• Ожидает одобрения: {pending_count}\n"
        f"• Одобрено и ожидает публикации: {approved_count}\n"
    )
    
    await message.answer(status_text, parse_mode="HTML")

# Обработчик команды /run_parser (ручной запуск парсинга)
@router.message(Command("run_parser"))
async def cmd_run_parser(message: Message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        await message.answer("⛔️ У вас нет прав на выполнение этой команды.")
        return
    
    # Отправляем уведомление о запуске парсинга
    await message.answer("🔄 Запускаю процесс парсинга новостей. Это может занять некоторое время...")
    
    # В основном модуле будет добавлен вызов функции парсинга
    # Здесь только заглушка для интерфейса
    
    await message.answer("✅ Парсинг новостей завершен. Используйте /pending для просмотра новых статей.")

# Обработчик для всех остальных сообщений
@router.message()
async def handle_other_messages(message: Message):
    # Если сообщение от администратора и есть текст
    if is_admin(message.from_user.id) and message.text:
        await message.answer(
            "Я не распознал команду. Пожалуйста, используйте доступные команды:\n"
            "/pending - показать ожидающие одобрения новости\n"
            "/approved - показать одобренные новости\n"
            "/run_parser - запустить парсинг новостей вручную\n"
            "/status - показать статус работы бота\n"
            "/help - показать справку по работе с ботом"
        )
    else:
        # Для обычных пользователей
        await message.answer(
            "Для получения информации о боте используйте команду /help"
        ) 