#define MyAppName "Prompt Master Standalone"
#define MyAppVersion "1.0.0"
[Setup]
AppId={{B491C935-B563-42BB-AD3F-A6B8A5938F93}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
DefaultDirName={localappdata}\PromptMasterStandalone
PrivilegesRequired=lowest
OutputBaseFilename=PromptMasterSetup
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
UninstallDisplayName={#MyAppName}
[Tasks]
Name: "desktopicon"; Description: "Create a desktop shortcut"; Flags: unchecked
[Files]
Source: "..\dist\PromptMaster\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs
[Icons]
Name: "{group}\Prompt Master Standalone"; Filename: "{app}\PromptMaster.exe"
Name: "{autodesktop}\Prompt Master Standalone"; Filename: "{app}\PromptMaster.exe"; Tasks: desktopicon
[Run]
Filename: "{app}\PromptMaster.exe"; Parameters: "--setup"; Description: "Configure models and hardware"; Flags: nowait postinstall
