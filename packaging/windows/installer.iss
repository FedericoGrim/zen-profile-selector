; Inno Setup script for the Windows installer; build it with packaging\windows\build.ps1.
; Installs per user (no administrator rights), like most desktop apps distributed outside a store.

#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{6F1C2A57-3E8B-4C1D-9A2F-5B7E0D4C8A31}
AppName=Zen Profile Selector
AppVersion={#AppVersion}
AppPublisher=Federico Grimaldi
AppPublisherURL=https://github.com/FedericoGrim/zen-profile-selector
AppSupportURL=https://github.com/FedericoGrim/zen-profile-selector/issues
AppUpdatesURL=https://github.com/FedericoGrim/zen-profile-selector/releases
DefaultDirName={localappdata}\Programs\Zen Profile Selector
DefaultGroupName=Zen Profile Selector
DisableProgramGroupPage=yes
PrivilegesRequired=lowest
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
SetupIconFile=..\..\src\zen_profile_selector\assets\icon.ico
UninstallDisplayIcon={app}\zen-profile-selector.exe
UninstallDisplayName=Zen Profile Selector
OutputDir=..\..\dist
OutputBaseFilename=zen-profile-selector-setup-{#AppVersion}
Compression=lzma2
SolidCompression=yes
WizardStyle=modern
CloseApplications=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "italian"; MessagesFile: "compiler:Languages\Italian.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
Source: "..\..\build\pyinstaller\dist\zen-profile-selector\*"; DestDir: "{app}"; Flags: ignoreversion recursesubdirs createallsubdirs

[InstallDelete]
; Files of the previous version are replaced as a whole
Type: filesandordirs; Name: "{app}\_internal"

[Icons]
Name: "{userprograms}\Zen Profile Selector"; Filename: "{app}\zen-profile-selector.exe"
Name: "{userdesktop}\Zen Profile Selector"; Filename: "{app}\zen-profile-selector.exe"; Tasks: desktopicon

[Run]
Filename: "{app}\zen-profile-selector.exe"; Description: "{cm:LaunchProgram,Zen Profile Selector}"; Flags: nowait postinstall skipifsilent
