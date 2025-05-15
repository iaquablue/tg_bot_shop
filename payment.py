from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import CallbackQueryHandler, ContextTypes
from database import get_user_balance, update_user_balance
from config import CRYPTOBOT_API_KEY
import requests
import logging

logger = logging.getLogger(__name__)

async def start_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        # Логируем данные
        logger.info(f"Callback data: {query.data}")
        
        # Разбираем данные товара (формат: prod_<id>_<price>)
        _, product_id, price = query.data.split('_')
        
        context.user_data['current_order'] = {
            'product_id': product_id,
            'price': float(price),
            'quantity': 1
        }
        
        keyboard = [
            [InlineKeyboardButton("💰 С баланса", callback_data="pay_balance")],
            [InlineKeyboardButton("🪙 CryptoBot", callback_data="pay_crypto")],
            [InlineKeyboardButton("❌ Отменить", callback_data="cancel_order")]
        ]
        
        await query.edit_message_text(
            f"💳 Оплата товара #{product_id}\n"
            f"Сумма: {price} руб.\n\n"
            "Выберите способ оплаты:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        logger.error(f"Ошибка в start_payment: {e}")
        await query.edit_message_text("❌ Ошибка обработки заказа")

async def handle_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    try:
        method = query.data
        logger.info(f"Выбран метод: {method}")
        
        order = context.user_data.get('current_order')
        if not order:
            await query.edit_message_text("❌ Заказ не найден")
            return

        if method == "pay_balance":
            user_id = update.effective_user.id
            balance = get_user_balance(user_id)
            
            if balance >= order['price']:
                update_user_balance(user_id, -order['price'])
                await query.edit_message_text(
                    f"✅ Оплачено с баланса!\n"
                    f"Товар #{order['product_id']}\n"
                    f"Списано: {order['price']} руб.\n"
                    f"Новый баланс: {balance - order['price']:.2f} руб."
                )
            else:
                await query.edit_message_text(
                    f"❌ Недостаточно средств\n"
                    f"Нужно: {order['price']} руб.\n"
                    f"Ваш баланс: {balance:.2f} руб."
                )

        elif method == "pay_crypto":
            response = requests.post(
                "https://pay.crypt.bot/api/createInvoice",
                headers={"Crypto-Pay-API-Token": CRYPTOBOT_API_KEY},
                json={
                    "asset": "USDT",
                    "amount": str(order['price']),
                    "description": f"Товар #{order['product_id']}"
                }
            )
            data = response.json()
            
            if data.get('ok'):
                await query.edit_message_text(
                    f"👉 [Оплатить {order['price']} USDT]({data['result']['pay_url']})\n\n"
                    "После оплаты товар будет выдан автоматически.",
                    parse_mode="Markdown"
                )
            else:
                raise Exception(data.get('error', 'Ошибка CryptoBot'))

        elif method == "cancel_order":
            await query.edit_message_text("❌ Заказ отменен")
            context.user_data.pop('current_order', None)

    except Exception as e:
        logger.error(f"Ошибка в handle_payment: {e}")
        await query.edit_message_text("❌ Ошибка при обработке платежа")

def get_payment_handlers():
    return [
        CallbackQueryHandler(start_payment, pattern="^prod_"),
        CallbackQueryHandler(handle_payment, pattern="^pay_|cancel_order")
    ]