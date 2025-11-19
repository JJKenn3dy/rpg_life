from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from backend.app.db.session import engine
from backend.app.db.base import Base

# импорт моделей, чтобы SQLAlchemy видел их перед create_all
from backend.app.models import user
from backend.app.models import domain   # или domains — как у тебя называется

app = FastAPI()

Base.metadata.create_all(bind=engine)

from backend.app.api.v1.router import api_router
app.include_router(api_router, prefix="/api/v1")


@app.get("/", response_class=HTMLResponse)
def root_page():
    return """
    <!DOCTYPE html>
    <html lang=\"ru\">
    <head>
        <meta charset=\"UTF-8\" />
        <meta name=\"viewport\" content=\"width=device-width, initial-scale=1\" />
        <title>RPG Life API playground</title>
        <style>
            :root {
                color-scheme: light dark;
                font-family: system-ui, -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            }
            body {
                margin: 0 auto;
                max-width: 900px;
                padding: 2rem 1.5rem 3rem;
                line-height: 1.5;
            }
            h1 {
                margin-top: 0;
                font-size: 1.8rem;
            }
            label {
                display: block;
                font-weight: 600;
                margin: 1rem 0 0.35rem;
            }
            input, select, textarea {
                width: 100%;
                padding: 0.6rem;
                border-radius: 0.4rem;
                border: 1px solid #8884;
                font-size: 1rem;
            }
            textarea {
                min-height: 140px;
                font-family: 'JetBrains Mono', Consolas, monospace;
            }
            button {
                margin-top: 1.2rem;
                padding: 0.7rem 1.4rem;
                font-size: 1rem;
                border-radius: 999px;
                border: none;
                background: #2563eb;
                color: #fff;
                cursor: pointer;
            }
            button:disabled { opacity: .6; cursor: not-allowed; }
            pre {
                background: #1111;
                border-radius: 0.6rem;
                padding: 1rem;
                overflow-x: auto;
                white-space: pre-wrap;
            }
            .grid {
                display: grid;
                gap: 1rem;
            }
            @media (min-width: 720px) {
                .grid { grid-template-columns: repeat(2, 1fr); }
            }
        </style>
    </head>
    <body>
        <h1>RPG Life API playground</h1>
        <p>
            Укажи метод, относительный путь (например, <code>/api/v1/users/by-tg/123</code>)
            и JSON-тело запроса. Сайт отправит запрос на этот же сервер и покажет ответ.
        </p>
        <label for=\"method\">Метод</label>
        <select id=\"method\">
            <option>GET</option>
            <option>POST</option>
            <option>PUT</option>
            <option>PATCH</option>
            <option>DELETE</option>
        </select>

        <label for=\"endpoint\">Путь</label>
        <input id=\"endpoint\" value=\"/api/v1/users/by-tg/1\" />

        <label for=\"body\">JSON тело</label>
        <textarea id=\"body\">{\n  \"tg_id\": 1,\n  \"username\": \"tester\"\n}</textarea>

        <button id=\"sendBtn\">Отправить запрос</button>

        <div class=\"grid\">
            <div>
                <h2>Ответ</h2>
                <pre id=\"response\">запрос ещё не отправлялся</pre>
            </div>
            <div>
                <h2>Служебная информация</h2>
                <pre id=\"meta\"></pre>
            </div>
        </div>

        <script>
            const btn = document.getElementById('sendBtn');
            const methodEl = document.getElementById('method');
            const endpointEl = document.getElementById('endpoint');
            const bodyEl = document.getElementById('body');
            const responseEl = document.getElementById('response');
            const metaEl = document.getElementById('meta');

            btn.addEventListener('click', async () => {
                const method = methodEl.value;
                const endpoint = endpointEl.value.trim() || '/';
                let bodyText = bodyEl.value.trim();
                let payload;
                let headers = {};

                if (method !== 'GET' && method !== 'DELETE' && bodyText) {
                    headers['Content-Type'] = 'application/json';
                    try {
                        payload = JSON.stringify(JSON.parse(bodyText));
                    } catch (err) {
                        responseEl.textContent = 'Некорректный JSON: ' + err.message;
                        return;
                    }
                }

                btn.disabled = true;
                responseEl.textContent = 'Загрузка...';
                metaEl.textContent = '';

                const start = performance.now();
                try {
                    const res = await fetch(endpoint, {
                        method,
                        headers,
                        body: payload,
                    });
                    const elapsed = (performance.now() - start).toFixed(0);
                    metaEl.textContent = `Статус: ${res.status} ${res.statusText}\nВремя: ${elapsed} мс`;

                    const text = await res.text();
                    try {
                        const parsed = JSON.parse(text);
                        responseEl.textContent = JSON.stringify(parsed, null, 2);
                    } catch (_) {
                        responseEl.textContent = text;
                    }
                } catch (error) {
                    responseEl.textContent = 'Ошибка сети: ' + error.message;
                } finally {
                    btn.disabled = false;
                }
            });
        </script>
    </body>
    </html>
    """
