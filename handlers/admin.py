from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackContext, ConversationHandler
import sqlite3
import logging

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Состояния диалога
INPUT_DATA, CONFIRM = range(2)

async def is_admin(user_id: int) -> bool:
    """Проверяет, является ли пользователь админом"""
    conn = sqlite3.connect('data/products.db')
    cursor = conn.cursor()
    cursor.execute("SELECT role FROM users WHERE user_id=?", (user_id,))
    role = cursor.fetchone()
    conn.close()
    return role and role[0] == 'admin'

async def grant_admin(update: Update, context: CallbackContext):
    """Выдача прав админа (/grant_admin @username)"""
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Только админы могут использовать эту команду!")
        return

    if not context.args:
        await update.message.reply_text("Укажите username: /grant_admin @username")
        return

    target_username = context.args[0].strip('@')
    conn = sqlite3.connect('data/products.db')
    cursor = conn.cursor()
    
    try:
        cursor.execute(
            "UPDATE users SET role='admin' WHERE username=?",
            (target_username,)
        )
        conn.commit()
        await update.message.reply_text(f"✅ Пользователь @{target_username} теперь админ!")
    except Exception as e:
        await update.message.reply_text(f"❌ Ошибка: {e}")
    finally:
        conn.close()

async def add_product_start(update: Update, context: CallbackContext):
    """Начало диалога добавления товара (только для админов)"""
    if not await is_admin(update.effective_user.id):
        await update.message.reply_text("❌ Недостаточно прав!")
        return ConversationHandler.END

    await update.message.reply_text(
        "Введите данные товара в формате:\n"
        "Название | Цена | Категория | Подкатегория\n"
        "Пример: Футболка | 1990 | Одежда | Мужская"
    )
    return INPUT_DATA

async def input_product_data(update: Update, context: CallbackContext):
    """Обработка введенных данных"""
    user_input = update.message.text
    logger.info("Received input: %s", user_input)
    
    try:
        # Проверка и разбор данных
        if user_input.count('|') != 3:
            raise ValueError("Нужно ровно 3 разделителя '|'")
            
        name, price, category, subcategory = map(str.strip, user_input.split('|'))
        
        if not price.isdigit():
            raise ValueError("Цена должна быть целым числом")
            
        if not all([name, category, subcategory]):
            raise ValueError("Все поля должны быть заполнены")

        # Сохраняем данные
        context.user_data["new_product"] = {
            "name": name,
            "price": int(price),
            "category": category,
            "subcategory": subcategory
        }
        logger.debug("Parsed product data: %s", context.user_data["new_product"])

        # Создаем клавиатуру
        keyboard = [
            [InlineKeyboardButton("✅ Сохранить", callback_data="save_product")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel")]
        ]
        
        await update.message.reply_text(
            "Проверьте данные:\n\n"
            f"🏷 Название: {name}\n"
            f"💰 Цена: {price}₽\n"
            f"📂 Категория: {category}\n"
            f"📌 Подкатегория: {subcategory}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return CONFIRM
        
    except ValueError as e:
        logger.error("Input error: %s", str(e))
        await update.message.reply_text(
            f"❌ Ошибка: {str(e)}\n\n"
            "Правильный формат:\n"
            "Название | Цена | Категория | Подкатегория\n"
            "Пример: Кроссовки | 5990 | Обувь | Спорт"
        )
        return ConversationHandler.END

async def save_product(update: Update, context: CallbackContext):
    """Сохранение товара в БД"""
    try:
        data = context.user_data["new_product"]
        logger.info("Saving product: %s", data)
        
        conn = sqlite3.connect('data/products.db')
        cursor = conn.cursor()
        
        cursor.execute(
            "INSERT INTO products (name, price, category, subcategory) VALUES (?, ?, ?, ?)",
            (data["name"], data["price"], data["category"], data["subcategory"])
        )
        conn.commit()
        
        await update.callback_query.answer("✅ Товар сохранен!")
        await update.callback_query.edit_message_text(
            f"Товар успешно добавлен:\n{data['name']} - {data['price']}₽"
        )
        logger.info("Product saved successfully")
        
    except Exception as e:
        logger.error("Save error: %s", str(e))
        await update.callback_query.answer("❌ Ошибка сохранения")
    finally:
        conn.close()
        return ConversationHandler.END

async def cancel(update: Update, context: CallbackContext):
    """Отмена операции"""
    logger.info("User canceled operation")
    await update.callback_query.answer("❌ Операция отменена")
    await update.callback_query.edit_message_text("Добавление товара отменено")
    return ConversationHandler.END