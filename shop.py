from aiogram import Bot, types
from database import Database


class ShopHandler:
    """Handle shop-related operations"""
    
    def __init__(self, db: Database, bot: Bot, admin_ids: list):
        self.db = db
        self.bot = bot
        self.admin_ids = admin_ids
    
    async def handle_purchase(self, message: types.Message, product_id: str):
        """Handle purchase request from user"""
        user_id = message.from_user.id
        product = self.db.get_product(product_id)
        
        if not product:
            await message.answer(
                "❌ Товар не найден / Mahsulot topilmadi"
            )
            return
        
        if product["status"] == "sold":
            await message.answer(
                "❌ Товар уже продан / Mahsulot allaqachon sotilgan"
            )
            return
        
        # Record purchase attempt
        purchase_id = self.db.record_purchase(product_id, user_id)
        
        # Send product link to user
        response_text = (
            f"✅ Ссылка на товар:\n{product['link']}\n\n"
            f"📝 Отправьте эту ссылку администратору для завершения покупки.\n\n"
            f"✅ Mahsulot havolasi:\n{product['link']}\n\n"
            f"📝 Xaridni yakunlash uchun bu havolani administratorga yuboring."
        )
        
        # Create button to contact admin
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(
                text="✉️ Написать админу / Adminga yozish",
                url=f"tg://user?id={self.admin_ids[0]}"
            )]
        ])
        
        await message.answer(response_text, reply_markup=keyboard)
        
        # Notify admin about purchase attempt
        admin_notification = (
            f"🔔 Новая попытка покупки!\n\n"
            f"👤 Пользователь: {message.from_user.full_name} (@{message.from_user.username})\n"
            f"🆔 User ID: {user_id}\n"
            f"📦 Товар: {product['name']}\n"
            f"💰 Цена: {product['price']} ₽\n"
            f"🔗 ID покупки: {purchase_id}"
        )
        
        for admin_id in self.admin_ids:
            try:
                await self.bot.send_message(admin_id, admin_notification)
            except Exception as e:
                print(f"Failed to notify admin {admin_id}: {e}")
    
    def get_products_by_category(self, category: str = None):
        """Get products filtered by category"""
        return self.db.get_all_products(category=category, status="available")
    
    def get_product_details(self, product_id: str):
        """Get detailed product information"""
        return self.db.get_product(product_id)
