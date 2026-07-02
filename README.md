# Team Manager

Система управления командой — веб-приложение для управления задачами, встречами и оценкой работы сотрудников внутри компании.

## Технологический стек

- Python 3.13 — основной язык
- FastAPI — веб-фреймворк
- SQLAlchemy 2.0 (async) — ORM
- PostgreSQL — база данных
- Alembic — миграции
- Jinja2 — шаблонизация фронтенда
- Pydantic — валидация данных
- JWT (python-jose + bcrypt) — аутентификация
- Pytest — тестирование
- uv — менеджер зависимостей

## Архитектура

Проект построен по принципам Clean Architecture с разделением на три слоя:

src/
├── domain/          # Бизнес-логика (сущности, use cases, интерфейсы)
├── infra/           # Инфраструктура (ORM-модели, репозитории, JWT)
└── presentation/    # API (FastAPI эндпоинты, схемы, шаблоны)

- Domain — чистый Python, не зависит от фреймворков. Содержит бизнес-правила, сущности и интерфейсы (Protocol).
- Infra — реализации интерфейсов из domain. SQLAlchemy-модели, репозитории, хеширование паролей, JWT-утилиты.
- Presentation — FastAPI-приложение, Pydantic-схемы API, Jinja2-шаблоны.

Правило зависимостей: presentation → domain ← infra. Domain ничего не знает о внешних слоях.

## Функциональные модули

- Пользователи — регистрация, логин, JWT, профиль, смена пароля, роли
- Команды — создание, присоединение по коду, список участников, исключение
- Задачи — CRUD, статусы (open → in_progress → done), комментарии
- Оценки — выставление оценок, просмотр своих, средний балл
- Встречи — создание, проверка пересечений, отмена
- Календарь — агрегация задач и встреч за период

## Быстрый старт

### 1. Клонируйте репозиторий

git clone <repo-url>
cd team-manager

### 2. Настройте окружение

cp .env.example .env

Отредактируйте .env — укажите SECRET_KEY, JWT_SECRET, DATABASE_URL

### 3. Запустите PostgreSQL (опционально, для разработки можно SQLite)

docker compose up -d

### 4. Установите зависимости

uv sync

### 5. Примените миграции

uv run alembic upgrade head

### 6. Запустите приложение

uv run uvicorn src.presentation.api.factory:app --reload

Откройте http://localhost:8000

### 7. Запустите тесты

uv run pytest -v

С оценкой покрытия:

uv run pytest --cov=src --cov-report=term-missing

## API Документация

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Переменные окружения

| Переменная | Описание | По умолчанию |
|:---|:---|:---|
| SECRET_KEY | Секретный ключ приложения | обязательно |
| JWT_SECRET | Ключ для подписи JWT | обязательно |
| DATABASE_URL | URL базы данных | postgresql+asyncpg://postgres:postgres@localhost:5432/team_manager |
| DEBUG | Режим отладки | false |
| ACCESS_TOKEN_EXPIRE_MINUTES | Время жизни access токена | 30 |
| REFRESH_TOKEN_EXPIRE_DAYS | Время жизни refresh токена | 7 |
| ALLOWED_ORIGINS | Разрешённые CORS-источники | http://localhost:8000 |

## Тестирование

Проект использует Pytest с разделением на unit и integration тесты:

uv run pytest -m unit           # Unit-тесты
uv run pytest -m integration    # Интеграционные тесты
uv run pytest -m users          # Тесты модуля пользователей
uv run pytest -m teams          # Тесты модуля команд

Фикстуры для тестов находятся в tests/conftest.py. Для интеграционных тестов используется тестовая SQLite БД с автоматическим созданием и удалением таблиц.

## CI/CD

Команда для CI-пайплайна:

uv run pytest --cov=src --cov-report=term-missing
