; Script generated by the Inno Setup Script Wizard.
; SEE THE DOCUMENTATION FOR DETAILS ON CREATING INNO SETUP SCRIPT FILES!
 
#define MyAppName "ESO Packet Tracker"
#define MyAppVersion "25.07.19"
#define MyAppPublisher "XaKO"
#define MyAppExeName "ESO Tracker.exe"


[Setup]
; NOTE: The value of AppId uniquely identifies this application.
; Do not use the same AppId value in installers for other applications.
; (To generate a new GUID, click Tools | Generate GUID inside the IDE.)
AppId={{BE5FCEDA-3AE1-4A57-8C9D-D4C7713FA7F1}

AppName={#MyAppName}
AppVersion={#MyAppVersion}
AppVerName={#MyAppName} {#MyAppVersion}
AppPublisher={#MyAppPublisher}
AppCopyright={#MyAppPublisher}
VersionInfoVersion={#MyAppVersion}
DefaultDirName={pf}\{#MyAppName}
DefaultGroupName={#MyAppName}
OutputBaseFilename=[setup]ESO Tracker
SetupIconFile=icon.ico
UninstallDisplayIcon=icon.ico
Compression=lzma2/ultra
SolidCompression=yes

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Tasks]
Name: "desktopicon1"; Description: "ESO Packet Tracker"; GroupDescription: "Create desktop shortcuts:"; Flags: checkablealone

[Files]
;EXEs
Source: "dist\ESO Tracker.exe"; DestDir: "{app}"; Flags: ignoreversion
Source: "WinPcap_4_1_3.exe"; DestDir: "{tmp}"
Source: "Data\*"; DestDir: "{app}\Data"; Flags: ignoreversion
Source: "Maps\*"; DestDir: "{app}\Maps"; Flags: ignoreversion
Source: "Cards\*"; DestDir: "{app}\Cards"; Flags: ignoreversion

; NOTE: Don't use "Flags: ignoreversion" on any shared system files

[Icons]
Name: "{group}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"
Name: "{commondesktop}\{#MyAppName}"; Filename: "{app}\{#MyAppExeName}"; Tasks: desktopicon1

[Run]
Filename: "{tmp}\WinPcap_4_1_3.exe"; Flags: runascurrentuser;  Check: NeedInstallWinPcap
Filename: "{app}\{#MyAppExeName}"; Description: "{cm:LaunchProgram,{#StringChange(MyAppName, '&', '&&')}}"; Flags: nowait postinstall skipifsilent runascurrentuser


[Code]
#IFDEF UNICODE
  #DEFINE AW "W"
#ELSE
  #DEFINE AW "A"
#ENDIF
var 
  StaticText: TNewStaticText; 
  RadioButton_1, RadioButton_2: TRadioButton; 
  Uninstall, Location: string; 
  ResultCode: Integer; 

type
  INSTALLSTATE = Longint;


function NeedInstallWinPcap: Boolean;
var
  bSuccess: Boolean;
  regVersion: string;
begin
  Result := True;
  bSuccess := RegQueryStringValue(HKLM, 'Software\Microsoft\Windows\CurrentVersion\Uninstall\WinPcapInst', 'DisplayName', regVersion);
  if bSuccess then 
    Result := False;
end;



///��������� NextButtonClick ��� ����� ��������. 
function Page_NextButtonClick(Page: TWizardPage): Boolean; 
begin 
  if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{BE5FCEDA-3AE1-4A57-8C9D-D4C7713FA7F1}_is1','UninstallString', Uninstall) then
    Uninstall := RemoveQuotes(Uninstall); 
  if RadioButton_1.Checked then 
  begin 
    if not Exec(Uninstall, ' /SILENT', '', SW_SHOW, ewWaitUntilTerminated, ResultCode) then 
      MsgBox('Uninstalling Error. ' #13#13 '' + SysErrorMessage(ResultCode) + '.' #13#13 'Possibly, the uninstaller has been moved, removed or renamed.', mbError, MB_OK); 
    Result := True; 
  end 
  else 
  begin 
    if not RadioButton_1.Checked then 
    Result := True; 
  end; 
end; 

///��������� CancelButtonClick ��� ����� ��������. 
procedure Page_CancelButtonClick(Page: TWizardPage; var Cancel, Confirm: Boolean); 
begin 
  Confirm := False; 
  Cancel  := True; 
end; 

///��� ��������� ������� ����� �������� � ��� ��� �� ��� ���������
function CheckInstalledPage(PreviousPageId: Integer): Integer; 
var 
  Page: TWizardPage; 
begin 
  RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{BE5FCEDA-3AE1-4A57-8C9D-D4C7713FA7F1}_is1', 'InstallLocation', Location);
  
  Page := CreateCustomPage(PreviousPageId, 'Previous Installation Found', 'Please choose how you want to proceed.'); 
///����� �� �������� 
  StaticText := TNewStaticText.Create(Page); 
  StaticText.Parent := Page.Surface; 
  StaticText.Caption := 'ESO Tracker is already installed in "' + Location +'"'+#13+ 'It is recommended that you uninstall the current version before continuing.';
  StaticText.Left := 0; 
  StaticText.Top := ScaleY(24); 
  StaticText.TabOrder := 0; 
  StaticText.AutoSize := True; 
  ///������ RadioButton 
  RadioButton_1 := TRadioButton.Create(Page); 
  RadioButton_1.Parent := Page.Surface; 
  RadioButton_1.Caption := 'Uninstall before continuing (recommended)'; 
  RadioButton_1.Left := 0; 
  RadioButton_1.Top := ScaleY(104); 
  RadioButton_1.Width := ScaleX(233); 
  RadioButton_1.Height := ScaleY(17); 
  RadioButton_1.Checked := True; 
  RadioButton_1.TabOrder := 1; 
  RadioButton_1.TabStop := True; 
  ///������ RadioButton 
  RadioButton_2 := TRadioButton.Create(Page); 
  RadioButton_2.Parent := Page.Surface; 
  RadioButton_2.Caption := 'Overwrite current version'; 
  RadioButton_2.Left := 0; 
  RadioButton_2.Top := ScaleY(144); 
  RadioButton_2.Width := ScaleX(153); 
  RadioButton_2.Height := ScaleY(17); 
  RadioButton_2.TabOrder := 2; 

  Page.OnNextButtonClick := @Page_NextButtonClick; 
  Page.OnCancelButtonClick := @Page_CancelButtonClick; 

  Result := Page.ID; 
end; 

procedure InitializeWizard(); 
begin 
  if RegQueryStringValue(HKLM, 'SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall\{BE5FCEDA-3AE1-4A57-8C9D-D4C7713FA7F1}_is1', 'UninstallString', Uninstall) then
    CheckInstalledPage(wpLicense); 
end;
