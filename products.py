from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, CommandHandler, ContextTypes
from database import create_connection
import logging

logger = logging.getLogger(__name__)

async def show_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # Получаем объект сообщения (работает и для команд, и для callback)
        effective_message = update.message or update.callback_query.message
        
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT category_id, name FROM categories ORDER BY category_id")
        categories = cursor.fetchall()
        
        keyboard = [
            [InlineKeyboardButton(name, callback_data=f"cat_{category_id}")]
            for category_id, name in categories
        ]
        
        await effective_message.reply_text(
            "🏪 Выберите категорию:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Ошибка в show_main_menu: {e}")
        if update.callback_query:
            await update.callback_query.answer("❌ Ошибка загрузки меню")
        else:
            await update.message.reply_text("❌ Ошибка загрузки меню")
    finally:
        if conn:
            conn.close()

async def handle_category(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        category_id = int(query.data.split('_')[1])
        conn = create_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT product_id, name, price FROM products WHERE category_id = ?",
            (category_id,)
        )
        products = cursor.fetchall()
        
        keyboard = [
            [InlineKeyboardButton(
                f"{name} - {price:.2f} руб.", 
                callback_data=f"prod_{product_id}_{price}"
            )]
            for product_id, name, price in products
        ]
        
        # Добавляем кнопку "Назад"
        keyboard.append([InlineKeyboardButton("⬅️ Назад", callback_data="back_to_menu")])
        
        await query.edit_message_text(
            "📦 Выберите товар:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Ошибка в handle_category: {e}")
        await query.edit_message_text("❌ Ошибка загрузки товаров")
    finally:
        if conn:
            conn.close()

def get_products_handlers():
    return [
        CommandHandler("menu", show_main_menu),
        CallbackQueryHandler(handle_category, pattern="^cat_"),
        CallbackQueryHandler(show_main_menu, pattern="^back_to_menu$")
    ]