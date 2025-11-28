; Script pour Inno Setup
; A compiler avec Inno Setup Compiler

[Setup]
; Nom de votre application
AppName=Smart Downloads Organizer
AppVersion=1.0
DefaultDirName={autopf}\SmartDownloadsOrganizer
DefaultGroupName=SmartDownloadsOrganizer
; Le dossier où sera créé le setup.exe (ici le dossier parent)
OutputDir=.
OutputBaseFilename=SmartOrganizer_Setup_v1
Compression=lzma
SolidCompression=yes
; Icône de l'installateur (optionnel, sinon supprimer la ligne)
; SetupIconFile=icon.ico 

[Languages]
Name: "french"; MessagesFile: "compiler:Languages\French.isl"

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; GroupDescription: "{cm:AdditionalIcons}"; Flags: unchecked

[Files]
; IMPORTANT : Vérifiez que le chemin vers votre .exe est correct ici
; On suppose que le .iss est dans le dossier src et l'exe dans src/dist
Source: "dist\SmartOrganizer.exe"; DestDir: "{app}"; Flags: ignoreversion

[Icons]
Name: "{group}\Smart Downloads Organizer"; Filename: "{app}\SmartOrganizer.exe"
Name: "{autodesktop}\Smart Downloads Organizer"; Filename: "{app}\SmartOrganizer.exe"; Tasks: desktopicon

[Run]
; C'est cette section qui permet de lancer l'app après l'installation
Filename: "{app}\SmartOrganizer.exe"; Description: "{cm:LaunchProgram,Smart Downloads Organizer}"; Flags: nowait postinstall skipifsilent