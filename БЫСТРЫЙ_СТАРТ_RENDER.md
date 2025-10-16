# ⚡ Быстрый старт на Render (5 минут)

## 1️⃣ Создайте Web Service на Render

1. Перейдите на https://render.com и войдите
2. Нажмите **New** → **Web Service**
3. Подключите GitHub репозиторий

## 2️⃣ Настройки сервиса

```
Name: csgosalleruzb
Region: Frankfurt
Runtime: Python 3
Build Command: pip install -r requirements.txt
Start Command: python bot.py
Instance Type: Free ✅
```

## 3️⃣ Environment Variables (переменные окружения)

Добавьте эти переменные:

```
BOT_TOKEN = ваш_токен_от_BotFather
ADMIN_IDS = 1939282952,5266027747
```

**После создания сервиса** Render даст вам URL (например: `https://csgosalleruzb.onrender.com`)

Добавьте еще 2 переменные с этим URL:

```
WEBAPP_URL = https://csgosalleruzb.onrender.com
RENDER_EXTERNAL_URL = https://csgosalleruzb.onrender.com
```

## 4️⃣ Deploy!

Нажмите **Create Web Service** и ждите 3-5 минут.

## 5️⃣ Проверка

1. Откройте ваш URL в браузере - должен открыться магазин
2. В Telegram отправьте боту `/start`
3. Нажмите "Открыть магазин"

## ✅ Готово!

Ваш магазин работает на Render бесплатно!

---

## 📌 Важно знать

- Бесплатный план: сервис засыпает после 15 минут неактивности
- При первом запросе просыпается за 30-60 секунд
- 750 часов работы в месяц (достаточно для тестов)

## 🔧 Если что-то не работает

1. Проверьте логи в Render Dashboard
2. Убедитесь, что все переменные окружения правильные
3. Подождите 1-2 минуты после деплоя

## 📚 Подробная инструкция

См. файл `RENDER_DEPLOY.md`
