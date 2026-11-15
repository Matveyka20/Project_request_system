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
