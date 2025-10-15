import json
import logging
from aiogram import types, Bot, F
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from database import db

# Настройка логирования
logger = logging.getLogger(__name__)

# Статусы заказов
ORDER_STATUSES = {
    'pending': '⏳ Ожидает обработки',
    'processing': '🔄 В обработке',
    'completed': '✅ Завершен',
    'cancelled': '❌ Отменен'
}

async def handle_purchase_request(message: types.Message, bot: Bot):
    """Обработка запроса на покупку из WebApp"""
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        user_id = message.from_user.id
        username = f"@{message.from_user.username}" if message.from_user.username else "без username"
        
        if action == "buy":
            item_id = data.get("item_id")
            item_type = data.get("item_type", "product")
            
            if item_type == "product":
                product = db.get_product(item_id)
                if not product:
                    return await message.answer("❌ Товар не найден.")
                    
                if product["status"] != "available":
                    return await message.answer("❌ Этот товар временно недоступен.")
                
                # Создаем заказ
                order_id = db.create_order(
                    user_id=user_id,
                    item_id=item_id,
                    item_type=item_type,
                    amount=product['price'],
                    status='pending'
                )
                
                if not order_id:
                    return await message.answer("❌ Не удалось создать заказ. Попробуйте позже.")
                
                # Клавиатура с действиями
                keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(
                        text="📦 Мои заказы",
                        callback_data=f"my_orders_{user_id}"
                    )],
                    [InlineKeyboardButton(
                        text="📞 Связаться с поддержкой",
                        callback_data="contact_support"
                    )]
                ])
                
                # Уведомление пользователю
                await message.answer(
                    f"✅ <b>Заказ #{order_id} создан!</b>\n\n"
                    f"📦 <b>Товар:</b> {product['name']}\n"
                    f"💰 <b>Цена:</b> ${product['price']:.2f}\n"
                    f"📝 <b>Статус:</b> {ORDER_STATUSES['pending']}\n\n"
                    f"Наш менеджер свяжется с вами в ближайшее время для уточнения деталей.",
                    reply_markup=keyboard,
                    parse_mode='HTML'
                )
                
                # Уведомление админам
                admin_ids = bot.get("ADMIN_IDS", [])
                admin_keyboard = InlineKeyboardMarkup(inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="✅ Принять заказ",
                            callback_data=f"process_order_{order_id}"
                        ),
                        InlineKeyboardButton(
                            text="❌ Отклонить",
                            callback_data=f"cancel_order_{order_id}"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            text="👤 Профиль покупателя",
                            url=f"tg://user?id={user_id}"
                        )
                    ]
                ])
                
                for admin_id in admin_ids:
                    try:
                        await bot.send_message(
                            admin_id,
                            f"🛒 <b>Новый заказ #{order_id}</b>\n\n"
                            f"👤 <b>Покупатель:</b> {username} (ID: {user_id})\n"
                            f"📦 <b>Товар:</b> {product['name']}\n"
                            f"💰 <b>Цена:</b> ${product['price']:.2f}\n"
                            f"📅 <b>Дата:</b> {db.get_order(order_id)['created_at']}",
                            reply_markup=admin_keyboard,
                            parse_mode='HTML'
                        )
                    except Exception as e:
                        logger.error(f"Failed to notify admin {admin_id}: {e}")
                
            elif item_type == "auction":
                auction = db.get_auction(item_id)
                if not auction:
                    return await message.answer("❌ Аукцион не найден.")
                    
                if auction["status"] != "active":
                    return await message.answer("❌ Этот аукцион завершен или приостановлен.")
                
                # Логика для участия в аукционе
                # ...
                
                await message.answer(
                    f"🎯 <b>Вы участвуете в аукционе!</b>\n\n"
                    f"📦 <b>Лот:</b> {auction['name']}\n"
                    f"💰 <b>Текущая ставка:</b> ${auction['current_price']:.2f}\n"
                    f"⏳ <b>Завершение:</b> {auction['end_time']}\n\n"
                    f"Мы уведомим вас, если вашу ставку перебьют.",
                    parse_mode='HTML'
                )
        
        elif action == "order_status":
            order_id = data.get("order_id")
            order = db.get_order(order_id)
            
            if not order:
                return await message.answer("❌ Заказ не найден.")
                
            if order['user_id'] != user_id and user_id not in bot.get("ADMIN_IDS", []):
                return await message.answer("❌ У вас нет доступа к этому заказу.")
                
            status_text = ORDER_STATUSES.get(order['status'], order['status'])
            
            await message.answer(
                f"📦 <b>Информация о заказе #{order_id}</b>\n\n"
                f"📝 <b>Статус:</b> {status_text}\n"
                f"💰 <b>Сумма:</b> ${order['amount']:.2f}\n"
                f"📅 <b>Дата создания:</b> {order['created_at']}",
                parse_mode='HTML'
            )
            
        elif action == "contact_admin":
            support_username = bot.get("SUPPORT_USERNAME", "@admin_username")
            await message.answer(
                f"📞 <b>Служба поддержки</b>\n\n"
                f"По всем вопросам обращайтесь к нашему менеджеру: {support_username}\n"
                f"Мы работаем для вас 24/7!",
                parse_mode='HTML',
                disable_web_page_preview=True
            )
            
    except json.JSONDecodeError:
        await message.answer("❌ Ошибка при обработке данных. Пожалуйста, попробуйте еще раз.")
    except Exception as e:
        logger.error(f"Error in handle_purchase_request: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла непредвиденная ошибка. "
            "Пожалуйста, попробуйте позже или свяжитесь с поддержкой."
        )
