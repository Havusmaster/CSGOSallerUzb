import asyncio
import logging
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.types import WebAppInfo, InlineKeyboardMarkup, InlineKeyboardButton

from database import db
from shop import handle_purchase_request
from admin_panel import admin_router

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "7504123410:AAEznGqRafbyrBx2e34HzsxztWV201HRMxE")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", [1939282952, 5266027747]).split(",")]
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://csgosalleruzb-1.onrender.com")

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

# Подключаем роутер админ-панели
dp.include_router(admin_router)

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛍 Открыть магазин",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "👋 Добро пожаловать в магазин CS:GO!\n\n"
        "Нажмите кнопку ниже, чтобы открыть каталог товаров.",
        reply_markup=keyboard
    )

@dp.message(Command("admin"))
async def cmd_admin(message: types.Message):
    """Обработчик команды /admin"""
    if message.from_user.id not in ADMIN_IDS:
        await message.answer("❌ У вас нет доступа к админ-панели.")
        return
    
    from admin_panel import show_admin_menu
    await show_admin_menu(message)

@dp.message(F.web_app_data)
async def handle_webapp_data(message: types.Message):
    """Обработчик данных из WebApp"""
    try:
        await handle_purchase_request(message, bot)
    except Exception as e:
        logger.error(f"Error handling webapp data: {e}")
        await message.answer("❌ Произошла ошибка при обработке запроса.")

async def main():
    """Главная функция запуска бота"""
    logger.info("Starting bot...")
    logger.info(f"WebApp URL: {WEBAPP_URL}")
    logger.info(f"Admin IDs: {ADMIN_IDS}")
    
    # Запускаем polling
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
