# Telegram Bot (Background Worker)

Это Python бот для Telegram.

## Развертывание на Render

1. Создайте новый **Background Worker** на Render
2. Подключите ваш GitHub репозиторий
3. Настройки:
   - **Root Directory**: `bot-service`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
4. Environment Variables:
   - `BOT_TOKEN` - токен вашего бота
   - `ADMIN_IDS` - ID администраторов (через запятую)
   - `WEBAPP_URL` - URL статического сайта из шага 1

## Структура файлов

- `bot.py` - главный файл бота
- `database.py` - база данных в памяти
- `shop.py` - логика магазина
- `admin_panel.py` - админ панель
- `requirements.txt` - зависимости Python
