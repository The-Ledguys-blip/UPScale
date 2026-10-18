; Inno Setup 6 installer script voor UPScale (Windows 11).
; Bouwen: ISCC.exe installer.iss
; Of via: py build_app_windows.py installer

#define MyAppName "UPScale"
#ifndef MyAppVersion
  #define MyAppVersion "2.2.0"
#endif
#define MyAppPublisher "UPScale"
#define MyAppExeName "UPScale.exe"

[Setup]
AppId={{7F3C1E5A-9B2D-4C6E-8A1F-2D4E6B8C0A31}
AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppPublisher={#MyAppPublisher}
DefaultDirName={autopf}\{#MyAppName}
DefaultGroupName={#MyAppName}
UninstallDisplayIcon={app}\{#MyAppExeName}
OutputDir=installer_output
OutputBaseFilename={#MyAppName}-Setup-{#MyAppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
ArchitecturesInstallIn64BitMode=x64compatible
ArchitecturesAllowed=x64compatible
PrivilegesRequired=admin
DisableProgramGroupPage=yes
; Geen sign; Windows SmartScreen kan waarschuwen bij onbekende uitgever.
SignTool= 
SignedUninstaller=no

[Languages]
Name: "dutch"; MessagesFile: "compiler:Languages\Dutch.isl"
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; PyInstaller onedir output staat in dist\UPScale\
Source: "dist\UPScale\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{autodesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon

[Run]
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#MyAppName}}"; Flags: nowait postinstall skipifsilent
