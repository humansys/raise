; scripts/rai-installer.iss — RAISE-15631
;
; GUI wizard installer for rai + rai-mcp-pipeline (Windows). Installs both
; binaries in one step, registers both in the user PATH, and registers a
; standard uninstall entry ("Add or remove programs") that removes both
; binaries and the PATH entries with no residue.
;
; NOT compiled/tested in this environment — ISCC (Inno Setup Compiler) is
; Windows-only and there is no Wine here. This file follows standard Inno
; Setup syntax and mirrors the install/uninstall logic already verified in
; scripts/install.ps1 (same atomic-pair intent, same PATH registration
; target). Pending: compile with ISCC and run the generated installer on a
; real Windows machine before story/epic close (RAISE-15631 plan.md risk).
;
; Expects the onedir builds already extracted (from the Task 1 release
; archives, or a local build via scripts/build-binary-local.ps1) at:
;   {#SourceDir}\rai\rai.exe (+ _internal\...)
;   {#SourceDir}\rai-mcp-pipeline\rai-mcp-pipeline.exe (+ _internal\...)
;
; Compile:
;   ISCC rai-installer.iss
;   ISCC /DSourceDir=C:\path\to\extracted /DAppVersion=3.1.0 rai-installer.iss

#ifndef SourceDir
  #define SourceDir "build"
#endif
#ifndef AppVersion
  #define AppVersion "0.0.0"
#endif

[Setup]
AppId={{76B3675D-7C31-4F3B-A6D9-511CEAFF2603}
AppName=RaiSE (rai)
AppVersion={#AppVersion}
AppPublisher=RaiSE
DefaultDirName={autopf}\rai
DefaultGroupName=RaiSE
DisableProgramGroupPage=yes
OutputBaseFilename=rai-installer-windows-x86_64
Compression=lzma2
SolidCompression=yes
ArchitecturesAllowed=x64
ArchitecturesInstallIn64BitMode=x64
UninstallDisplayIcon={app}\rai\rai.exe
PrivilegesRequired=lowest

[Files]
Source: "{#SourceDir}\rai\*"; DestDir: "{app}\rai"; Flags: recursesubdirs createallsubdirs
Source: "{#SourceDir}\rai-mcp-pipeline\*"; DestDir: "{app}\rai-mcp-pipeline"; Flags: recursesubdirs createallsubdirs

[Registry]
; Append both binary dirs to the user PATH — never overwrite the existing
; value. {olddata} + Check:NeedsAddPath is the standard Inno Setup idiom for
; PATH entries (jrsoftware Path.iss example); each entry re-reads the
; on-disk value, so the second append sees the first entry's result.
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
  ValueData: "{olddata};{app}\rai"; Flags: preservestringtype; \
  Check: NeedsAddPath('{app}\rai')
Root: HKCU; Subkey: "Environment"; ValueType: expandsz; ValueName: "Path"; \
  ValueData: "{olddata};{app}\rai-mcp-pipeline"; Flags: preservestringtype; \
  Check: NeedsAddPath('{app}\rai-mcp-pipeline')

[UninstallDelete]
Type: filesandordirs; Name: "{app}\rai"
Type: filesandordirs; Name: "{app}\rai-mcp-pipeline"

[Code]
function NeedsAddPath(Param: string): boolean;
var
  OrigPath: string;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', OrigPath) then
  begin
    Result := True;
    exit;
  end;
  Result := Pos(';' + UpperCase(Param) + ';', ';' + UpperCase(OrigPath) + ';') = 0;
end;

procedure RemoveFromPath(Dir: string);
var
  Paths: string;
  P: Integer;
begin
  if not RegQueryStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Paths) then
    exit;
  Paths := ';' + Paths + ';';
  P := Pos(';' + Dir + ';', Paths);
  if P = 0 then
    exit;
  Delete(Paths, P, Length(Dir) + 1);
  Paths := Copy(Paths, 2, Length(Paths) - 2);
  RegWriteStringValue(HKEY_CURRENT_USER, 'Environment', 'Path', Paths);
end;

procedure CurUninstallStepChanged(CurUninstallStep: TUninstallStep);
begin
  if CurUninstallStep = usPostUninstall then
  begin
    RemoveFromPath(ExpandConstant('{app}\rai'));
    RemoveFromPath(ExpandConstant('{app}\rai-mcp-pipeline'));
  end;
end;

procedure CurStepChanged(CurStep: TSetupStep);
var
  OldShim: string;
begin
  // Pre-binary installs (docs/install.ps1) left a rai.cmd shim here that
  // resolves to .venv\Scripts\rai.exe in the current directory. Left in
  // place, it shadows the binaries this installer registers (RAISE-15801).
  if CurStep = ssInstall then
  begin
    OldShim := ExpandConstant('{%USERPROFILE}\.local\bin\rai.cmd');
    if FileExists(OldShim) then
      DeleteFile(OldShim);
  end;
end;
