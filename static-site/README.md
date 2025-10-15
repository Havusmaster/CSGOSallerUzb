# Telegram Shop WebApp (Static Site)

Это статический сайт для интерфейса магазина Telegram бота.

## Развертывание на Render

1. Создайте новый **Static Site** на Render
2. Подключите ваш GitHub репозиторий
3. Настройки:
   - **Publish Directory**: `static-site`
   - **Build Command**: (оставьте пустым)
4. После развертывания скопируйте URL (например: `https://your-app.onrender.com`)
5. Добавьте этот URL в переменную окружения `WEBAPP_URL` для бота

## Структура файлов

- `index.html` - главная страница магазина
- `app.js` - логика приложения
- `translations.js` - переводы
- `translations.yaml` - исходные переводы
