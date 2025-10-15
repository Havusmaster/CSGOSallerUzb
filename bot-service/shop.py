import json
from aiogram import types, Bot
from database import db

async def handle_purchase_request(message: types.Message, bot: Bot):
    """Обработка запроса на покупку из WebApp"""
    try:
        data = json.loads(message.web_app_data.data)
        action = data.get("action")
        
        if action == "buy":
            item_id = data.get("item_id")
            item_type = data.get("item_type", "product")
            
            if item_type == "product":
                product = db.get_product(item_id)
                if product and product["status"] == "available":
                    # Отправляем уведомление пользователю
                    await message.answer(
                        f"✅ Запрос на покупку принят!\n\n"
                        f"📦 Товар: {product['name']}\n"
                        f"💰 Цена: ${product['price']}\n\n"
                        f"Администратор свяжется с вами в ближайшее время."
                    )
                    
                    # Уведомляем админов
                    admin_ids = [int(id.strip()) for id in message.bot.get("ADMIN_IDS", "").split(",")]
                    for admin_id in admin_ids:
                        try:
                            await bot.send_message(
                                admin_id,
                                f"🔔 Новый запрос на покупку!\n\n"
                                f"👤 Пользователь: @{message.from_user.username or 'без username'} (ID: {message.from_user.id})\n"
                                f"📦 Товар: {product['name']}\n"
                                f"💰 Цена: ${product['price']}"
                            )
                        except Exception as e:
                            print(f"Failed to notify admin {admin_id}: {e}")
                    
                    # Сохраняем покупку
                    db.add_purchase(message.from_user.id, item_id, "product", product['price'])
                else:
                    await message.answer("❌ Товар недоступен.")
            
            elif item_type == "auction":
                auction = db.get_auction(item_id)
                if auction and auction["status"] == "active":
                    await message.answer(
                        f"✅ Вы участвуете в аукционе!\n\n"
                        f"📦 Лот: {auction['name']}\n"
                        f"💰 Текущая ставка: ${auction['current_price']}\n\n"
                        f"Следите за обновлениями!"
                    )
                else:
                    await message.answer("❌ Аукцион недоступен.")
        
        elif action == "contact_admin":
            await message.answer(
                "📞 Для связи с администратором напишите @admin_username"
            )
            
    except Exception as e:
        print(f"Error in handle_purchase_request: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса.")
