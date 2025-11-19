import os

# STRUCTURE
TREE = [
    ".env",

    "backend/requirements.txt",
    "backend/app/main.py",

    "backend/app/core/__init__.py",
    "backend/app/core/config.py",
    "backend/app/core/deps.py",

    "backend/app/db/__init__.py",
    "backend/app/db/base.py",
    "backend/app/db/session.py",
    "backend/app/db/init_db.py",

    "backend/app/models/__init__.py",
    "backend/app/models/user.py",
    "backend/app/models/level.py",
    "backend/app/models/logs.py",

    "backend/app/schemas/__init__.py",
    "backend/app/schemas/user.py",
    "backend/app/schemas/level.py",
    "backend/app/schemas/logs.py",

    "backend/app/services/__init__.py",
    "backend/app/services/gpt_service.py",
    "backend/app/services/xp_service.py",
    "backend/app/services/logs_service.py",

    "backend/app/api/__init__.py",
    "backend/app/api/v1/__init__.py",
    "backend/app/api/v1/router.py",
    "backend/app/api/v1/endpoints/__init__.py",
    "backend/app/api/v1/endpoints/users.py",
    "backend/app/api/v1/endpoints/domains.py",
    "backend/app/api/v1/endpoints/logs.py",
    "backend/app/api/v1/endpoints/analytics.py",

    "bot/requirements.txt",
    "bot/__init__.py",
    "bot/bot_main.py",
    "bot/config.py",
    "bot/api_client.py",

    "bot/handlers/__init__.py",
    "bot/handlers/start.py",
    "bot/handlers/profile.py",
    "bot/handlers/daily.py",
    "bot/handlers/misc.py",
]

# FILE TEMPLATES
CONTENT = {
    ".env": "MODE=debug\nSQLALCHEMY_DATABASE_URI=\nOPENAI_API_KEY=\nBOT_TOKEN=\nAPI_BASE_URL=http://127.0.0.1:8000/api/v1\n",

    "backend/requirements.txt": "fastapi\nuvicorn[standard]\nsqlalchemy\npydantic\npython-dotenv\nhttpx\npsycopg2-binary\n",

    "bot/requirements.txt": "aiogram\nhttpx\npython-dotenv\npydantic\n",
}

def create_file(path):
    folder = os.path.dirname(path)
    if folder and not os.path.exists(folder):
        os.makedirs(folder)

    if not os.path.exists(path):
        with open(path, "w", encoding="utf-8") as f:
            f.write(CONTENT.get(path, ""))

def main():
    for item in TREE:
        create_file(item)

    print("\n🎉 Структура проекта успешно создана!\n"
          "Открывай в PyCharm → запускай backend и бота.\n")

if __name__ == "__main__":
    main()
