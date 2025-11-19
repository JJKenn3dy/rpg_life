# RPG Life

Этот репозиторий содержит backend и Telegram-бота для системы отслеживания привычек «RPG Life».

## Telegram-бот

### Настройка окружения
1. Создайте файл `.env` в корне репозитория и укажите параметры:
   ```env
   BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   BACKEND_URL=http://localhost:8000/api/v1
   ```
2. Установите зависимости:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r bot/requirements.txt
   ```

### Запуск
```bash
python -m bot.bot_main
```
Бот подключится к бэкенду (URL берётся из переменной `BACKEND_URL`) и начнёт принимать команды `/start`, `/profile`, `/domains` и `/daily`. Для удобства выводится клавиатура с быстрым доступом к командам.

### Тесты
Smoke-тест для HTTP-клиента можно запустить так:
```bash
pytest tests/test_api_client.py -q
```
Он использует `httpx.MockTransport`, чтобы убедиться, что клиент корректно обрабатывает ответы от REST-ручек бэкенда.
