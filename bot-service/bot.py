import asyncio
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command, Text
from aiogram.types import (
    WebAppInfo, InlineKeyboardMarkup, 
    InlineKeyboardButton, CallbackQuery
)
from aiogram.utils.markdown import hbold

from database import db
from shop import handle_purchase_request, ORDER_STATUSES
from admin_panel import admin_router

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Инициализация бота
BOT_TOKEN = os.getenv("BOT_TOKEN", "7504123410:AAEznGqRafbyrBx2e34HzsxztWV201HRMxE")
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "5266027747").split(",")]
WEBAPP_URL = os.getenv("WEBAPP_URL", "https://csgosalleruzb-1.onrender.com")
SUPPORT_USERNAME = os.getenv("SUPPORT_USERNAME", "@csgoseller_support")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher()

# Сохраняем настройки в боте для доступа из других модулей
bot["ADMIN_IDS"] = ADMIN_IDS
bot["WEBAPP_URL"] = WEBAPP_URL
bot["SUPPORT_USERNAME"] = SUPPORT_USERNAME

# Подключаем роутер админ-панели
dp.include_router(admin_router)

# Глобальные команды бота
BOT_COMMANDS = [
    types.BotCommand(command="start", description="Запустить бота"),
    types.BotCommand(command="help", description="Помощь и команды"),
    types.BotCommand(command="catalog", description="Каталог товаров"),
    types.BotCommand(command="orders", description="Мои заказы"),
    types.BotCommand(command="support", description="Поддержка"),
    types.BotCommand(command="admin", description="Админ-панель")
]

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    """Обработчик команды /start"""
    user = message.from_user
    welcome_text = (
        f"👋 Привет, {user.first_name}!\n\n"
        "Добро пожаловать в магазин CS:GO скинов и предметов. "
        "У нас вы найдете лучшие предложения по выгодным ценам!"
    )
    
    # Регистрируем пользователя в базе, если его еще нет
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        language_code=user.language_code
    )
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="🛍 Каталог товаров",
                web_app=WebAppInfo(url=WEBAPP_URL)
            )
        ],
        [
            InlineKeyboardButton(
                text="📦 Мои заказы",
                callback_data="my_orders"
            ),
            InlineKeyboardButton(
                text="❓ Помощь",
                callback_data="help"
            )
        ]
    ])
    
    if user.id in ADMIN_IDS:
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text="👑 Админ-панель",
                callback_data="admin_panel"
            )
        ])
    
    await message.answer(welcome_text, reply_markup=keyboard)

@dp.message(Command("help"))
async def cmd_help(message: types.Message):
    """Показать справку по командам"""
    help_text = (
        "ℹ️ <b>Доступные команды:</b>\n\n"
        "/start - Запустить бота\n"
        "/catalog - Открыть каталог товаров\n"
        "/orders - Просмотреть мои заказы\n"
        "/support - Связаться с поддержкой\n"
        "/help - Показать это сообщение"
    )
    
    if message.from_user.id in ADMIN_IDS:
        help_text += "\n\n👑 <b>Команды администратора:</b>\n"
        help_text += "/admin - Открыть админ-панель"
    
    await message.answer(help_text)

@dp.message(Command("catalog"))
async def cmd_catalog(message: types.Message):
    """Открыть каталог товаров"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text="🛍 Перейти в каталог",
            web_app=WebAppInfo(url=WEBAPP_URL)
        )]
    ])
    
    await message.answer(
        "🎮 <b>Каталог товаров CS:GO</b>\n\n"
        "Нажмите кнопку ниже, чтобы открыть каталог и выбрать товары:",
        reply_markup=keyboard
    )

@dp.callback_query(Text(startswith=["order_", "my_orders"]))
async def handle_order_callback(callback: CallbackQuery):
    """Обработка колбэков, связанных с заказами"""
    try:
        data = callback.data
        user_id = callback.from_user.id
        
        if data == "my_orders" or data.startswith("my_orders_"):
            # Показываем список заказов пользователя
            orders = db.get_user_orders(user_id)
            
            if not orders:
                await callback.message.answer(
                    "📭 У вас пока нет заказов. "
                    "Перейдите в каталог, чтобы сделать заказ!"
                )
                return
            
            orders_text = "📋 <b>Ваши заказы:</b>\n\n"
            
            for order in orders[:10]:  # Ограничиваем количество отображаемых заказов
                status = ORDER_STATUSES.get(order['status'], order['status'])
                orders_text += (
                    f"📦 <b>Заказ #{order['id']}</b>\n"
                    f"📝 Статус: {status}\n"
                    f"💰 Сумма: ${order['amount']:.2f}\n"
                    f"📅 {order['created_at']}\n"
                    f"➖➖➖➖➖➖\n"
                )
            
            if len(orders) > 10:
                orders_text += "\nПоказаны последние 10 заказов."
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🛍 В каталог",
                        web_app=WebAppInfo(url=WEBAPP_URL)
                    ),
                    InlineKeyboardButton(
                        text="📞 Поддержка",
                        callback_data="contact_support"
                    )
                ]
            ])
            
            await callback.message.edit_text(orders_text, reply_markup=keyboard)
        
        elif data.startswith("order_details_"):
            # Показываем детали конкретного заказа
            order_id = int(data.split("_")[2])
            order = db.get_order(order_id)
            
            if not order or order['user_id'] != user_id:
                await callback.answer("❌ Заказ не найден или у вас нет доступа.", show_alert=True)
                return
            
            status = ORDER_STATUSES.get(order['status'], order['status'])
            
            text = (
                f"📦 <b>Заказ #{order['id']}</b>\n\n"
                f"📝 <b>Статус:</b> {status}\n"
                f"💰 <b>Сумма:</b> ${order['amount']:.2f}\n"
                f"📅 <b>Дата создания:</b> {order['created_at']}\n"
            )
            
            if order.get('updated_at'):
                text += f"🔄 <b>Последнее обновление:</b> {order['updated_at']}\n"
            
            if order.get('admin_comment'):
                text += f"\n💬 <b>Комментарий:</b> {order['admin_comment']}\n"
            
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="🔙 Назад к заказам",
                        callback_data="my_orders"
                    ),
                    InlineKeyboardButton(
                        text="📞 Поддержка",
                        callback_data="contact_support"
                    )
                ]
            ])
            
            await callback.message.edit_text(text, reply_markup=keyboard)
        
        await callback.answer()
    except Exception as e:
        logger.error(f"Error in handle_order_callback: {e}")
        await callback.answer("❌ Произошла ошибка. Пожалуйста, попробуйте позже.", show_alert=True)

@dp.callback_query(Text("contact_support"))
async def contact_support(callback: CallbackQuery):
    """Показать контакты поддержки"""
    await callback.answer()
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(
                text="💬 Написать в поддержку",
                url=f"https://t.me/{SUPPORT_USERNAME[1:] if SUPPORT_USERNAME.startswith('@') else SUPPORT_USERNAME}"
            )
        ],
        [
            InlineKeyboardButton(
                text="🔙 На главную",
                callback_data="back_to_main"
            )
        ]
    ])
    
    await callback.message.edit_text(
        f"📞 <b>Служба поддержки</b>\n\n"
        f"По всем вопросам вы можете обратиться к нашему менеджеру: {SUPPORT_USERNAME}\n\n"
        "⏰ <b>График работы:</b> круглосуточно\n"
        "💬 <b>Среднее время ответа:</b> до 15 минут",
        reply_markup=keyboard
    )

@dp.callback_query(Text("back_to_main"))
async def back_to_main(callback: CallbackQuery):
    """Вернуться в главное меню"""
    await cmd_start(callback.message)
    await callback.answer()

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
        logger.error(f"Error handling webapp data: {e}", exc_info=True)
        await message.answer(
            "❌ Произошла ошибка при обработке запроса. "
            "Пожалуйста, попробуйте еще раз или свяжитесь с поддержкой."
        )

async def setup_bot_commands():
    """Установка команд бота"""
    await bot.set_my_commands(BOT_COMMANDS)

async def on_startup():
    """Действия при запуске бота"""
    logger.info("Starting bot...")
    logger.info(f"WebApp URL: {WEBAPP_URL}")
    logger.info(f"Admin IDs: {ADMIN_IDS}")
    await setup_bot_commands()

async def main():
    """Главная функция запуска бота"""
    await on_startup()
    
    # Запускаем бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
