-- Synthetic Russian-language fixture data for a dedicated test database only.
-- Safe to rerun: fixed primary keys use ON CONFLICT DO NOTHING; no existing
-- rows are updated or deleted. Initialize the test database with schema.sql.

PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

INSERT INTO Roles (role_id, name) VALUES
    (1, 'Заявитель'),
    (2, 'Оператор'),
    (3, 'Исполнитель'),
    (4, 'Контролёр результата')
ON CONFLICT (role_id) DO NOTHING;

INSERT INTO Users (user_id, account, name, contacts) VALUES
    (1, 'demo-applicant', 'Анна Заявкина', 'anna@example.test'),
    (2, 'demo-operator', 'Борис Диспетчеров', 'boris@example.test'),
    (3, 'demo-executor-a', 'Вера Исполнитель', 'vera@example.test'),
    (4, 'demo-executor-b', 'Глеб Мастер', 'gleb@example.test'),
    (5, 'demo-controller', 'Дарья Проверкина', 'darya@example.test'),
    (6, 'demo-applicant-two', 'Егор Клиентов', NULL)
ON CONFLICT (user_id) DO NOTHING;

INSERT INTO UserRoles (user_id, role_id) VALUES
    (1, 1),
    (2, 2),
    (3, 3),
    (4, 3),
    (5, 4),
    (6, 1)
ON CONFLICT (user_id, role_id) DO NOTHING;

INSERT INTO Statuses (status_id, name) VALUES
    (1, 'Новая'),
    (2, 'В работе'),
    (3, 'На проверке'),
    (4, 'На доработке'),
    (5, 'Закрыта'),
    (6, 'Ожидает уточнения')
ON CONFLICT (status_id) DO NOTHING;

INSERT INTO Categories (category_id, name) VALUES
    (1, 'Информационные технологии'),
    (2, 'Административная помощь'),
    (3, 'Оборудование'),
    (4, 'Сетевой доступ')
ON CONFLICT (category_id) DO NOTHING;

INSERT INTO Requests (
    request_id, request_number, description, applicant_user_id,
    category_id, priority, registered_at
) VALUES
    (1, 'DEMO-1001', 'Настроить доступ к учебному порталу', 1, 1, 'Высокий', '2026-10-12T09:00:00Z'),
    (2, 'DEMO-1002', 'Подготовить проектор для аудитории', 6, 2, 'Обычный', '2026-10-13T10:15:00Z'),
    (3, 'DEMO-1003', 'Уточнить параметры рабочего места', 1, NULL, NULL, '2026-10-14T11:30:00Z'),
    (4, 'DEMO-1004', 'Проверить подключение сетевого принтера', 6, 4, 'Обычный', '2026-10-15T08:30:00Z'),
    (5, 'DEMO-1005', 'Заменить неисправную клавиатуру', 1, 3, 'Низкий', '2026-10-15T09:45:00Z'),
    (6, 'DEMO-1006', 'Установить обновление офисного пакета', 6, 1, 'Обычный', '2026-10-16T10:00:00Z'),
    (7, 'DEMO-1007', 'Восстановить доступ к общей папке курса', 1, 4, 'Высокий', '2026-10-16T11:15:00Z'),
    (8, 'DEMO-1008', 'Подготовить рабочее место в лаборатории', 6, 2, 'Низкий', '2026-10-17T08:20:00Z'),
    (9, 'DEMO-1009', 'Настроить программное обеспечение для занятия', 1, 1, 'Обычный', '2026-10-17T09:40:00Z'),
    (10, 'DEMO-1010', 'Проверить нестабильное подключение Wi-Fi', 6, 4, 'Высокий', '2026-10-18T12:05:00Z')
ON CONFLICT (request_id) DO NOTHING;

INSERT INTO RequestHistory (
    history_id, request_id, actor_user_id, previous_status_id,
    new_status_id, occurred_at, explanation
) VALUES
    (1, 1, 1, NULL, 1, '2026-10-12T09:00:00Z', 'Заявка зарегистрирована'),
    (2, 1, 2, 1, 2, '2026-10-12T09:20:00Z', 'Передана исполнителю'),
    (3, 1, 2, 2, 3, '2026-10-12T13:00:00Z', 'Результат направлен на проверку'),
    (4, 1, 5, 3, 5, '2026-10-12T14:00:00Z', 'Результат принят'),
    (5, 2, 6, NULL, 1, '2026-10-13T10:15:00Z', 'Заявка зарегистрирована'),
    (6, 2, 2, 1, 2, '2026-10-13T10:40:00Z', 'Начато выполнение'),
    (7, 2, 3, 2, 3, '2026-10-13T12:10:00Z', 'Результат ожидает проверки'),
    (8, 2, 5, 3, 4, '2026-10-13T12:45:00Z', 'Нужно проверить подключение кабеля'),
    (9, 2, 3, 4, 2, '2026-10-13T13:10:00Z', 'Исполнитель устраняет замечание'),
    (10, 3, 1, NULL, 6, '2026-10-14T11:30:00Z', 'Запрошены сведения о помещении'),
    (11, 4, 6, NULL, 1, '2026-10-15T08:30:00Z', 'Заявка зарегистрирована'),
    (12, 5, 1, NULL, 1, '2026-10-15T09:45:00Z', 'Заявка зарегистрирована'),
    (13, 6, 6, NULL, 1, '2026-10-16T10:00:00Z', 'Заявка зарегистрирована'),
    (14, 7, 1, NULL, 1, '2026-10-16T11:15:00Z', 'Заявка зарегистрирована'),
    (15, 8, 6, NULL, 1, '2026-10-17T08:20:00Z', 'Заявка зарегистрирована'),
    (16, 9, 1, NULL, 1, '2026-10-17T09:40:00Z', 'Заявка зарегистрирована'),
    (17, 10, 6, NULL, 1, '2026-10-18T12:05:00Z', 'Заявка зарегистрирована')
ON CONFLICT (history_id) DO NOTHING;

INSERT INTO Assignments (
    assignment_id, request_id, assignee_user_id, assigned_by_user_id,
    assigned_at, ended_at, reassignment_reason
) VALUES
    (1, 1, 3, 2, '2026-10-12T09:20:00Z', '2026-10-12T10:00:00Z', 'Перераспределение нагрузки'),
    (2, 1, 4, 2, '2026-10-12T10:00:00Z', '2026-10-12T13:00:00Z', NULL),
    (3, 2, 3, 2, '2026-10-13T10:40:00Z', NULL, NULL)
ON CONFLICT (assignment_id) DO NOTHING;

INSERT INTO Comments (
    comment_id, request_id, author_user_id, text, is_service, created_at
) VALUES
    (1, 1, 2, 'Проверьте, пожалуйста, имя учётной записи.', 0, '2026-10-12T09:10:00Z'),
    (2, 1, 1, 'Учётная запись: anna-demo.', 0, '2026-10-12T09:15:00Z'),
    (3, 2, 2, 'В заявке указана аудитория 204.', 1, '2026-10-13T10:35:00Z'),
    (4, 2, 5, 'При повторной проверке убедитесь в передаче изображения.', 1, '2026-10-13T12:45:00Z'),
    (5, 3, 2, 'Укажите номер аудитории и нужное программное обеспечение.', 0, '2026-10-14T11:35:00Z')
ON CONFLICT (comment_id) DO NOTHING;

INSERT INTO Attachments (
    attachment_id, request_id, uploaded_by_user_id, reference
) VALUES
    (1, 1, 1, 'demo://attachments/DEMO-1001-access-note.txt'),
    (2, 2, 6, 'demo://attachments/DEMO-1002-room-photo.jpg')
ON CONFLICT (attachment_id) DO NOTHING;

INSERT INTO ResultSubmissions (
    result_submission_id, request_id, executor_user_id, description, submitted_at
) VALUES
    (1, 1, 4, 'Доступ к порталу проверен в тестовой учётной записи.', '2026-10-12T13:00:00Z'),
    (2, 2, 3, 'Проектор включён, изображение выведено на экран.', '2026-10-13T12:10:00Z')
ON CONFLICT (result_submission_id) DO NOTHING;

INSERT INTO AcceptanceDecisions (
    decision_id, result_submission_id, controller_user_id,
    outcome, comment, decided_at
) VALUES
    (1, 1, 5, 'accepted', 'Результат соответствует запросу.', '2026-10-12T14:00:00Z'),
    (2, 2, 5, 'rework', 'Не подтверждена передача звука.', '2026-10-13T12:45:00Z')
ON CONFLICT (decision_id) DO NOTHING;

COMMIT;
