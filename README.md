# RPG Life

Этот репозиторий содержит backend и Telegram-бота для системы отслеживания привычек «RPG Life».

## Telegram-бот

### Настройка окружения
1. Создайте файл `.env` в корне репозитория и укажите параметры:
   ```env
   BOT_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   BACKEND_URL=http://localhost:8000/api/v1
   ```
   Токен и URL читаются в `bot/config.py` через `pydantic.BaseSettings`, поэтому достаточно указать их однажды.
2. Установите зависимости:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r bot/requirements.txt
   ```

### Команды бота
* `/start` — приветствует пользователя и показывает клавиатуру с быстрыми действиями.
* `/profile` — обращается к ручке `/users/<telegram_id>` и выводит данные профиля.
* `/domains` — запрашивает `/domains?telegram_id=...` и показывает домены развития.
* `/daily` — запрашивает `/daily-logs` и `/finances`, чтобы отобразить заметки и финансовые записи за день.

### Запуск
```bash
python -m bot.bot_main
```
Бот подключится к бэкенду (URL берётся из переменной `BACKEND_URL`) и начнёт принимать команды, перечисленные выше.

### Тесты
Smoke-тесты для HTTP-клиента можно запустить так:
```bash
pytest tests/test_api_client.py -q
```
Они используют `httpx.MockTransport`, чтобы убедиться, что клиент корректно обрабатывает ответы от REST-ручек бэкенда.
