# Полная инструкция по развертыванию

## Структура проекта

\`\`\`
project/
├── static-site/          # Статический сайт (WebApp интерфейс)
│   ├── index.html
│   ├── app.js
│   ├── translations.js
│   └── translations.yaml
└── bot-service/          # Python бот
    ├── bot.py
    ├── database.py
    ├── shop.py
    ├── admin_panel.py
    └── requirements.txt
\`\`\`

## Шаг 1: Развертывание Static Site (WebApp)

1. Зайдите на [Render.com](https://render.com)
2. Нажмите **New** → **Static Site**
3. Подключите ваш GitHub репозиторий
4. Настройки:
   - **Name**: `telegram-shop-webapp`
   - **Root Directory**: оставьте пустым
   - **Publish Directory**: `static-site`
   - **Build Command**: оставьте пустым
5. Нажмите **Create Static Site**
6. Дождитесь завершения развертывания
7. **ВАЖНО**: Скопируйте URL вашего сайта (например: `https://telegram-shop-webapp.onrender.com`)

## Шаг 2: Развертывание Bot Service (Python бот)

1. На Render нажмите **New** → **Background Worker**
2. Подключите тот же GitHub репозиторий
3. Настройки:
   - **Name**: `telegram-shop-bot`
   - **Root Directory**: `bot-service`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `python bot.py`
4. Environment Variables (добавьте эти переменные):
   - `BOT_TOKEN` = ваш токен от @BotFather
   - `ADMIN_IDS` = ваши Telegram ID (через запятую, например: `123456789,987654321`)
   - `WEBAPP_URL` = URL из Шага 1 (например: `https://telegram-shop-webapp.onrender.com`)
5. Нажмите **Create Background Worker**

## Шаг 3: Проверка работы

1. Откройте вашего бота в Telegram
2. Отправьте команду `/start`
3. Нажмите кнопку "🛍 Открыть магазин"
4. Должен открыться WebApp с интерфейсом магазина

## Получение Telegram ID

Чтобы узнать свой Telegram ID:
1. Напишите боту @userinfobot
2. Он отправит вам ваш ID

## Получение токена бота

1. Напишите @BotFather в Telegram
2. Отправьте команду `/newbot`
3. Следуйте инструкциям
4. Скопируйте токен

## Troubleshooting

### Бот не отвечает
- Проверьте правильность `BOT_TOKEN`
- Проверьте логи в Render Dashboard

### WebApp не открывается
- Проверьте правильность `WEBAPP_URL`
- Убедитесь что Static Site успешно развернут

### Нет доступа к админ-панели
- Проверьте правильность `ADMIN_IDS`
- Убедитесь что используете правильный Telegram ID
