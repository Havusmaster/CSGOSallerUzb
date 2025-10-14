import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from shop import ShopHandler
from admin_panel import AdminHandler
from database import Database

# Configuration
BOT_TOKEN = "7504123410:AAEznGqRafbyrBx2e34HzsxztWV201HRMxE"
ADMIN_IDS = [1939282952, 5266027747]
WEBAPP_URL = "https://csgosalleruzb.onrender.com"  # Replace with your actual URL

# Initialize
logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
db = Database()
shop_handler = ShopHandler(db, bot, ADMIN_IDS)
admin_handler = AdminHandler(db, bot, ADMIN_IDS)


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Handle /start command"""
    user_id = message.from_user.id
    is_admin = user_id in ADMIN_IDS
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛍️ Открыть магазин / Do'konni ochish",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    if is_admin:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="⚙️ Админ-панель / Admin panel",
                web_app=WebAppInfo(url=f"{WEBAPP_URL}?admin=true")
            )
        ])
    
    welcome_text = (
        "👋 Добро пожаловать в магазин!\n"
        "Нажмите кнопку ниже, чтобы открыть каталог.\n\n"
        "👋 Do'konga xush kelibsiz!\n"
        "Katalogni ochish uchun quyidagi tugmani bosing."
    )
    
    await message.answer(welcome_text, reply_markup=keyboard)


@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Handle /help command"""
    help_text = (
        "ℹ️ Помощь / Yordam\n\n"
        "🛍️ Используйте кнопку 'Открыть магазин' для просмотра товаров\n"
        "💰 Нажмите 'Купить' на товаре, чтобы получить ссылку\n"
        "✉️ Свяжитесь с админом для завершения покупки\n\n"
        "🛍️ Mahsulotlarni ko'rish uchun 'Do'konni ochish' tugmasidan foydalaning\n"
        "💰 Havolani olish uchun mahsulotda 'Sotib olish' tugmasini bosing\n"
        "✉️ Xaridni yakunlash uchun admin bilan bog'laning"
    )
    await message.answer(help_text)


@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    """Handle data from WebApp"""
    data = message.web_app_data.data
    user_id = message.from_user.id
    
    # Handle different actions from WebApp
    if data.startswith("buy:"):
        product_id = data.split(":")[1]
        await shop_handler.handle_purchase(message, product_id)
    elif data.startswith("admin:"):
        if user_id in ADMIN_IDS:
            await admin_handler.handle_admin_action(message, data)
    else:
        await message.answer("✅ Данные получены / Ma'lumotlar qabul qilindi")


async def main():
    """Start the bot"""
    print("🤖 Bot is starting...")
    print(f"📱 WebApp URL: {WEBAPP_URL}")
    print(f"👥 Admin IDs: {ADMIN_IDS}")
    
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
