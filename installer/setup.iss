#define MyAppName "P2P Flash Raid"
#define MyAppVersion "0.1.0"
#define MyAppPublisher "Anton"

[Setup]
AppId={{PUT-A-GUID-HERE}}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputDir=..\dist\installer
OutputBaseFilename=P2PBackupSetup
Compression=lzma
SolidCompression=yes
PrivilegesRequired=admin

[Files]
Source: "..\dist\gui\P2PBackupGUI.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "..\dist\daemon\P2PBackupDaemon.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\P2PBackupGUI.exe"
Name: "{group}\Uninstall {#MyAppName}"; Filename: "{uninstallexe}"

[Tasks]
Name: "autostart"; Description: "Запускать демон восстановления при входе в систему"; GroupDescription: "Дополнительно:"

[Run]
Filename: "powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -NoProfile -Command ""Register-ScheduledTask -TaskName 'P2PBackupDaemon' -Action (New-ScheduledTaskAction -Execute '{app}\P2PBackupDaemon.exe') -Trigger (New-ScheduledTaskTrigger -AtLogOn) -RestartCount 3 -RestartInterval (New-TimeSpan -Minutes 1) -Force"""; \
    Tasks: autostart; \
    Flags: runhidden

[UninstallRun]
Filename: "powershell.exe"; \
    Parameters: "-ExecutionPolicy Bypass -NoProfile -Command ""Unregister-ScheduledTask -TaskName 'P2PBackupDaemon' -Confirm:$false"""; \
    Flags: runhidden