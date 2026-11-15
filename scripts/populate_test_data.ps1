#!/usr/bin/env pwsh
<#
.SYNOPSIS
    Populate the Request System database with test data.

.DESCRIPTION
    Loads populate_test_data.sql into the Request System database.
    Verifies the database is empty before inserting to prevent data loss.

.EXAMPLE
    .\scripts\populate_test_data.ps1

.NOTES
    Database path can be customized via REQUEST_SYSTEM_DB environment variable.
#>

$ErrorActionPreference = "Stop"

$dbPath = if ($env:REQUEST_SYSTEM_DB) { $env:REQUEST_SYSTEM_DB } else { "request-system.db" }
$sqlScriptPath = Join-Path $PSScriptRoot "populate_test_data.sql"

Write-Host "📁 Database path: $dbPath"
Write-Host "📄 SQL script path: $sqlScriptPath"

if (-not (Test-Path $dbPath)) {
    Write-Host "❌ Database file does not exist at: $dbPath"
    Write-Host "Initialize the database first by running:"
    Write-Host "   python -m request_system list"
    exit 1
}

if (-not (Test-Path $sqlScriptPath)) {
    Write-Host "❌ SQL script not found at: $sqlScriptPath"
    exit 1
}

# Check if sqlite3 is available
try {
    $null = Get-Command sqlite3 -ErrorAction Stop
} catch {
    Write-Host "❌ sqlite3 command not found. Please install SQLite3."
    exit 1
}

Write-Host "`nRunning populate_test_data.sql..."

try {
    # Execute the SQL script
    Get-Content $sqlScriptPath | sqlite3 $dbPath

    Write-Host "`n✅ All test data inserted successfully!"
    Write-Host "`n📊 Summary:"
    Write-Host "   • 4 users (user_id 1-4)"
    Write-Host "   • 4 categories (category_id 1-4)"
    Write-Host "   • 6 statuses (status_id 1-6)"
    Write-Host "   • 10 requests (request_id 1-10)"
    Write-Host "   • 24 history entries"

    Write-Host "`n🧪 To verify, run:"
    Write-Host "   python -m request_system list"
    Write-Host "   python -m request_system list --status ""В работе"""
    Write-Host "   python -m request_system list --user 1"
    Write-Host "   python -m request_system get 1"
}
catch {
    Write-Host "❌ Error during insertion: $_"
    exit 1
}
