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

Приложение автоматически создаёт таблицы при первом запуске в файл `request-system.db`. Вы также можете инициализировать схему вручную:

```powershell
python -c "from pathlib import Path; from request_system.infrastructure.database.sqlite import SQLiteDatabase; SQLiteDatabase('request-system.db', Path('docs/sql/schema.sql')).initialize()"
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

### Дополнительные ресурсы

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
