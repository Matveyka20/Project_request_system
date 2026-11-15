# Система обработки заявок

Учебный проект информационной системы для централизованной регистрации, распределения, выполнения и контроля заявок на работы или услуги.

## Текущее состояние

Реализован вертикальный сценарий регистрации заявки: CLI проверяет ввод, прикладной сервис применяет базовые правила, а SQLite-адаптер сохраняет заявку вместе с начальным событием статуса в одной транзакции. Назначение исполнителей, изменение статусов, приёмка результата, уведомления и разграничение доступа остаются целевыми функциями.

## Назначение

Система должна помогать заявителям отслеживать обращения, операторам — проверять и назначать заявки, исполнителям — фиксировать ход работы и результат, а контролёрам — принимать результат или возвращать его на доработку.

## Функции

- регистрация заявок с описанием и категорией;
- просмотр статуса и истории, проверка заявок, запрос уточнений и назначение исполнителей;
- фиксация хода выполнения и передача результата на проверку;
- приёмка результата или возврат на доработку;
- уведомления участников и разграничение доступа по ролям.

Сейчас реализована регистрация; остальные перечисленные сценарии планируются.

Подробные требования, роли, сущности и критерии приёмки описаны в [техническом задании](docs/TZ.md).

## Архитектура

Приложение разделено на интерфейс, прикладной сценарий, предметные сущности и инфраструктурный адаптер. Модули развиваются по реальным сценариям, а не обязаны иметь отдельный контроллер, сервис и репозиторий каждый.

```text
Вызовы во время выполнения:
presentation -> application service -> persistence port -> SQLite adapter -> database

Зависимости исходного кода:
presentation -> application -> domain
                     ^
                     └── infrastructure adapter implements application port
```

- `presentation` — CLI и другие адаптеры ввода/вывода; преобразуют входные данные и вызывают сценарии, не обращаясь к хранилищу напрямую.
- `application/services` — прикладные сценарии и правила регистрации; используют контракты хранения и не зависят от конкретной СУБД.
- `application/ports` — контракты репозиториев и единицы работы, необходимые сценариям.
- `domain` — модели предметных сущностей, независимые от хранения и пользовательского интерфейса.
- `infrastructure` — реализации портов, подключения и детали хранения; SQLite-репозитории выполняют операции в общей транзакции Unit of Work.

Стрелка вызова во время выполнения и направление зависимости исходного кода — не одно и то же: сервис вызывает порт репозитория, а инфраструктурная реализация предоставляет этот порт. Так сценарии можно тестировать с подменным хранилищем и не привязывать к деталям SQLite.

[Слоистая архитектура](docs/architecture/architecture.puml) и [диаграмма компонентов](docs/architecture/components.puml) показывают целевую схему.

## Структура исходного кода

```text
src/request_system/
├── __main__.py
├── application/
│   ├── ports/persistence.py
│   └── services/request_service.py
├── domain/entities.py
├── presentation/cli.py
└── infrastructure/database/sqlite/
    ├── database.py
    ├── repositories.py
    └── unit_of_work.py
tests/
```

Пакеты `services` и `repositories` верхнего уровня сохранены как заготовки для следующих сценариев. Добавляйте компоненты вместе с вертикальными пользовательскими сценариями, а не создавайте заранее одинаковые репозитории на каждую сущность.

## Локальная установка и запуск

### Требования

- **Python** 3.8 или новее (проверка: `python --version`)
- **pip** — менеджер пакетов Python
- **git** — система контроля версий

### Установка окружения

Выполняйте все команды из корня репозитория:

1. **Создайте виртуальное окружение:**
   ```powershell
   python -m venv .venv
   ```

2. **Активируйте виртуальное окружение:**
   ```powershell
   .\.venv\Scripts\Activate.ps1
   ```

   Если PowerShell блокирует запуск скриптов, разрешите временно:
   ```powershell
   Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
   .\.venv\Scripts\Activate.ps1
   ```

3. **Установите зависимости:**
   ```powershell
   python -m pip install -e .
   ```

### Конфигурация

Приложение использует систему конфигурации на основе переменных окружения с поддержкой файлов `.env`.

#### Быстрый старт

Скопируйте файл `.env.example` в `.env` и настройте нужные значения:

```bash
cp .env.example .env
# Отредактируйте .env в текстовом редакторе
```

#### Переменные окружения

Все параметры можно переопределить через переменные окружения:

**Окружение и сервер:**
- `APP_ENV` - Режим работы: `development`, `staging`, `production` (по умолчанию: `development`)
- `APP_DEBUG` - Включить режим отладки: `true` или `false` (по умолчанию: `true`)
- `APP_PORT` - Порт сервера API (по умолчанию: `8000`)
- `APP_HOST` - IP адрес для прослушивания (по умолчанию: `0.0.0.0`)
- `APP_WORKERS` - Количество Uvicorn workers для production (по умолчанию: `4`)
- `APP_NAME` - Название приложения (по умолчанию: `Request System`)

**База данных:**
- `DATABASE_URL` - Строка подключения (по умолчанию: `sqlite:///./requests.db`)
  - SQLite: `sqlite:///./requests.db` (относительный путь)
  - SQLite: `sqlite:////tmp/db.sqlite3` (абсолютный путь)
  - PostgreSQL: `postgresql://user:password@localhost:5432/dbname`
- `DATABASE_POOL_SIZE` - Размер пула подключений (по умолчанию: `10`)
- `DATABASE_ECHO_SQL` - Логировать SQL запросы: `true` или `false` (по умолчанию: `false`)

**API:**
- `API_PREFIX` - Префикс API endpoints (по умолчанию: `/api`)
- `API_TITLE` - Название API в документации (по умолчанию: `Request System API`)
- `API_VERSION` - Версия API (по умолчанию: `1.1.0`)
- `API_CORS_ORIGINS` - CORS разрешённые origins: `*` или `https://example.com,https://app.example.com` (по умолчанию: `*`)
- `API_DOCS_URL` - Путь к Swagger UI (по умолчанию: `/docs`)
- `API_REDOC_URL` - Путь к ReDoc (по умолчанию: `/redoc`)
- `API_OPENAPI_URL` - Путь к OpenAPI схеме (по умолчанию: `/openapi.json`)

**Логирование:**
- `LOG_LEVEL` - Уровень логирования: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` (по умолчанию: `INFO`)

#### Примеры конфигурации

**Разработка (локальная машина):**
```bash
APP_ENV=development
APP_DEBUG=true
APP_PORT=8000
APP_HOST=127.0.0.1
DATABASE_URL=sqlite:///./requests-dev.db
DATABASE_ECHO_SQL=true
LOG_LEVEL=DEBUG
API_CORS_ORIGINS=*
```

**Staging окружение:**
```bash
APP_ENV=staging
APP_DEBUG=false
APP_PORT=8000
APP_WORKERS=2
DATABASE_URL=postgresql://user:password@staging-db:5432/requests_staging
DATABASE_ECHO_SQL=false
LOG_LEVEL=INFO
API_CORS_ORIGINS=https://staging.example.com
```

**Production окружение:**
```bash
APP_ENV=production
APP_DEBUG=false
APP_PORT=8000
APP_WORKERS=8
DATABASE_URL=postgresql://user:password@prod-db:5432/requests_prod
DATABASE_ECHO_SQL=false
LOG_LEVEL=WARNING
API_CORS_ORIGINS=https://app.example.com,https://api.example.com
```

#### Установка переменных окружения

**Способ 1: Файл `.env` (рекомендуется для разработки)**
```bash
# Скопируйте и отредактируйте
cp .env.example .env
```

**Способ 2: Переменные окружения системы**
```bash
# Linux/Mac
export APP_PORT=9000
export DATABASE_URL=postgresql://localhost/db

# Windows PowerShell
$env:APP_PORT=9000
$env:DATABASE_URL="postgresql://localhost/db"
```

**Способ 3: Командная строка (для однократного запуска)**
```bash
# Linux/Mac
APP_PORT=9000 APP_DEBUG=false python -m uvicorn src.request_system.presentation.main:app

# Windows PowerShell
$env:APP_PORT=9000; $env:APP_DEBUG="false"; python -m uvicorn src.request_system.presentation.main:app
```

### 🔒 Безопасность

#### Защита от утечки секретов

**Никогда не коммитьте файл `.env`!** Система разработана так, чтобы минимизировать риск утечки чувствительных данных.

**Что уже защищено:**
- ✅ Файл `.env` добавлен в `.gitignore` и не попадёт в Git
- ✅ `.env.example` содержит только шаблоны и примеры без реальных секретов
- ✅ В исходном коде нет хардкодированных паролей, ключей или токенов
- ✅ Все чувствительные данные загружаются только из переменных окружения

**Best Practices безопасности:**

1. **Локальная разработка:**
   ```bash
   # ПРАВИЛЬНО: используйте .env файл
   cp .env.example .env
   # Отредактируйте .env с вашими значениями
   # .env автоматически игнорируется Git
   
   # НЕПРАВИЛЬНО: не коммитьте реальные значения
   # git commit .env  # ❌ ОПАСНО!
   ```

2. **Production развертывание:**
   ```bash
   # ПРАВИЛЬНО: устанавливайте переменные окружения на сервере
   export APP_ENV=production
   export DATABASE_URL=postgresql://user:pass@prod-db/db
   export LOG_LEVEL=WARNING
   
   # Или через system environment, Docker, Kubernetes secrets, CI/CD, и т.д.
   # НИКОГДА не коммитьте .env в production
   ```

3. **Что считается чувствительными данными:**
   - 🔐 Пароли к БД
   - 🔐 API ключи и токены
   - 🔐 Private keys и сертификаты
   - 🔐 Credentials и авторизационные данные
   - 🔐 Secret keys для криптографии
   - 🔐 URLs с паролями (e.g., `postgresql://user:password@host`)

4. **Проверка перед коммитом:**
   ```bash
   # Убедитесь что .env не в Git
   git status | grep ".env"  # Не должно быть результатов
   
   # Проверьте историю (если случайно закоммитили)
   git log --all --full-history -- ".env"
   
   # Если обнаружили утечку - сразу удалите
   git filter-branch --tree-filter 'rm -f .env' HEAD
   ```

5. **Для CI/CD систем:**
   ```yaml
   # GitHub Actions пример (НЕ коммитьте реальные значения!)
   env:
     APP_ENV: ${{ secrets.APP_ENV }}
     DATABASE_URL: ${{ secrets.DATABASE_URL }}
     LOG_LEVEL: ${{ secrets.LOG_LEVEL }}
   ```

**Аудит безопасности:**
- ✅ Проверено: нет `.env` файла в Git истории
- ✅ Проверено: нет хардкодированных секретов в коде
- ✅ Проверено: `.gitignore` правильно настроен
- ✅ Проверено: `.env.example` содержит только примеры

### Инициализация базы данных

Приложение использует SQLite для хранения данных. База данных инициализируется автоматически при первом запуске, однако вы можете выполнить инициализацию вручную и загрузить тестовые данные несколькими способами.

#### Быстрая инициализация (рекомендуется)

Используйте удобный bash-скрипт для инициализации базы данных:

```bash
# Инициализировать БД со схемой и тестовыми данными
bash scripts/init-db.sh

# Сбросить БД и переинициализировать (удалит всё)
bash scripts/init-db.sh --reset

# Использовать кастомный путь к БД
bash scripts/init-db.sh --database /path/to/custom.db
```

Или используйте Makefile:

```bash
# Инициализировать БД
make init-db

# Сбросить БД
make reset-db

# Загрузить тестовые данные в существующую БД
make seed-db
```

#### Ручная инициализация

Если скрипты недоступны, вы можете инициализировать вручную:

```powershell
# Вариант 1: Прямая инициализация через Python
python -m request_system.scripts.load_seed_data --reset-db

# Вариант 2: Только загрузить семена (не сбрасывать схему)
python -m request_system.scripts.load_seed_data

# Вариант 3: Использовать кастомный путь
python -m request_system.scripts.load_seed_data --database ./my-database.db
```

#### Структура базы данных

Подробная документация по структуре БД доступна в [docs/DATABASE_SCHEMA.md](docs/DATABASE_SCHEMA.md):

- 10 таблиц с отношениями и индексами
- Автоматические временные метки и аудит-трейлы
- Полная история изменений статусов через `RequestHistory`
- Встроенная поддержка комментариев и вложений

#### Тестовые данные

База данных автоматически заполняется реалистичными тестовыми данными:

- **10 тестовых пользователей** с разными ролями (Admin, Manager, Executor, User)
- **7 статусов** для управления жизненным циклом заявок
- **8 категорий** для классификации заявок
- **20 образцов заявок** с разными приоритетами и датами
- **Комментарии и история** для демонстрации workflow

Все тестовые данные синтетические и безопасны для разработки.

#### Сброс и восстановление

**Создать резервную копию:**
```bash
# SQLite резервная копия
make backup
# Создаст: backup_requests_YYYYMMDD_HHMMSS.db.gz
```

**Восстановить из резервной копии:**
```bash
make restore BACKUP_FILE=backup_requests_20261115_180000.db.gz
```

**Просмотр статистики БД:**
```bash
make db-stats
```

**Интерактивный доступ к БД:**
```bash
# Откроет sqlite3 командную строку
make db-shell

# Примеры SQL запросов
sqlite> SELECT COUNT(*) FROM Requests;
sqlite> SELECT * FROM Users LIMIT 5;
sqlite> .tables
```

#### Интеграция с Docker

Если вы используете Docker Compose, база данных автоматически инициализируется при запуске:

```bash
# При первом запуске Docker будет инициализировать БД с тестовыми данными
docker-compose up -d

# Проверить логи инициализации
docker-compose logs app
```

#### Переключение между окружениями

Вы можете использовать разные базы данных для разработки, тестирования и production:

```bash
# Разработка
export DATABASE_URL=sqlite:///./requests-dev.db
make init-db

# Тестирование
export DATABASE_URL=sqlite:///./requests-test.db
make init-db

# Production (обычно PostgreSQL, не SQLite)
export DATABASE_URL=postgresql://user:pass@host/db
# Инициализация через миграции (в будущем через Alembic)
```

#### Диагностика проблем

Если инициализация БД не работает:

```bash
# Проверить существование БД файла
ls -lh requests.db

# Проверить целостность БД
sqlite3 requests.db "PRAGMA integrity_check;"

# Просмотреть структуру таблиц
sqlite3 requests.db ".schema"

# Проверить количество записей
sqlite3 requests.db "SELECT COUNT(*) FROM Requests;"

# Посмотреть логи приложения
tail -f logs/app.log
```

### Использование CLI

#### Справка по командам
```powershell
python -m request_system --help
```

#### Регистрация заявки

Для регистрации нужны существующие в базе заявитель, категория и статус `Новая`:

```powershell
python -m request_system create --help
```

Пример (с помощью демонстрационных данных):

```powershell
$demoDb = '.\request-system-demo.db'
if (Test-Path $demoDb) { throw 'Выберите другой путь для копии fixture или удалите существующую копию.' }
Copy-Item .\docs\sql\sample-data.sqlite3 $demoDb
$env:REQUEST_SYSTEM_DB = (Resolve-Path $demoDb).Path
python -m request_system
```

В приглашении fixture введите:
- ID заявителя: `1`
- ID категории: `1`
- Описание заявки: любой текст

Завершите работу:
```powershell
Remove-Item Env:REQUEST_SYSTEM_DB
```

#### Просмотр заявок

```powershell
python -m request_system get <id>        # Получить заявку по ID
python -m request_system list            # Список всех заявок
```

### Тестирование

Запустите все тесты:

```powershell
python -m unittest discover -s tests -v
```

Или с использованием pytest (если установлен):

```powershell
pytest tests/ -v
```

### Полный цикл разработки

```powershell
# 1. Активируйте окружение
.\.venv\Scripts\Activate.ps1

# 2. Установите зависимости в режиме разработки
python -m pip install -e .

# 3. Инициализируйте БД
python -c "from pathlib import Path; from request_system.infrastructure.database.sqlite import SQLiteDatabase; SQLiteDatabase('request-system.db', Path('docs/sql/schema.sql')).initialize()"

# 4. Запустите тесты
python -m unittest discover -s tests -v

# 5. Используйте CLI
python -m request_system --help
```

## 🌐 REST API

### Быстрый старт

#### 1. Запустите API сервер

```powershell
# Режим разработки (с автоперезагрузкой)
python -m uvicorn src.request_system.presentation.main:app --reload --host 0.0.0.0 --port 8000

# Режим production
uvicorn src.request_system.presentation.main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 2. Документация API

Когда сервер запущен, откройте интерактивную документацию:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### API Endpoints

Все endpoints требуют заголовок `Content-Type: application/json`.

#### 1. **Создать заявку** (POST)
```
POST /api/requests
```
Создает новую заявку.

**Тело запроса:**
```json
{
  "description": "Требуется офисное оборудование",
  "category_id": 1,
  "applicant_user_id": 1,
  "priority": "Высокий"
}
```

**Ответ (201 Created):**
```json
{
  "request": {
    "request_id": 123,
    "request_number": "REQ-A1B2C3D4...",
    "description": "Требуется офисное оборудование",
    "category_id": 1,
    "applicant_user_id": 1,
    "priority": "Высокий",
    "status": "Новая",
    "registered_at": "2026-11-15T18:00:00Z"
  }
}
```

#### 2. **Получить заявку** (GET)
```
GET /api/requests/{id}
```
Получить одну заявку по ID.

**Пример:**
```bash
curl http://localhost:8000/api/requests/123
```

**Ответ (200 OK):**
```json
{
  "request": {
    "request_id": 123,
    "request_number": "REQ-A1B2C3D4...",
    "description": "Требуется офисное оборудование",
    "applicant_user_id": 1,
    "user_name": "John Doe",
    "category_id": 1,
    "category_name": "IT",
    "priority": "Высокий",
    "status": "В работе",
    "registered_at": "2026-11-15T18:00:00Z"
  },
  "user": {
    "user_id": 1,
    "name": "John Doe"
  },
  "category": {
    "category_id": 1,
    "name": "IT"
  }
}
```

#### 3. **Список заявок** (GET)
```
GET /api/requests?[фильтры][&sort_by=...][&limit=...][&offset=...]
```
Получить список заявок с фильтрацией, поиском, сортировкой и пагинацией.

**Query параметры:**

| Параметр | Описание | Пример |
|----------|---------|--------|
| `user_id` | Фильтр по ID пользователя | `1` |
| `category_id` | Фильтр по ID категории | `2` |
| `status` | Фильтр по статусу (Новая, В работе, На проверке, Одобрена, Отклонена, Завершена) | `В работе` |
| `priority` | Фильтр по приоритету (Низкий, Средний, Высокий, Критический) | `Высокий` |
| `account_name` | Фильтр по имени пользователя (подстрока, без учета регистра) | `john` |
| `search` | Полнотекстовый поиск в description и account_name | `договор` |
| `search_description` | Поиск только в description | `оборудование` |
| `sort_by` | Поле для сортировки (created_at, id, priority, status, account_name). По умолчанию: created_at | `priority` |
| `sort_order` | Порядок сортировки (asc, desc). По умолчанию: desc | `asc` |
| `limit` | Размер страницы (1-100). По умолчанию: 10 | `20` |
| `offset` | Смещение от начала. По умолчанию: 0 | `10` |
| `page` | Номер страницы (альтернатива offset) | `2` |

**Примеры запросов:**
```bash
# Базовый список (все заявки)
curl http://localhost:8000/api/requests

# Фильтр по пользователю и статусу
curl "http://localhost:8000/api/requests?user_id=1&status=В работе"

# Полнотекстовый поиск
curl "http://localhost:8000/api/requests?search=договор"

# Сортировка по приоритету (убывающий порядок)
curl "http://localhost:8000/api/requests?sort_by=priority&sort_order=desc"

# Пагинация (страница 2, 20 элементов на страницу)
curl "http://localhost:8000/api/requests?limit=20&page=2"

# Комбинация: фильтр + поиск + сортировка + пагинация
curl "http://localhost:8000/api/requests?user_id=1&status=В работе&search=договор&sort_by=created_at&sort_order=desc&limit=10&offset=0"
```

**Ответ (200 OK):**
```json
{
  "requests": [
    {
      "request_id": 1,
      "request_number": "REQ-A1B2C3D4...",
      "description": "Требуется офисное оборудование",
      "applicant_user_id": 1,
      "user_name": "John Doe",
      "category_id": 1,
      "category_name": "IT",
      "priority": "Высокий",
      "status": "В работе",
      "registered_at": "2026-11-15T18:00:00Z"
    }
  ],
  "total_count": 100,
  "filtered_count": 15,
  "returned_count": 10,
  "limit": 10,
  "offset": 0,
  "has_next": true,
  "has_previous": false
}
```

#### 4. **Обновить заявку** (PATCH)
```
PATCH /api/requests/{id}
```
Обновить описание заявки (только для заявок со статусом "Новая").

**Тело запроса:**
```json
{
  "new_description": "Обновленное описание"
}
```

**Ответ (200 OK):**
```json
{
  "request": {...},
  "updated_fields": ["description"],
  "updated_at": "2026-11-15T18:30:00Z"
}
```

#### 5. **Изменить статус заявки** (PUT)
```
PUT /api/requests/{id}/status
```
Изменить статус заявки (допустимые переходы зависят от текущего статуса).

**Тело запроса:**
```json
{
  "new_status_name": "В работе",
  "actor_user_id": 2,
  "explanation": "Начинаем работу над заявкой"
}
```

**Ответ (200 OK):**
```json
{
  "request": {...},
  "history_record": {
    "old_status": "Новая",
    "new_status": "В работе",
    "changed_by": 2,
    "explanation": "Начинаем работу над заявкой",
    "changed_at": "2026-11-15T18:30:00Z"
  }
}
```

### HTTP Коды состояния

Все endpoints возвращают правильные HTTP коды:

| Код | Значение | Описание |
|-----|----------|---------|
| `200` | OK | Успешный GET/PATCH/PUT |
| `201` | Created | Успешный POST |
| `204` | No Content | Успешный DELETE |
| `400` | Bad Request | Некорректный ввод или ошибка валидации |
| `404` | Not Found | Ресурс не найден |
| `409` | Conflict | Конфликт состояния (например, недопустимый переход статуса) |
| `500` | Internal Server Error | Ошибка сервера |

### Формат ошибок

Все ошибки следуют единому формату:

```json
{
  "code": "ERROR_CODE",
  "message": "Сообщение об ошибке на понятном языке",
  "status_code": 400,
  "timestamp": "2026-11-15T18:00:00Z",
  "path": "/api/requests/123",
  "details": {
    "field": "description",
    "reason": "too_short",
    "constraint": "minLength=10"
  }
}
```

Коды ошибок:
- `VALIDATION_ERROR` - Некорректный ввод (400)
- `REQUEST_NOT_FOUND` - Заявка не найдена (404)
- `USER_NOT_FOUND` - Пользователь не найден (404)
- `CATEGORY_NOT_FOUND` - Категория не найдена (404)
- `INVALID_TRANSITION` - Недопустимый переход статуса (409)
- `CANNOT_UPDATE` - Невозможно обновить в текущем состоянии (409)
- `INTERNAL_ERROR` - Ошибка сервера (500)

### Примеры использования curl

```bash
# Создать заявку
curl -X POST http://localhost:8000/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Требуется оборудование для команды",
    "category_id": 1,
    "applicant_user_id": 1,
    "priority": "Высокий"
  }'

# Получить все заявки
curl http://localhost:8000/api/requests

# Поиск заявок
curl "http://localhost:8000/api/requests?search=оборудование"

# Фильтр и пагинация
curl "http://localhost:8000/api/requests?user_id=1&limit=5&offset=0"

# Получить конкретную заявку
curl http://localhost:8000/api/requests/123

# Обновить заявку
curl -X PATCH http://localhost:8000/api/requests/123 \
  -H "Content-Type: application/json" \
  -d '{"new_description": "Обновленное описание"}'

# Изменить статус
curl -X PUT http://localhost:8000/api/requests/123/status \
  -H "Content-Type: application/json" \
  -d '{
    "new_status_name": "В работе",
    "actor_user_id": 2,
    "explanation": "Начинаем работу"
  }'
```

## 🐳 Docker

Приложение готово к развертыванию в контейнере с использованием Docker и Docker Compose.

### Требования

- Docker 20.10+
- Docker Compose 1.29+

### Сборка Docker образа

Построить Docker образ для приложения:

```bash
# Сборка образа
docker build -t request-system:latest .

# С tag для репозитория
docker build -t myregistry/request-system:1.1.0 .
```

### Запуск приложения с Docker

Запустить контейнер с локальным SQLite:

```bash
# Базовый запуск
docker run -p 8000:8000 request-system:latest

# С переменными окружения
docker run -p 8000:8000 \
  -e APP_ENV=development \
  -e APP_DEBUG=true \
  -e DATABASE_URL=sqlite:///./requests.db \
  request-system:latest

# С монтированием volume для БД
docker run -p 8000:8000 \
  -v $(pwd)/data:/app/data \
  request-system:latest
```

### Docker Compose (Рекомендуется)

Docker Compose упрощает управление контейнером и переменными окружения:

#### 1. Подготовка

```bash
# Скопируйте .env.example в .env
cp .env.example .env

# Отредактируйте .env под вашу конфигурацию (если нужно)
# nano .env
```

#### 2. Запуск сервиса

```bash
# Запустить в фоне
docker-compose up -d

# Запустить с выводом логов
docker-compose up

# Пересобрать образ и запустить
docker-compose up -d --build
```

#### 3. Просмотр логов

```bash
# Все логи
docker-compose logs -f

# Только логи приложения
docker-compose logs -f app
```

#### 4. Остановка сервиса

```bash
# Остановить контейнеры
docker-compose stop

# Остановить и удалить контейнеры
docker-compose down

# Остановить и удалить всё (включая volumes)
docker-compose down -v
```

### Доступ к API в Docker

Когда контейнер запущен, API доступна по адресу:

| Ресурс | URL |
|--------|-----|
| **Swagger UI** | http://localhost:8000/docs |
| **ReDoc** | http://localhost:8000/redoc |
| **API Endpoints** | http://localhost:8000/api/requests |
| **Health Check** | http://localhost:8000/health |
| **OpenAPI JSON** | http://localhost:8000/openapi.json |

### Примеры запросов из Docker

```bash
# Проверить здоровье сервиса
curl http://localhost:8000/health

# Получить список заявок
curl http://localhost:8000/api/requests

# Создать заявку
curl -X POST http://localhost:8000/api/requests \
  -H "Content-Type: application/json" \
  -d '{
    "description": "Тестовая заявка из Docker",
    "category_id": 1,
    "applicant_user_id": 1,
    "priority": "Средний"
  }'
```

### Переменные окружения в Docker

Используйте файл `.env` или переданные переменные для конфигурации:

```env
# Application
APP_ENV=development              # development, staging, production
APP_DEBUG=false                  # Отладка
APP_PORT=8000                    # Порт контейнера
APP_WORKERS=4                    # Workers (production only)

# Database
DATABASE_URL=sqlite:///./requests.db  # Путь БД
DATABASE_POOL_SIZE=10            # Размер пула

# API
API_TITLE=Request System API     # Название API
API_VERSION=1.1.0                # Версия API
API_CORS_ORIGINS=*               # CORS origins

# Logging
LOG_LEVEL=INFO                   # DEBUG, INFO, WARNING, ERROR
```

### Мониторинг контейнера

#### Health Check

Контейнер включает встроенный health check:

```bash
# Проверить статус контейнера
docker ps --format "table {{.Names}}\t{{.Status}}"

# Должен показать: "healthy" или "starting"
```

#### Просмотр ресурсов

```bash
# Использование CPU и памяти
docker stats request-system-api

# Информация о контейнере
docker inspect request-system-api
```

### Production Deployment

#### Multi-stage Build

Dockerfile использует multi-stage build для оптимизации размера образа:

- **Stage 1 (Builder)**: Установка зависимостей, сборка wheels
- **Stage 2 (Runtime)**: Компактный финальный образ с non-root пользователем

Размер образа: ~150MB (с python:3.11-slim базовым образом)

#### Security Best Practices

Контейнер включает встроенные security меры:

- ✅ Non-root пользователь (`appuser`)
- ✅ Минимальный базовый образ (`python:3.11-slim`)
- ✅ Read-only файловая система (можно настроить)
- ✅ Health check endpoint для мониторинга
- ✅ Отсутствие секретов в образе (используются env переменные)

#### Использование с оркестраторами (Kubernetes, Swarm)

```yaml
# Kubernetes deployment пример
apiVersion: apps/v1
kind: Deployment
metadata:
  name: request-system-api
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: api
        image: myregistry/request-system:1.1.0
        ports:
        - containerPort: 8000
        env:
        - name: APP_ENV
          value: "production"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
        livenessProbe:
          httpGet:
            path: /health
            port: 8000
          initialDelaySeconds: 10
          periodSeconds: 30
```

### Управление портами (Port Mapping)

Docker контейнер имеет собственное сетевое пространство. Порты контейнера нужно пробросить на хост для доступа.

**Формат port mapping:** `<external_port>:<internal_port>`
- **External port** - порт на хост-машине (видна снаружи)
- **Internal port** - порт внутри контейнера (где слушает приложение, 8000)

#### Примеры

```bash
# По умолчанию: внешний 8000 -> внутренний 8000
docker run -p 8000:8000 request-system:latest
# Доступ: http://localhost:8000

# Внешний 9000 -> внутренний 8000
docker run -p 9000:8000 request-system:latest
# Доступ: http://localhost:9000

# Разные внешние порты
docker run -p 8000:8000 request-system:latest
docker run -p 8001:8000 request-system:latest  # Второй контейнер на другом порту
# Доступ: http://localhost:8000 и http://localhost:8001

# Явно указать IP хоста
docker run -p 0.0.0.0:8000:8000 request-system:latest  # Все интерфейсы
docker run -p 127.0.0.1:8000:8000 request-system:latest  # Только localhost
```

#### Изменение порта в Docker Compose

**docker-compose.yml:**
```yaml
services:
  app:
    ports:
      - "${APP_PORT:-8000}:8000"  # Используется APP_PORT из .env.docker или 8000 по умолчанию
    environment:
      APP_PORT: 8000  # Внутренний порт (внутри контейнера)
```

**Способы изменения:**
1. **Переменная окружения .env.docker:**
   ```env
   APP_PORT=9000  # Внешний порт станет 9000
   ```

2. **Команда строка:**
   ```bash
   APP_PORT=9000 docker-compose up -d
   ```

3. **Прямое редактирование:**
   ```yaml
   ports:
     - "9000:8000"  # Явное указание: внешний:внутренний
   ```

#### Проверка портов

```bash
# Какой порт слушает контейнер
docker ps
# Показывает: 0.0.0.0:8000->8000/tcp request-system-api

# Проверить доступность
curl http://localhost:8000/health
curl http://localhost:9000/health  # если изменили порт на 9000

# Какие процессы слушают портов на хосте (Linux/Mac)
netstat -tlnp | grep 8000
lsof -i :8000

# На Windows
netstat -ano | findstr :8000
```

## 🏥 Health Check

Приложение предоставляет endpoint `/health` для мониторинга состояния и используется Docker, Kubernetes и балансировщиками нагрузки для проверки здоровья приложения.

### Endpoints

#### GET /health - Полная проверка здоровья

Возвращает подробную информацию о состоянии приложения включая:
- Общее состояние (healthy, degraded, unhealthy)
- Версия API
- Время работы приложения (uptime)
- Статус базы данных
- Статус кэша (если настроен)
- Окружение (development, staging, production)
- Версия Python

**Запрос:**
```bash
curl http://localhost:8000/health
```

**Ответ (200 OK или 503 Service Unavailable):**
```json
{
  "status": "healthy",
  "version": "1.1.0",
  "timestamp": "2026-11-15T19:02:07Z",
  "uptime_seconds": 3600.5,
  "database": "ok",
  "cache": "ok",
  "environment": "development",
  "python_version": "3.11.0"
}
```

**HTTP коды:**
- `200 OK` - Приложение работает нормально (healthy или degraded)
- `503 Service Unavailable` - Критические сервисы недоступны (unhealthy)

#### GET /ready - Простая проверка готовности

Простой endpoint для быстрой проверки готовности приложения принимать запросы. Используется при быстрых проверках и в Kubernetes readiness probes.

**Запрос:**
```bash
curl http://localhost:8000/ready
```

**Ответ (200 OK):**
```json
{
  "ready": true
}
```

### Docker Health Check

Docker автоматически мониторит здоровье приложения используя endpoint `/health`.

**Просмотр статуса здоровья:**
```bash
# Показать статус контейнера (должен быть "healthy")
docker ps --format "table {{.Names}}\t{{.Status}}"
# Результат: request-system-api  Up 5 minutes (healthy)

# Получить детали здоровья контейнера
docker inspect --format='{{.State.Health.Status}}' request-system-api
# Результат: healthy

# Просмотреть логи health check
docker inspect request-system-api | grep -A 10 "Health"
```

### Docker Compose Health Check

Health check уже настроен в `docker-compose.yml`:

```yaml
services:
  app:
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
      interval: 30s        # Проверка каждые 30 секунд
      timeout: 10s         # Таймаут ответа 10 секунд
      retries: 3           # Попыток перед unhealthy
      start_period: 5s     # Благодатный период перед первой проверкой
```

**Конфигурация в .env:**
```env
# Health Check Configuration
HEALTH_CHECK_INTERVAL=30      # Интервал проверки (секунды)
HEALTH_CHECK_TIMEOUT=10       # Таймаут (секунды)
HEALTH_CHECK_START_PERIOD=5   # Благодатный период (секунды)
HEALTH_CHECK_RETRIES=3        # Максимум попыток
```

### Kubernetes Probes

Для развертывания в Kubernetes используйте health endpoints в probes конфигурации:

**Liveness Probe** (перезагрузить контейнер если unhealthy):
```yaml
livenessProbe:
  httpGet:
    path: /ready
    port: 8000
  initialDelaySeconds: 10      # Ждать 10 сек перед первой проверкой
  periodSeconds: 30            # Проверять каждые 30 сек
  timeoutSeconds: 5            # Таймаут ответа
  failureThreshold: 3          # Попыток перед перезагрузкой
```

**Readiness Probe** (удалить из балансировщика если не ready):
```yaml
readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5       # Ждать 5 сек перед первой проверкой
  periodSeconds: 10            # Проверять каждые 10 сек
  timeoutSeconds: 3            # Таймаут ответа
  failureThreshold: 2          # Попыток перед удалением
```

### Мониторинг и интеграция

Health endpoints интегрируются с популярными инструментами мониторинга:

- **Prometheus**: Scrape `/health` для метрик
- **DataDog**: Использует `/health` для проверки доступности
- **NewRelic**: Интегрирует health checks для alerting
- **ELK Stack**: Агент собирает health статус
- **AWS ECS**: Использует `/health` для задач health check
- **Google Cloud Run**: Настраивается health check на `/ready`

### Тестирование Health Check

**Unit тесты:**
```bash
# Запустить тесты health check
pytest tests/test_health_check.py -v

# С покрытием
pytest tests/test_health_check.py --cov=src/request_system/application/services/health_service
```

**Integration тесты:**
```bash
# Запустить контейнер и проверить health
docker-compose up -d
sleep 5
curl http://localhost:8000/health | jq '.'

# Проверить health status контейнера
docker-compose ps
```

**Load test (проверить отклик под нагрузкой):**
```bash
# Использовать hey или ab
hey -n 1000 -c 10 http://localhost:8000/health
```

### Troubleshooting

**Контейнер marked as unhealthy:**
1. Проверить логи: `docker-compose logs app`
2. Проверить ответ endpoint: `curl -v http://localhost:8000/health`
3. Проверить статус БД: `docker-compose logs db`
4. Проверить статус кэша: `docker-compose logs cache`

**Timeout health check:**
1. Увеличить HEALTH_CHECK_TIMEOUT в .env
2. Проверить ресурсы контейнера (CPU, память)
3. Проверить network latency: `docker exec request-system-api ping cache`

**Health check endpoint недоступен:**
1. Проверить что curl установлен: `docker-compose exec app which curl`
2. Проверить что app запущен: `docker-compose ps`
3. Проверить port binding: `docker port request-system-api`
4. Проверить firewall правила

---

## 🐳
netstat -ano | findstr :8000
```

#### Общие проблемы

**Проблема:** "Port 8000 is already in use"
```bash
# Решение 1: Изменить порт
APP_PORT=8001 docker-compose up -d

# Решение 2: Остановить конфликтующий контейнер
docker stop container_name
docker rm container_name
```

**Проблема:** Контейнер работает, но API недоступна
```bash
# Проверить логи
docker-compose logs app

# Проверить health check
curl http://localhost:8000/health

# Проверить что контейнер запущен
docker ps

# Проверить сетевое подключение
docker-compose exec app curl http://localhost:8000/health
```

**Проблема:** "Connection refused" при обращении к БД
```bash
# Проверить зависимости (depends_on)
docker-compose ps

# Должны быть: app, db, cache все в статусе "healthy"

# Ждать готовности БД
./scripts/wait-for-db.sh
```

## 🐳 Docker Compose - Multi-Service Deployment

Comprehensive Docker Compose setup with support for different deployment scenarios:
- **Development**: SQLite database, live code reload
- **Development + Tools**: PostgreSQL, Redis, pgAdmin
- **Production**: PostgreSQL, Redis, optimized settings

### Quick Start - Development (SQLite)

```bash
# Basic setup (no database tools needed)
docker-compose up -d

# Access API
curl http://localhost:8000/health

# View logs
docker-compose logs -f app

# Stop
docker-compose down
```

### Development with Database Tools

For PostgreSQL database management and Redis caching:

```bash
# Copy environment file (or use defaults)
cp .env.docker.example .env.docker

# Start with dev profile (includes pgAdmin)
docker-compose --profile dev up -d

# Access services
# API: http://localhost:8000/docs
# pgAdmin: http://localhost:5050 (admin@example.com / admin)
# Redis: localhost:6379
# PostgreSQL: localhost:5432

# View logs
docker-compose logs -f app

# Database shell
docker-compose exec db psql -U postgres -d requests_db

# Stop
docker-compose down
```

### Production Deployment

```bash
# Copy and configure environment
cp .env.docker.example .env.docker
# Edit .env.docker with production values:
# - Set APP_ENV=production
# - Set strong DB_PASSWORD
# - Set LOG_LEVEL=WARNING
# - Configure DATABASE_URL for PostgreSQL

# Start with production overrides
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# View logs
docker-compose logs -f app

# Database backup
docker-compose exec db pg_dump -U postgres requests_db > backup.sql

# Database restore
docker-compose exec -T db psql -U postgres requests_db < backup.sql

# Stop (keep data)
docker-compose down

# Stop and remove all data
docker-compose down -v
```

### Services Overview

| Service | Container | Image | Port | Purpose |
|---------|-----------|-------|------|---------|
| **app** | request-system-api | python:3.11-slim | 8000 | FastAPI application |
| **db** | request-system-db | postgres:15-alpine | 5432 | PostgreSQL database |
| **cache** | request-system-cache | redis:7-alpine | 6379 | Redis cache |
| **pgadmin** | request-system-pgadmin | pgadmin4 | 5050 | Database UI (dev only) |

### Configuration Files

- **docker-compose.yml** - Main configuration (SQLite by default)
- **docker-compose.dev.yml** - Development overrides (PostgreSQL + Redis profiles)
- **docker-compose.prod.yml** - Production overrides (optimized settings, no dev tools)
- **.env.docker.example** - Environment template (copy to .env.docker)

### Common Commands

```bash
# Start services
docker-compose up -d

# Stop services
docker-compose stop

# View logs (all)
docker-compose logs -f

# View logs (specific service)
docker-compose logs -f app
docker-compose logs -f db
docker-compose logs -f cache

# Execute commands in container
docker-compose exec app bash
docker-compose exec db psql -U postgres

# Database operations
# Backup
docker-compose exec db pg_dump -U postgres requests_db > backup.sql
# Restore
cat backup.sql | docker-compose exec -T db psql -U postgres -d requests_db

# Redis operations
docker-compose exec cache redis-cli

# Check health
docker-compose ps

# Remove all (including volumes)
docker-compose down -v
```

### Profiles (Selective Service Startup)

```bash
# Start only API (SQLite, no external services)
docker-compose up -d

# Add PostgreSQL and Redis
docker-compose --profile postgres --profile redis up -d

# Add pgAdmin for database management
docker-compose --profile dev up -d

# Production with all databases
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### Health Checks

Each service includes health checks:

```bash
# Check service status
docker-compose ps

# Should show: "healthy" or "starting"

# Check all services health
python scripts/healthcheck.py
```

### Environment Variables

Key environment variables in .env.docker:

```env
# Development
APP_ENV=development
APP_DEBUG=true
LOG_LEVEL=DEBUG

# Production
APP_ENV=production
APP_DEBUG=false
LOG_LEVEL=WARNING

# Database (SQLite or PostgreSQL)
DATABASE_URL=sqlite:///./requests.db  # or postgresql://...

# Redis (optional)
REDIS_URL=redis://cache:6379/0

# PostgreSQL credentials
DB_USER=postgres
DB_PASSWORD=postgres
DB_NAME=requests_db
```

### Troubleshooting

**API won't start:**
```bash
# Check logs
docker-compose logs app

# Verify health check
curl http://localhost:8000/health
```

**Database connection failed:**
```bash
# Check database service
docker-compose logs db

# Wait for database to be ready
docker-compose exec app python scripts/wait-for-db.sh
```

**Permission denied errors:**
```bash
# Run with proper permissions
docker-compose exec -u appuser app bash

# For root access (if needed)
docker-compose exec app bash
```

**Volume/data persistence:**
```bash
# Check volumes
docker volume ls

# Inspect volume
docker volume inspect <volume_name>

# Clean up unused volumes
docker volume prune
```

### 📋 Дополнительные ресурсы

- **Swagger UI** (Интерактивное тестирование API): http://localhost:8000/docs
- **OpenAPI Спецификация**: http://localhost:8000/openapi.json
- **API Документация**: См. `docs/search-and-filtering.md` для подробных примеров
- **Постман коллекция**: См. `docs/postman-collection.json` для предготовленных запросов
- **Руководство по Swagger UI**: См. `docs/SWAGGER-UI-GUIDE.md` для быстрого старта

## Документация и материалы

- [Предметные модули и их распределение по слоям](docs/modular-decomposition.md)
- [Концептуальные сущности и связи](docs/domain-entities.md)
- [Архитектура хранения данных](docs/architecture/persistence.md)
- [ER-диаграмма таблиц](docs/architecture/er-diagram.md)
- [SQL-схема, тестовые данные и примеры запросов](docs/sql/README.md)
- [Прототипы интерфейса в Figma и PNG-экспорты](docs/prototypes/README.md)

## ?? Remote Verification & Testing

Complete verification procedures for ensuring your API deployment is working correctly on local machines, VPS, or cloud platforms.

### Quick Verification

**Local verification:**
`ash
# Verify local deployment
make verify-local

# Or directly
bash scripts/remote-verify.sh localhost 8000
`

**Remote verification:**
`ash
# Verify remote VPS deployment
make verify-remote

# Or directly
bash scripts/remote-verify.sh 192.168.1.100 8000
`

### Full Deployment + Verification

Deploy to VPS and run all verification tests:
`ash
make deploy-and-verify

# Or directly
bash scripts/full-deploy-and-verify.sh 192.168.1.100 ubuntu 22
`

**What this does:**
1. ? SSH connectivity check
2. ? System updates
3. ? Docker installation
4. ? Repository deployment
5. ? Environment setup
6. ? Database initialization
7. ? Health checks
8. ? Full API verification (15+ tests)

### Integration Testing

Run comprehensive test suite:
`ash
# Run all integration tests
make test-remote

# With coverage report
make test-remote-coverage

# Against remote server
API_BASE_URL=http://192.168.1.100:8000 make test-remote-server
`

**Tests included:**
- Connectivity tests (health, ready, docs)
- CRUD operations (create, read, update, delete)
- Filtering & search
- Pagination & sorting
- Data integrity
- Error handling
- Performance (response times)

### Postman Collection

Import postman/Request-System-API.json into Postman for manual testing:

1. Open Postman
2. Click "Import"
3. Choose postman/Request-System-API.json
4. Update ase_url variable for your environment
5. Start testing!

**Included requests:**
- Health checks
- List, create, read, update, delete requests
- Filtering by status, priority, category
- Search & pagination
- Sorting

### Manual Testing Examples

`ash
# Health check
curl http://192.168.1.100:8000/health | jq .

# List requests
curl http://192.168.1.100:8000/api/requests | jq .

# Filter by status
curl "http://192.168.1.100:8000/api/requests?status=submitted" | jq .

# Search
curl "http://192.168.1.100:8000/api/requests?search=IT" | jq .

# Pagination
curl "http://192.168.1.100:8000/api/requests?limit=10&offset=0" | jq .

# Create request
curl -X POST http://192.168.1.100:8000/api/requests \
  -H "Content-Type: application/json" \
  -d '{"user_id": 1, "category_id": 1, "title": "Test", "description": "Test", "priority": 2}'
`

### Documentation

For comprehensive verification guide, see [docs/VERIFICATION.md](docs/VERIFICATION.md):
- All test procedures
- Expected responses
- Troubleshooting guide
- Performance benchmarks
- API endpoints reference

