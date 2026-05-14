@echo off
title MONSTER BRIGHTNESS - KURULUM VE DERLEME
color 0A

echo.
echo  ███╗   ███╗ ██████╗ ███╗   ██╗███████╗████████╗███████╗██████╗ 
echo  ████╗ ████║██╔═══██╗████╗  ██║██╔════╝╚══██╔══╝██╔════╝██╔══██╗
echo  ██╔████╔██║██║   ██║██╔██╗ ██║███████╗   ██║   █████╗  ██████╔╝
echo  ██║╚██╔╝██║██║   ██║██║╚██╗██║╚════██║   ██║   ██╔══╝  ██╔══██╗
echo  ██║ ╚═╝ ██║╚██████╔╝██║ ╚████║███████║   ██║   ███████╗██║  ██║
echo  ╚═╝     ╚═╝ ╚═════╝ ╚═╝  ╚═══╝╚══════╝   ╚═╝   ╚══════╝╚═╝  ╚═╝
echo.
echo  BRIGHTNESS CONTROL - EXE BUILDER
echo  ==========================================
echo.

REM Python kontrol
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  [HATA] Python bulunamadi!
    echo  https://python.org adresinden Python 3.10+ yukleyin.
    echo  Kurulumda "Add Python to PATH" secenegini isaretleyin!
    pause
    exit /b 1
)

echo  [OK] Python bulundu.

REM pip guncelle
echo  [..] pip guncelleniyor...
python -m pip install --upgrade pip --quiet

REM Bagimliliklar
echo  [..] Gerekli kutuphaneler yukleniyor...
pip install pyinstaller --quiet
pip install wmi --quiet

echo  [OK] Kutuphaneler hazir.

REM PyInstaller ile EXE olustur
echo.
echo  [..] EXE derleniyor... (1-2 dakika surebilir)
echo.

pyinstaller --onefile ^
            --windowed ^
            --name "MonsterBrightness" ^
            --icon NONE ^
            --add-data "." ^
            monster_brightness.py

if %errorlevel% neq 0 (
    echo.
    echo  [HATA] Derleme basarisiz oldu!
    echo  Lutfen hata mesajini kontrol edin.
    pause
    exit /b 1
)

echo.
echo  ==========================================
echo  [BASARILI] EXE olusturuldu!
echo  Konum: dist\MonsterBrightness.exe
echo  ==========================================
echo.

REM EXE yi ana klasore kopyala
copy "dist\MonsterBrightness.exe" "MonsterBrightness.exe" >nul 2>&1

echo  MonsterBrightness.exe bu klasorde hazir!
echo  Sag tikla - Yonetici olarak calistir deneyin.
echo.
pause
