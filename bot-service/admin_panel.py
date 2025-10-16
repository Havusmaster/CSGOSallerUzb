from aiogram import Router, types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import os

from database import db

admin_router = Router()
ADMIN_IDS = [int(id.strip()) for id in os.getenv("ADMIN_IDS", "1939282952,5266027747").split(",")]

class ProductForm(StatesGroup):
    category = State()
    name = State()
    price = State()
    description = State()
    image_url = State()
    float_value = State()

async def show_admin_menu(message: types.Message):
    """Показать главное меню админ-панели"""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="➕ Добавить товар", callback_data="admin_add_product")],
        [InlineKeyboardButton(text="📦 Список товаров", callback_data="admin_list_products")],
        [InlineKeyboardButton(text="🎯 Аукционы", callback_data="admin_auctions")],
    ])
    
    await message.answer(
        "🔧 Админ-панель\n\nВыберите действие:",
        reply_markup=keyboard
    )

@admin_router.callback_query(F.data == "admin_add_product")
async def start_add_product(callback: types.CallbackQuery, state: FSMContext):
    """Начать добавление товара"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔫 Оружие", callback_data="category_weapons")],
        [InlineKeyboardButton(text="👤 Агенты", callback_data="category_agents")],
    ])
    
    await callback.message.edit_text(
        "Выберите категорию товара:",
        reply_markup=keyboard
    )
    await state.set_state(ProductForm.category)

@admin_router.callback_query(F.data.startswith("category_"))
async def set_category(callback: types.CallbackQuery, state: FSMContext):
    """Установить категорию товара"""
    category = callback.data.split("_")[1]
    await state.update_data(category=category)
    
    await callback.message.edit_text("Введите название товара:")
    await state.set_state(ProductForm.name)

@admin_router.message(ProductForm.name)
async def set_name(message: types.Message, state: FSMContext):
    """Установить название товара"""
    await state.update_data(name=message.text)
    await message.answer("Введите цену товара (в долларах):")
    await state.set_state(ProductForm.price)

@admin_router.message(ProductForm.price)
async def set_price(message: types.Message, state: FSMContext):
    """Установить цену товара"""
    try:
        price = float(message.text)
        await state.update_data(price=price)
        await message.answer("Введите описание товара:")
        await state.set_state(ProductForm.description)
    except ValueError:
        await message.answer("❌ Неверный формат цены. Введите число:")

@admin_router.message(ProductForm.description)
async def set_description(message: types.Message, state: FSMContext):
    """Установить описание товара"""
    await state.update_data(description=message.text)
    await message.answer("Введите URL изображения:")
    await state.set_state(ProductForm.image_url)

@admin_router.message(ProductForm.image_url)
async def set_image_url(message: types.Message, state: FSMContext):
    """Установить URL изображения"""
    await state.update_data(image_url=message.text)
    
    data = await state.get_data()
    if data.get("category") == "weapons":
        await message.answer("Введите значение Float (или 0 если не применимо):")
        await state.set_state(ProductForm.float_value)
    else:
        await finish_product_creation(message, state, None)

@admin_router.message(ProductForm.float_value)
async def set_float_value(message: types.Message, state: FSMContext):
    """Установить значение Float"""
    try:
        float_value = float(message.text) if message.text != "0" else None
        await finish_product_creation(message, state, float_value)
    except ValueError:
        await message.answer("❌ Неверный формат Float. Введите число:")

async def finish_product_creation(message: types.Message, state: FSMContext, float_value):
    """Завершить создание товара"""
    data = await state.get_data()
    
    product_id = db.add_product(
        category=data["category"],
        name=data["name"],
        price=data["price"],
        description=data["description"],
        image_url=data["image_url"],
        float_value=float_value
    )
    
    await message.answer(
        f"✅ Товар успешно добавлен!\n\n"
        f"ID: {product_id}\n"
        f"Название: {data['name']}\n"
        f"Цена: ${data['price']}"
    )
    await state.clear()

@admin_router.callback_query(F.data == "admin_list_products")
async def list_products(callback: types.CallbackQuery):
    """Показать список товаров"""
    if callback.from_user.id not in ADMIN_IDS:
        await callback.answer("❌ Нет доступа", show_alert=True)
        return
    
    products = db.get_all_products()
    
    if not products:
        await callback.message.edit_text("📦 Товаров пока нет.")
        return
    
    text = "📦 Список товаров:\n\n"
    for product in products:
        status_emoji = "✅" if product["status"] == "available" else "❌"
        text += f"{status_emoji} {product['name']} - ${product['price']}\n"
        text += f"   ID: {product['id']}\n\n"
    
    await callback.message.edit_text(text)
