import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from shop import ShopHandler
from admin_panel import AdminHandler
from database import Database

# Configuration
BOT_TOKEN = "7504123410:AAEznGqRafbyrBx2e34HzsxztWV201HRMxE"
ADMIN_IDS = [1939282952, 5266027747]
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://csgosalleruzb-1.onrender.com")  # Set in Render env vars

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_HOST = os.getenv("RENDER_EXTERNAL_URL", "https://csgosalleruzb-1.onrender.com")  # Set in Render
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"
WEB_SERVER_HOST = "0.0.0.0"
WEB_SERVER_PORT = int(os.getenv("PORT", 8080))  # Render provides PORT env variable

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


async def health_check(request):
    """Health check endpoint for Render"""
    return web.Response(text="OK")


async def on_startup(app):
    """Set webhook on startup"""
    await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
    print(f"🌐 Webhook set to: {WEBHOOK_URL}")
    print(f"🚀 Server running on {WEB_SERVER_HOST}:{WEB_SERVER_PORT}")


async def on_shutdown(app):
    """Delete webhook on shutdown"""
    await bot.delete_webhook()
    print("🛑 Webhook deleted")


def main():
    """Start the bot with webhook"""
    print("🤖 Bot is starting with webhook...")
    print(f"📱 WebApp URL: {WEBAPP_URL}")
    print(f"👥 Admin IDs: {ADMIN_IDS}")
    
    # Create aiohttp application
    app = web.Application()
    
    # Setup webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Add health check route
    app.router.add_get("/", health_check)
    app.router.add_get("/health", health_check)
    
    # Setup startup and shutdown hooks
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)
    
    # Configure and start web server
    setup_application(app, dp, bot=bot)
    web.run_app(app, host=WEB_SERVER_HOST, port=WEB_SERVER_PORT)


if __name__ == "__main__":
    main()
