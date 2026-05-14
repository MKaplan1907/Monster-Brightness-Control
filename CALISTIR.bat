@echo off
title Monster Brightness Control
color 0A

echo  [Monster Brightness] Baslatiliyor...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo  Python bulunamadi! https://python.org yukleyin.
    pause
    exit /b 1
)

pip install wmi --quiet 2>nul

REM Yonetici olarak calistir
net session >nul 2>&1
if %errorlevel% neq 0 (
    echo  Yonetici yetkisi isteniyor...
    powershell -Command "Start-Process cmd -ArgumentList '/c cd /d %~dp0 && pip install wmi -q && python monster_brightness.py' -Verb RunAs"
    exit /b
)

python monster_brightness.py
