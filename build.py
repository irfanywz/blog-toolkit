import PyInstaller.__main__
import os
import subprocess

APP_NAME = "Blog Toolkit"
SCRIPT_FILE = "main.py" 
ICON_FILE = "logo.ico"

def build():
    # 1. Proses PyInstaller
    add_data_path = f"{ICON_FILE};." 

    params = [
        SCRIPT_FILE,
        f'--name={APP_NAME}',
        '--noconsole',
        '--clean',
        '--contents-directory', f'{APP_NAME}_System',
        f'--add-data={add_data_path}',
        '--collect-all=tkinterdnd2',
        '--collect-all=customtkinter',
        '--collect-all=pillow_avif',
        '--hidden-import=pystray._win32',
    ]

    if os.path.exists(ICON_FILE):
        params.append(f'--icon={ICON_FILE}')

    print("🚀 Sedang memproses PyInstaller...")
    PyInstaller.__main__.run(params)

    # 2. Buat file script Inno Setup secara otomatis (.iss)
    iss_content = f"""
#define MyAppName "{APP_NAME}"
#define MyAppVersion "1.0"
#define MyAppPublisher "Irfan"
#define MyAppExeName "{APP_NAME}.exe"

[Setup]
AppId={{{{8E3A1C2B-4F5D-6E7A-8B9C-0D1E2F3A4B5C}}}}
AppName={{#MyAppName}}
AppVersion={{#MyAppVersion}}
AppPublisher={{#MyAppPublisher}}
DefaultDirName={{autopf}}\\{{#MyAppName}}
DisableProgramGroupPage=yes
OutputDir=.
OutputBaseFilename={{#MyAppName}}_Setup
SetupIconFile={ICON_FILE}
Compression=lzma
SolidCompression=yes
WizardStyle=modern

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"

[Files]
Source: "dist\\{{#MyAppName}}\\*"; DestDir: "{{app}}"; Flags: ignoreversion recursesubdirs createallsubdirs

[Icons]
Name: "{{autodesktop}}\\{{#MyAppName}}"; Filename: "{{app}}\\{{#MyAppExeName}}"; Tasks: desktopicon

[Tasks]
Name: "desktopicon"; Description: "{{cm:CreateDesktopIcon}}"; GroupDescription: "{{cm:AdditionalIcons}}"; Flags: unchecked

[Run]
Filename: "{{app}}\\{{#MyAppExeName}}"; Description: "{{cm:LaunchProgram,{{#StringChange(MyAppName, '&', '&&')}}}}"; Flags: nowait postinstall skipifsilent
"""

    iss_path = "installer.iss"
    with open(iss_path, "w") as f:
        f.write(iss_content)

    # 3. Cari lokasi compiler Inno Setup (ISCC.exe) secara otomatis di Windows
    inno_compiler = r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
    if not os.path.exists(inno_compiler):
        inno_compiler = r"C:\Program Files\Inno Setup 6\ISCC.exe"

    if os.path.exists(inno_compiler):
        print("📦 Sedang mengompilasi installer .exe dengan Inno Setup...")
        subprocess.run([inno_compiler, iss_path])
        print("✨ Selesai! File installer siap di folder utama.")
    else:
        print("⚠️ Inno Setup Compiler (ISCC.exe) tidak ditemukan, pastikan Inno Setup sudah terinstal.")

if __name__ == "__main__":
    build()