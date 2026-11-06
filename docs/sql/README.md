# SQLite schema

`schema.sql` creates the normalized tables for a new SQLite database. It includes the request, lookup, role-membership, history, assignment, comment, attachment, result-submission, and acceptance-decision records. Category and priority may be unset until classification; foreign-key enforcement is enabled by the script.

From the repository root, create a database with the SQLite CLI:

```powershell
Get-Content docs/sql/schema.sql | sqlite3 request-system.db
```

When creating a request, the application must insert the `Requests` row and its initial `RequestHistory` status event in the same transaction. The current status is the latest event's `new_status_id`, ordered by `occurred_at` and then `history_id`; no separate current-status value is stored on the request.

## Synthetic test data

`seed.sql` contains fictional Russian-language records for demonstration and tests. Its fixed IDs and `ON CONFLICT ... DO NOTHING` make it safe to rerun without updating existing rows, but use a dedicated test database only; never seed a production or personal database. Create the test database and load the fixture from the repository root:

```powershell
Get-Content docs/sql/schema.sql | sqlite3 request-system-test.db
Get-Content docs/sql/seed.sql | sqlite3 request-system-test.db
```

## CRUD examples

`crud-examples.sql` demonstrates inserts, at least three `SELECT ... WHERE` filters, multiple joined `SELECT` queries, an aggregate, constrained updates, and child-first deletes. It uses reserved demo IDs, runs in a transaction, and ends with `ROLLBACK`, so the test database is unchanged. Execute it only against the dedicated test database:

```powershell
@('.bail on'; '.read docs/sql/crud-examples.sql') | sqlite3 request-system-test.db
```
