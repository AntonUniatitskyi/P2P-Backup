$ErrorActionPreference = "Stop"

$projectRoot = Split-Path -Parent $PSScriptRoot
$pythonw = Join-Path $projectRoot "venv\Scripts\pythonw.exe"
$daemonArgs = "-m app.entrypoints_daemon"

$action = New-ScheduledTaskAction `
    -Execute $pythonw `
    -Argument $daemonArgs `
    -WorkingDirectory (Join-Path $projectRoot "manager-python")

$trigger = New-ScheduledTaskTrigger -AtLogOn

$settings = New-ScheduledTaskSettingsSet `
    -RestartCount 3 `
    -RestartInterval (New-TimeSpan -Minutes 1) `
    -ExecutionTimeLimit (New-TimeSpan -Days 0) `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries

Register-ScheduledTask `
    -TaskName "P2PBackupDaemon" `
    -Action $action `
    -Trigger $trigger `
    -Settings $settings `
    -Description "Фоновый демон восстановления P2P-бэкапов" `
    -Force

Write-Host "Задача 'P2PBackupDaemon' зарегистрирована. Запустится при следующем входе в систему."
Write-Host "Запустить сейчас: Start-ScheduledTask -TaskName 'P2PBackupDaemon'"