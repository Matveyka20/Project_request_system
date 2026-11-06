-- Demonstration DML for docs/sql/schema.sql and docs/sql/seed.sql.
-- Run against the dedicated test database only. All changes are rolled back.
PRAGMA foreign_keys = ON;
BEGIN IMMEDIATE;

-- INSERT: synthetic users, role links, request, status history, assignment,
-- comments, result submission and acceptance decision.
INSERT INTO Users (user_id, account, name, contacts) VALUES
    (9901, 'crud-demo-applicant', 'Тестовый заявитель', 'applicant@example.test'),
    (9902, 'crud-demo-executor', 'Тестовый исполнитель', 'executor@example.test');

INSERT INTO UserRoles (user_id, role_id) VALUES
    (9901, 1),
    (9902, 3);

INSERT INTO Requests (
    request_id, request_number, description, applicant_user_id,
    category_id, priority, registered_at
) VALUES (
    9901, 'CRUD-DEMO-9901', 'Демонстрационная заявка для CRUD-примеров',
    9901, 1, 'Обычный', '2026-11-06T15:00:00Z'
);

INSERT INTO RequestHistory (
    history_id, request_id, actor_user_id, previous_status_id,
    new_status_id, occurred_at, explanation
) VALUES
    (9901, 9901, 9901, NULL, 1, '2026-11-06T15:00:00Z', 'Начальная регистрация'),
    (9902, 9901, 2, 1, 2, '2026-11-06T15:15:00Z', 'Заявка передана в работу');

INSERT INTO Assignments (
    assignment_id, request_id, assignee_user_id, assigned_by_user_id,
    assigned_at, ended_at, reassignment_reason
) VALUES
    (9901, 9901, 3, 2, '2026-11-06T15:10:00Z', '2026-11-06T15:20:00Z', 'Демонстрация переназначения'),
    (9902, 9901, 9902, 2, '2026-11-06T15:20:00Z', NULL, NULL);

INSERT INTO Comments (
    comment_id, request_id, author_user_id, text, is_service, created_at
) VALUES
    (9901, 9901, 9901, 'Уточнение к демонстрационной заявке.', 0, '2026-11-06T15:05:00Z'),
    (9902, 9901, 9902, 'Заявка принята в работу.', 0, '2026-11-06T15:25:00Z');

INSERT INTO ResultSubmissions (
    result_submission_id, request_id, executor_user_id, description, submitted_at
) VALUES (
    9901, 9901, 9902, 'Демонстрационный результат выполнения.', '2026-11-06T16:00:00Z'
);

INSERT INTO AcceptanceDecisions (
    decision_id, result_submission_id, controller_user_id,
    outcome, comment, decided_at
) VALUES (
    9901, 9901, 5, 'accepted', 'Демонстрационный результат принят.', '2026-11-06T16:15:00Z'
);

-- SELECT: request with derived current status.
SELECT
    r.request_number,
    r.description,
    s.name AS current_status,
    r.priority
FROM Requests AS r
JOIN RequestHistory AS h
    ON h.history_id = (
        SELECT h2.history_id
        FROM RequestHistory AS h2
        WHERE h2.request_id = r.request_id
        ORDER BY h2.occurred_at DESC, h2.history_id DESC
        LIMIT 1
    )
JOIN Statuses AS s ON s.status_id = h.new_status_id
WHERE r.request_id = 9901;

-- SELECT: users and their roles.
SELECT u.name, ro.name AS role
FROM UserRoles AS ur
JOIN Users AS u ON u.user_id = ur.user_id
JOIN Roles AS ro ON ro.role_id = ur.role_id
WHERE u.user_id IN (9901, 9902)
ORDER BY u.user_id;

-- SELECT: assignment history, including who assigned whom.
SELECT
    a.assignment_id,
    executor.name AS executor,
    assigner.name AS assigned_by,
    a.assigned_at,
    a.ended_at,
    a.reassignment_reason
FROM Assignments AS a
JOIN Users AS executor ON executor.user_id = a.assignee_user_id
JOIN Users AS assigner ON assigner.user_id = a.assigned_by_user_id
WHERE a.request_id = 9901
ORDER BY a.assigned_at;

-- SELECT: comments with their authors.
SELECT c.created_at, u.name AS author, c.text
FROM Comments AS c
JOIN Users AS u ON u.user_id = c.author_user_id
WHERE c.request_id = 9901
ORDER BY c.created_at;

-- SELECT: result and its acceptance decision.
SELECT rs.description, d.outcome, d.comment, controller.name AS controller
FROM ResultSubmissions AS rs
JOIN AcceptanceDecisions AS d
    ON d.result_submission_id = rs.result_submission_id
JOIN Users AS controller ON controller.user_id = d.controller_user_id
WHERE rs.request_id = 9901;

-- SELECT: aggregate the request's status-event and comment counts.
SELECT
    r.request_number,
    (SELECT count(*) FROM RequestHistory WHERE request_id = r.request_id) AS status_events,
    (SELECT count(*) FROM Comments WHERE request_id = r.request_id) AS comments
FROM Requests AS r
WHERE r.request_id = 9901;

-- UPDATE: revise only this fixture's comment.
UPDATE Comments
SET text = 'Уточнение сохранено (демонстрация UPDATE).'
WHERE comment_id = 9901
  AND request_id = 9901
  AND author_user_id = 9901;

-- UPDATE: close only this fixture's active assignment.
UPDATE Assignments
SET ended_at = '2026-11-06T16:20:00Z'
WHERE assignment_id = 9902
  AND request_id = 9901
  AND assignee_user_id = 9902
  AND ended_at IS NULL;

-- DELETE in child-first order; only rows inserted by this fixture.
DELETE FROM AcceptanceDecisions
WHERE decision_id = 9901
  AND result_submission_id = 9901;

DELETE FROM Comments
WHERE comment_id = 9902
  AND request_id = 9901;

ROLLBACK;
