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

## Документация и материалы

- [Предметные модули и их распределение по слоям](docs/modular-decomposition.md)
- [Концептуальные сущности и связи](docs/domain-entities.md)
- [Архитектура хранения данных](docs/architecture/persistence.md)
- [ER-диаграмма таблиц](docs/architecture/er-diagram.md)
- [SQL-схема, тестовые данные и примеры запросов](docs/sql/README.md)
- [Прототипы интерфейса в Figma и PNG-экспорты](docs/prototypes/README.md)
