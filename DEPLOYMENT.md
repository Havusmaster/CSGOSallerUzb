# Инструкция по развертыванию / Deployment Instructions

## Структура проекта / Project Structure

Проект разделен на 2 части:
1. **Static Site** - веб-интерфейс магазина (папка `static-site/`)
2. **Background Worker** - Python бот (корневая папка)

---

## 1. Развертывание Static Site на Render

### Шаг 1: Создайте новый Static Site
1. Зайдите на [Render Dashboard](https://dashboard.render.com/)
2. Нажмите **New** → **Static Site**
3. Подключите ваш GitHub репозиторий

### Шаг 2: Настройте Static Site
- **Name**: `telegram-shop-webapp` (или любое другое имя)
- **Branch**: `main`
- **Root Directory**: `static-site`
- **Build Command**: (оставьте пустым)
- **Publish Directory**: `.`

### Шаг 3: Deploy
Нажмите **Create Static Site**. После деплоя вы получите URL вида:
\`\`\`
https://telegram-shop-webapp.onrender.com
\`\`\`

**Сохраните этот URL!** Он понадобится для настройки бота.

---

## 2. Развертывание Python бота на Render

### Шаг 1: Создайте новый Background Worker
1. На [Render Dashboard](https://dashboard.render.com/)
2. Нажмите **New** → **Background Worker**
3. Подключите тот же GitHub репозиторий

### Шаг 2: Настройте Background Worker
- **Name**: `telegram-shop-bot`
- **Environment**: `Python 3`
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`

### Шаг 3: Добавьте Environment Variables
Нажмите **Environment** и добавьте:

| Key | Value |
|-----|-------|
| `WEBAPP_URL` | URL вашего Static Site (из шага 1) |

Пример:
\`\`\`
WEBAPP_URL=https://telegram-shop-webapp.onrender.com
\`\`\`

### Шаг 4: Deploy
Нажмите **Create Background Worker**

---

## 3. Проверка работы

1. Откройте Telegram
2. Найдите вашего бота
3. Отправьте команду `/start`
4. Нажмите кнопку "🛍️ Открыть магазин"
5. Должен открыться веб-интерфейс магазина

---

## Альтернатива: Один Web Service (с webhook)

Если хотите использовать один сервис вместо двух:

### Настройки для Web Service:
- **Service Type**: Web Service
- **Build Command**: `pip install -r requirements.txt`
- **Start Command**: `python bot.py`
- **Environment Variables**:
  - `WEBAPP_URL`: URL где размещен webapp (можно тот же домен)
  - `RENDER_EXTERNAL_URL`: URL вашего Web Service на Render

**Примечание**: В этом случае бот будет использовать webhooks вместо polling.

---

## Troubleshooting

### Бот не отвечает
- Проверьте логи Background Worker на Render
- Убедитесь, что BOT_TOKEN правильный
- Проверьте, что сервис запущен (не в состоянии "Suspended")

### WebApp не открывается
- Проверьте, что WEBAPP_URL правильно указан в Environment Variables
- Убедитесь, что Static Site успешно задеплоен
- Проверьте URL Static Site в браузере

### Ошибка CORS
- Static Site на Render автоматически настроен для работы с Telegram WebApp
- Если проблема сохраняется, проверьте консоль браузера (F12)

---

## Контакты

Если возникли проблемы, проверьте:
1. Логи на Render Dashboard
2. Статус сервисов (должны быть "Live")
3. Environment Variables (должны быть правильно заполнены)
