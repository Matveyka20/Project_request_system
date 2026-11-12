# Phase 1: Домен и наслойка persistence layer

## Описание
Имплементация основного слоя архитектуры: доменные сущности и persistence layer с SQLite адаптером.

## Что включает
- **12 entity dataclass сущностей** (домен слой):
  - User, Role, Status, Category, Request, RequestHistory, Permission, и другие
  - Полная валидация и связи между сущностями

- **Persistence ports** (abstract interfaces):
  - CrudRepository - базовый CRUD интерфейс
  - RequestRepository - специализированный репозиторий для Request'ов
  - StatusRepository - специализированный репозиторий для Status'ов
  - UnitOfWork - управление транзакциями и SAVEPOINT'ами

- **SQLite adapter в infrastructure layer**:
  - SQLiteRepository - имплементация CrudRepository
  - SQLiteRequestRepository - имплементация RequestRepository
  - SQLiteStatusRepository - имплементация StatusRepository
  - SQLiteUnitOfWork - имплементация UnitOfWork с SAVEPOINT поддержкой
  - Database initialization и миграции

- **12 таблиц в БД**:
  - С constraints (PRIMARY KEY, FOREIGN KEY, NOT NULL, UNIQUE, CHECK)
  - PRAGMA foreign_keys = ON для целостности данных
  - Индексы для оптимизации запросов

- **Atomicity через SAVEPOINT**:
  - Request + RequestHistory коммитятся атомарно
  - Откат в случае ошибок
  - Transaction management

- **9 integration тестов**:
  - Тестирование всех операций CRUD
  - Тестирование связей между сущностями
  - Тестирование atomicity и rollback'а
  - Тестирование constraints и validations

## Технологический стек
- Python 3.8+
- SQLite (встроенное в Python)
- Dataclasses для сущностей
- Abstract Base Classes для ports
- pytest для тестирования

## Структура кода
```
src/request_system/
  domain/
    entities.py          # 12 dataclass сущностей
  application/
    ports/
      persistence.py     # Abstract interfaces
  infrastructure/
    database/
      sqlite/
        database.py      # SQLite connection & init
        repositories.py  # SQLite adapter имплементация
        unit_of_work.py  # UnitOfWork с SAVEPOINT
```

## Статус
✅ Полностью имплементирована
✅ Все тесты проходят
✅ Готова для Phase 2+3 (бизнес-логика и CLI)
