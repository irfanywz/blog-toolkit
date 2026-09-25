import PyInstaller.__main__
import os
import subprocess
import uuid
import textwrap
import re

APP_NAME = "Blog Toolkit"
SCRIPT_FILE = "main.py" 
ICON_FILE = "logo.ico"

def build():
    imported_modules = set()

    # 1. Konfigurasi Dasar PyInstaller
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
    ]

    # Masukkan semua modul yang terdeteksi secara otomatis sebagai hidden-import
    for mod in imported_modules:
        params.append(f'--hidden-import={mod}')

    if os.path.exists(ICON_FILE):
        params.append(f'--icon={ICON_FILE}')

    print("🚀 Sedang memproses PyInstaller...")
    PyInstaller.__main__.run(params)

    # 2. Kelola AppId persisten (Cek app-id.txt, buat jika belum ada)
    app_id_file = "app-id.txt"
    if os.path.exists(app_id_file):
        with open(app_id_file, "r") as f:
            dynamic_app_id = f.read().strip()
        print(f"🔑 Menggunakan AppId yang ada dari {app_id_file}")
    else:
        dynamic_app_id = f"{{{str(uuid.uuid4()).upper()}}}"
        with open(app_id_file, "w") as f:
            f.write(dynamic_app_id)
        print(f"✨ AppId baru berhasil digenerate dan disimpan ke {app_id_file}")

    # 3. Buat file script Inno Setup secara otomatis (.iss)
    iss_content = textwrap.dedent(f"""\
    #define MyAppName "{APP_NAME}"
    #define MyAppVersion "1.0"
    #define MyAppPublisher "irfanywz"
    #define MyAppExeName "{APP_NAME}.exe"

    [Setup]
    AppId={{{dynamic_app_id}}}
    AppName={{#MyAppName}}
    AppVersion={{#MyAppVersion}}
    AppPublisher={{#MyAppPublisher}}
    DefaultDirName={{localappdata}}\\{{#MyAppPublisher}}\\{{#MyAppName}}
    PrivilegesRequired=lowest
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
    """)

    iss_path = "installer.iss"
    with open(iss_path, "w") as f:
        f.write(iss_content)

    # 4. Cari lokasi compiler Inno Setup (ISCC.exe) secara otomatis di Windows
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