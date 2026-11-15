-- Test data population for the Request System.
-- Schema-safe seed file: uses ON CONFLICT DO NOTHING on all inserts.
-- Initialize the database with schema.sql first.
--
-- Usage:
--   sqlite3 request-system.db < scripts/populate_test_data.sql
--
-- Contains:
--   • 4 users (user_id 1-4)
--   • 4 categories (category_id 1-4)
--   • 6 statuses (status_id 1-6)
--   • 10 requests (request_id 1-10) with realistic distributions
--   • RequestHistory entries for status transitions

PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

-- Insert Statuses (1-6)
INSERT INTO Statuses (status_id, name) VALUES
    (1, 'Новая'),
    (2, 'В работе'),
    (3, 'На проверке'),
    (4, 'Одобрена'),
    (5, 'Отклонена'),
    (6, 'Завершена')
ON CONFLICT (status_id) DO NOTHING;

-- Insert Categories (1-4)
INSERT INTO Categories (category_id, name) VALUES
    (1, 'Нестабильность системы'),
    (2, 'Новая функция'),
    (3, 'Отчёты и аналитика'),
    (4, 'Улучшение процесса')
ON CONFLICT (category_id) DO NOTHING;

-- Insert Users (1-4)
INSERT INTO Users (user_id, account, name, contacts) VALUES
    (1, 'user1', 'Алексей Королев', NULL),
    (2, 'user2', 'Мария Петрова', NULL),
    (3, 'user3', 'Николай Иванов', NULL),
    (4, 'user4', 'Ольга Смирнова', NULL)
ON CONFLICT (user_id) DO NOTHING;

-- Insert Requests (1-10)
-- Requests 1-3: status "Новая"
-- Requests 4-6: status "В работе"
-- Requests 7-8: status "На проверке"
-- Request 9: status "Одобрена"
-- Request 10: status "Завершена"
INSERT INTO Requests (
    request_id, request_number, description, applicant_user_id, category_id, registered_at
) VALUES
    (1, 'REQ-001', 'Система часто зависает при обработке больших объёмов данных. Требуется оптимизировать алгоритмы обработки информации.', 1, 1, '2026-11-02T09:00:00Z'),
    (2, 'REQ-002', 'Необходимо реализовать экспорт отчётов в формате PDF с сохранением форматирования и стилей оригинального документа.', 2, 2, '2026-11-03T10:15:00Z'),
    (3, 'REQ-003', 'Аналитика должна показывать распределение заявок по категориям в виде диаграмм и графиков для лучшей визуализации.', 3, 3, '2026-11-04T11:30:00Z'),
    (4, 'REQ-004', 'Процесс назначения исполнителей требует автоматизации на основе навыков и текущей нагрузки сотрудников системы.', 4, 4, '2026-11-05T08:30:00Z'),
    (5, 'REQ-005', 'Интеграция с системой уведомлений для отправки SMS и email участникам по изменению статуса заявки в реальном времени.', 1, 1, '2026-11-06T09:45:00Z'),
    (6, 'REQ-006', 'Отчёты по времени выполнения заявок не соответствуют требуемому формату. Необходимо пересмотреть структуру данных.', 2, 2, '2026-11-07T10:00:00Z'),
    (7, 'REQ-007', 'Требуется расширить возможности фильтрации заявок по нескольким критериям одновременно для удобства пользователей.', 3, 3, '2026-11-08T11:15:00Z'),
    (8, 'REQ-008', 'Необходимо добавить возможность прикрепления документов и изображений к заявкам при регистрации и обработке.', 4, 4, '2026-11-09T08:20:00Z'),
    (9, 'REQ-009', 'Система должна сохранять полную историю всех изменений описания заявки с указанием времени и автора изменений.', 1, 1, '2026-11-10T09:40:00Z'),
    (10, 'REQ-010', 'Требуется реализовать механизм эскалации для просроченных заявок с уведомлением руководства и переназначением.', 2, 2, '2026-11-11T12:05:00Z')
ON CONFLICT (request_id) DO NOTHING;

-- Insert RequestHistory entries
-- Request 1: Новая (initial only)
INSERT INTO RequestHistory (
    history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation
) VALUES
    (1, 1, 1, NULL, 1, '2026-11-02T09:00:00Z', 'Заявка зарегистрирована')
ON CONFLICT (history_id) DO NOTHING;

-- Request 2: Новая (initial only)
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (2, 2, 2, NULL, 1, '2026-11-03T10:15:00Z', 'Заявка зарегистрирована')
ON CONFLICT (history_id) DO NOTHING;

-- Request 3: Новая (initial only)
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (3, 3, 3, NULL, 1, '2026-11-04T11:30:00Z', 'Заявка зарегистрирована')
ON CONFLICT (history_id) DO NOTHING;

-- Request 4: Новая -> В работе
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (4, 4, 4, NULL, 1, '2026-11-05T08:30:00Z', 'Заявка зарегистрирована'),
    (5, 4, 2, 1, 2, '2026-11-05T09:15:00Z', 'Заявка принята в работу')
ON CONFLICT (history_id) DO NOTHING;

-- Request 5: Новая -> В работе
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (6, 5, 1, NULL, 1, '2026-11-06T09:45:00Z', 'Заявка зарегистрирована'),
    (7, 5, 3, 1, 2, '2026-11-06T10:30:00Z', 'Заявка передана исполнителю')
ON CONFLICT (history_id) DO NOTHING;

-- Request 6: Новая -> В работе
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (8, 6, 2, NULL, 1, '2026-11-07T10:00:00Z', 'Заявка зарегистрирована'),
    (9, 6, 1, 1, 2, '2026-11-07T10:45:00Z', 'Начато выполнение')
ON CONFLICT (history_id) DO NOTHING;

-- Request 7: Новая -> В работе -> На проверке
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (10, 7, 3, NULL, 1, '2026-11-08T11:15:00Z', 'Заявка зарегистрирована'),
    (11, 7, 2, 1, 2, '2026-11-08T12:00:00Z', 'Заявка в процессе выполнения'),
    (12, 7, 4, 2, 3, '2026-11-08T14:30:00Z', 'Результат отправлен на проверку')
ON CONFLICT (history_id) DO NOTHING;

-- Request 8: Новая -> В работе -> На проверке
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (13, 8, 4, NULL, 1, '2026-11-09T08:20:00Z', 'Заявка зарегистрирована'),
    (14, 8, 1, 1, 2, '2026-11-09T09:00:00Z', 'Работа начата'),
    (15, 8, 2, 2, 3, '2026-11-09T11:45:00Z', 'Результат готов к проверке')
ON CONFLICT (history_id) DO NOTHING;

-- Request 9: Новая -> В работе -> На проверке -> Одобрена
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (16, 9, 1, NULL, 1, '2026-11-10T09:40:00Z', 'Заявка зарегистрирована'),
    (17, 9, 3, 1, 2, '2026-11-10T10:30:00Z', 'Заявка в процессе'),
    (18, 9, 4, 2, 3, '2026-11-10T13:00:00Z', 'Результат направлен контролёру'),
    (19, 9, 2, 3, 4, '2026-11-10T14:15:00Z', 'Результат одобрен')
ON CONFLICT (history_id) DO NOTHING;

-- Request 10: Новая -> В работе -> На проверке -> Одобрена -> Завершена
INSERT INTO RequestHistory (history_id, request_id, actor_user_id, previous_status_id, new_status_id, occurred_at, explanation) VALUES
    (20, 10, 2, NULL, 1, '2026-11-11T12:05:00Z', 'Заявка зарегистрирована'),
    (21, 10, 1, 1, 2, '2026-11-11T13:00:00Z', 'Заявка выполняется'),
    (22, 10, 3, 2, 3, '2026-11-11T15:30:00Z', 'Результат на проверке'),
    (23, 10, 4, 3, 4, '2026-11-11T16:15:00Z', 'Результат принят'),
    (24, 10, 2, 4, 6, '2026-11-11T17:00:00Z', 'Заявка завершена')
ON CONFLICT (history_id) DO NOTHING;

COMMIT;
