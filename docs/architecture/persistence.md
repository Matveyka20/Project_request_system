# Persistence-слой

Реализация разделяет доменную модель, контракт доступа к данным и конкретный SQLite-адаптер:

| Слой | Модуль | Ответственность |
|---|---|---|
| Domain | `src/request_system/domain/entities.py` | Типизированные сущности без зависимости от БД и инфраструктуры. |
| Application service | `src/request_system/application/services/request_service.py` | Валидация и оркестрация бизнес-сценария регистрации заявки. |
| Application ports | `src/request_system/application/ports/persistence.py` | Контракт CRUD-репозитория, поиска статуса, расширенный контракт заявок и Unit of Work. |
| Infrastructure adapter | `src/request_system/infrastructure/database/sqlite/` | Подключение SQLite, преобразование сущностей в строки таблиц и реализация портов. |

Сервис зависит только от доменных типов и портов; он не импортирует SQLite или presentation. SQL-адаптер отвечает за сохранение, чтение и соблюдение схемы, но не за правила регистрации. Интерфейс отвечает только за ввод, вызов сервиса и форматирование результата. API-контракт и другие пользовательские сценарии не расширяются.

## Охват схемы

Каждой таблице `docs/sql/schema.sql` соответствует доменная сущность и CRUD-репозиторий Unit of Work:

| Таблица | Сущность |
|---|---|
| `Users` | `User` |
| `Roles` | `Role` |
| `Statuses` | `Status` |
| `Categories` | `Category` |
| `Requests` | `Request` |
| `UserRoles` | `UserRole` |
| `Comments` | `Comment` |
| `RequestHistory` | `RequestHistory` |
| `Assignments` | `Assignment` |
| `Attachments` | `Attachment` |
| `ResultSubmissions` | `ResultSubmission` |
| `AcceptanceDecisions` | `AcceptanceDecision` |

Идентификаторы строк генерирует SQLite; у `UserRole` используется составной ключ `(user_id, role_id)`. Даты хранятся в SQLite как ISO 8601 `TEXT` и представлены в Python как `datetime`. `AcceptanceOutcome` и `Comment.is_service` преобразуются при чтении и записи в типизированные значения Python.

У `UserRoles` нет полей вне первичного ключа; для изменения такой связи запись удаляют и добавляют заново. `update` для существующей строки связи подтверждает её наличие без изменения ключа.

## Регистрация заявки

`RequestService.register` реализует ограниченный сценарий создания заявки. Он:

1. отклоняет пустое описание и некорректные идентификаторы до открытия Unit of Work;
2. проверяет, что заявитель и категория существуют, и находит начальный статус по имени `Новая`;
3. обрезает пробелы в описании, создаёт уникальный номер `REQ-<UUID>` и получает текущее время в UTC;
4. передаёт `Request` и автора/статус начального события через порт `RequestRepository.create_with_initial_status`;
5. возвращает зарегистрированную заявку и её начальный статус для presentation.

Ошибки пользовательского ввода представлены `RequestValidationError` с сообщениями по полям. Если статус `Новая` не настроен, сервис выбрасывает `InitialStatusNotConfigured`; заявка при этом не создаётся. Идентификаторы пользователя, категории и статуса должны быть предварительно заведены в справочниках. Роль пользователя, вложения, назначения и последующая обработка остаются за пределами этого сценария.

## CLI и обработка ошибок

`presentation/cli.py` только читает ID и описание, проверяет, что ID записаны целыми числами, вызывает `RequestService` и форматирует результат. Проверки положительности ID, обязательности описания и наличия пользователя/категории выполняет application service. CLI без traceback показывает `CliInputError`, `RequestValidationError`, `InitialStatusNotConfigured` и `PersistenceError`; для ошибок ввода/настроек возвращается код `2`, для ошибок хранилища — `3`. `EOFError` считается завершением ввода, `KeyboardInterrupt` — отменой с кодом `130`. Другие исключения не перехватываются и не выдаются за успешную регистрацию.

SQLite-адаптер преобразует ошибки SQLite в `PersistenceError`, сохраняя исходную причину в цепочке исключений. Сервис и CLI не импортируют SQLite; unexpected ошибки приложения не преобразуются в `PersistenceError`.

## Транзакции и начальный статус

Все репозитории одного `SQLiteUnitOfWork` используют одно соединение. Контекст Unit of Work фиксирует транзакцию при штатном выходе и откатывает при исключении. Внешние ключи включаются на каждом соединении.

Начальное событие статуса обязательно создаётся вместе с заявкой. Application service задаёт автора, статус и отсутствие предыдущего статуса; порт `RequestRepository.create_with_initial_status` связывает событие с выданным БД ID заявки, вставляет обе строки в одной транзакции и использует savepoint для совместного отката при ошибке. Текущий статус не дублируется в `Requests`; он определяется последним событием `RequestHistory` согласно порядку, указанному в SQL-схеме.

## Инициализация

Для нового файла БД укажите путь к существующей схеме:

```python
from pathlib import Path

from request_system.infrastructure.database.sqlite import SQLiteDatabase

database = SQLiteDatabase(
    "request-system.db",
    Path("docs/sql/schema.sql"),
)
database.initialize()
```

Для операций используйте один Unit of Work на транзакцию:

```python
from request_system.application.services import CreateRequestCommand, RequestService

service = RequestService(database.unit_of_work)
result = service.register(
    CreateRequestCommand(
        applicant_user_id=1,
        description="Не работает проектор",
        category_id=1,
    )
)
print(result.request.request_number, result.initial_status.name)
```

Сервис сам открывает Unit of Work через переданный портовый factory. На уровне адаптера прямые операции выполняются через контекстный менеджер Unit of Work: выход фиксирует транзакцию и закрывает соединение, а исключения приводят к откату.
