from aiogram import Bot, types
from database import Database


class AdminHandler:
    """Handle admin panel operations"""
    
    def __init__(self, db: Database, bot: Bot, admin_ids: list):
        self.db = db
        self.bot = bot
        self.admin_ids = admin_ids
    
    def is_admin(self, user_id: int) -> bool:
        """Check if user is admin"""
        return user_id in self.admin_ids
    
    async def handle_admin_action(self, message: types.Message, data: str):
        """Handle admin actions from WebApp"""
        user_id = message.from_user.id
        
        if not self.is_admin(user_id):
            await message.answer("❌ Доступ запрещен / Ruxsat berilmagan")
            return
        
        action_parts = data.split(":")
        action = action_parts[1] if len(action_parts) > 1 else ""
        
        if action == "product_created":
            await message.answer("✅ Товар успешно создан / Mahsulot muvaffaqiyatli yaratildi")
        elif action == "auction_created":
            await message.answer("✅ Лот создан / Lot yaratildi")
        elif action == "product_deleted":
            await message.answer("✅ Товар удален / Mahsulot o'chirildi")
        elif action == "status_changed":
            await message.answer("✅ Статус изменен / Holat o'zgartirildi")
        else:
            await message.answer("✅ Действие выполнено / Harakat bajarildi")
    
    def create_product(self, name: str, price: float, category: str,
                      description: str, photo_url: str, link: str,
                      float_value: float = None) -> str:
        """Create a new product"""
        return self.db.add_product(
            name=name,
            price=price,
            category=category,
            description=description,
            photo_url=photo_url,
            link=link,
            float_value=float_value
        )
    
    def create_auction(self, name: str, starting_price: float, category: str,
                      description: str, photo_url: str, link: str,
                      float_value: float = None) -> str:
        """Create a new auction lot"""
        return self.db.add_auction(
            name=name,
            starting_price=starting_price,
            category=category,
            description=description,
            photo_url=photo_url,
            link=link,
            float_value=float_value
        )
    
    def get_all_products(self):
        """Get all products for admin view"""
        return self.db.get_all_products()
    
    def get_all_auctions(self):
        """Get all auctions for admin view"""
        return self.db.get_all_auctions()
    
    def update_product_status(self, product_id: str, status: str) -> bool:
        """Update product status"""
        return self.db.set_product_status(product_id, status)
    
    def delete_product(self, product_id: str) -> bool:
        """Delete a product"""
        return self.db.delete_product(product_id)
    
    def delete_auction(self, auction_id: str) -> bool:
        """Delete an auction"""
        return self.db.delete_auction(auction_id)
