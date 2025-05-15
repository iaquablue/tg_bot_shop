from telegram import Update
from telegram.ext import CallbackContext
import sqlite3

async def handle_messages(update: Update, context: CallbackContext):
    """Обработчик текстовых сообщений (корзина)"""
    user_id = update.message.from_user.id
    text = update.message.text
    
    if text.lower() == "корзина":
        conn = sqlite3.connect('data/products.db')
        cursor = conn.cursor()
        cursor.execute("SELECT name FROM products LIMIT 3")
        items = [row[0] for row in cursor.fetchall()]
        
        await update.message.reply_text(
            f"Ваша корзина (тест):\n" + "\n".join(items)
        )
        conn.close()