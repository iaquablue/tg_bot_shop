from telegram.ext import ApplicationBuilder, CommandHandler
from products import get_products_handlers
from payment import get_payment_handlers
from config import BOT_TOKEN
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start(update, context):
    await update.message.reply_text(
        "👋 Добро пожаловать!\n"
        "Используйте /menu для выбора товаров"
    )

async def help(update, context):
    await update.message.reply_text(
        "ℹ️ Доступные команды:\n"
        "/start - Начало работы\n"
        "/menu - Каталог товаров\n"
        "/balance - Проверить баланс"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    
    # Основные команды
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help))
    
    # Обработчики из модулей
    for handler in get_products_handlers() + get_payment_handlers():
        app.add_handler(handler)
    
    logger.info("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()