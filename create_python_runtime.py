#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Создание Python runtime со всеми зависимостями для MIRA Loader
"""

import os
import sys
import shutil
import subprocess
import zipfile
import urllib.request
from pathlib import Path

def download_python_embed():
    """Скачивание встраиваемой версии Python"""
    python_version = "3.10.11"
    python_url = f"https://www.python.org/ftp/python/{python_version}/python-{python_version}-embed-amd64.zip"
    zip_path = "python_embed.zip"
    
    print(f"Скачивание Python {python_version}...")
    
    try:
        urllib.request.urlretrieve(python_url, zip_path)
        print(f"Python скачан: {zip_path}")
        return zip_path
    except Exception as e:
        print(f"Ошибка скачивания Python: {e}")
        return None

def extract_python(zip_path, target_dir):
    """Распаковка Python runtime"""
    print(f"Распаковка Python в {target_dir}...")
    
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(target_dir)
        print("Python runtime распакован")
        return True
    except Exception as e:
        print(f"Ошибка распаковки Python: {e}")
        return False

def setup_python_runtime(python_dir):
    """Настройка Python runtime"""
    # Модифицируем python310._pth для импорта site-packages
    pth_file = python_dir / "python310._pth"
    if pth_file.exists():
        content = pth_file.read_text(encoding='utf-8')
        if "#import site" in content:
            content = content.replace("#import site", "import site")
            pth_file.write_text(content, encoding='utf-8')
            print("Настроен python310._pth для site-packages")
    
    # Создаем папку для пакетов
    site_packages = python_dir / "Lib" / "site-packages"
    site_packages.mkdir(parents=True, exist_ok=True)
    
    return True

def install_packages(python_dir):
    """Установка необходимых пакетов"""
    python_exe = python_dir / "python.exe"
    site_packages = python_dir / "Lib" / "site-packages"
    
    print("Установка необходимых пакетов...")
    
    # Скачиваем get-pip.py
    get_pip_url = "https://bootstrap.pypa.io/get-pip.py"
    get_pip_path = python_dir / "get-pip.py"
    
    try:
        urllib.request.urlretrieve(get_pip_url, get_pip_path)
        
        # Устанавливаем pip
        subprocess.run([
            str(python_exe), str(get_pip_path), 
            "--target", str(site_packages)
        ], check=True, capture_output=True)
        
        # Устанавливаем необходимые пакеты из requirements.txt
        packages = [
            "pywebview",
            "requests", 
            "py7zr",
            "psutil"
        ]
        
        for package in packages:
            print(f"Установка {package}...")
            subprocess.run([
                str(python_exe), "-m", "pip", "install", "--target", 
                str(site_packages), package
            ], check=True, capture_output=True)
        
        # Удаляем get-pip.py
        get_pip_path.unlink()
        
        print("Пакеты установлены")
        return True
        
    except Exception as e:
        print(f"Ошибка установки пакетов: {e}")
        return False

def create_final_structure():
    """Создание финальной структуры"""
    print("Создание финальной структуры...")
    
    # Создаем папки
    dirs = [
        "MIRA_Loader_Final",
        "MIRA_Loader_Final/python"
    ]
    
    for dir_path in dirs:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    
    return Path("MIRA_Loader_Final")

def main():
    """Основная функция"""
    print("=== Создание MIRA Loader с Python runtime ===\n")
    
    # Создаем структуру
    final_dir = create_final_structure()
    python_dir = final_dir / "python"
    
    # Скачиваем и распаковываем Python
    zip_path = download_python_embed()
    if not zip_path:
        return False
    
    if not extract_python(zip_path, python_dir):
        return False
    
    # Удаляем zip файл
    os.remove(zip_path)
    
    # Настраиваем Python
    if not setup_python_runtime(python_dir):
        return False
    
    # Устанавливаем пакеты
    if not install_packages(python_dir):
        return False
    
    # Копируем EXE файл
    exe_source = Path("dist/MIRA_Loader.exe")
    if exe_source.exists():
        shutil.copy(exe_source, final_dir / "MIRA_Loader.exe")
        print(f"Скопирован EXE файл: {final_dir / 'MIRA_Loader.exe'}")
    
    # Копируем HTML
    html_source = Path("dist/index.html")
    if html_source.exists():
        shutil.copy(html_source, final_dir / "index.html")
        print(f"Скопирован HTML: {final_dir / 'index.html'}")
    
    # Создаем launcher.bat
    launcher_content = """@echo off
title MIRA Loader
cd /d "%~dp0"

REM Запускаем с локальным Python
python\\python.exe MIRA_Loader.exe

if %errorlevel% neq 0 (
    echo.
    echo Произошла ошибка при запуске.
    pause
)
"""
    
    launcher_path = final_dir / "MiraLoader.bat"
    launcher_path.write_text(launcher_content, encoding='cp866')
    print(f"Создан launcher: {launcher_path}")
    
    # Создаем README
    readme_content = """# MIRA Loader - Полная версия

## 🚀 Структура

```
MIRA_Loader_Final/
├── MIRA_Loader.exe         # Основной исполняемый файл
├── python/                 # Полный Python runtime со всеми зависимостями
│   ├── python.exe
│   ├── python310.dll
│   ├── Lib/
│   │   └── site-packages/  # Все установленные пакеты
│   └── ...
├── index.html              # HTML интерфейс
├── MiraLoader.bat          # Launcher для запуска
└── README.md              # Этот файл
```

## 📋 Запуск

### Вариант 1: Через launcher
Дважды кликните `MiraLoader.bat`

### Вариант 2: Прямой запуск
```cmd
python\python.exe MIRA_Loader.exe
```

## ✨ Особенности

- **Полностью автономная** - все зависимости включены
- **Python runtime встроен** - не требует установки Python
- **Все пакеты установлены** - pywebview, requests, py7zr и др.
- **Портативная** - можно скопировать всю папку

## 📦 Что включено

- Python 3.10.11 embeddable
- pywebview (для GUI)
- requests (для HTTP запросов)
- py7zr (для архивов)
- psutil (для системных функций)
- Все остальные зависимости

## 🔧 Как это работает

1. `MiraLoader.bat` запускает локальный Python
2. Python выполняет `MIRA_Loader.exe`
3. Приложение использует встроенные библиотеки из `python/Lib/site-packages`

## 🚚 Распространение

Скопируйте всю папку `MIRA_Loader_Final`:
- На другой компьютер
- На USB флешку
- В сетевую папку

Работать будет везде без дополнительной установки!

---
Разработано для MIRA Modification Team
"""
    
    readme_path = final_dir / "README.md"
    readme_path.write_text(readme_content, encoding='utf-8')
    print(f"Создан README: {readme_path}")
    
    # Создаем инструкцию по размеру
    total_size = sum(f.stat().st_size for f in final_dir.rglob('*') if f.is_file())
    
    print(f"\n=== Готово! ===")
    print(f"Папка: {final_dir.absolute()}")
    print(f"Общий размер: {total_size / (1024*1024):.1f} МБ")
    print(f"\nСтруктура:")
    print(f"├── MIRA_Loader.exe")
    print(f"├── python/ (Python runtime + зависимости)")
    print(f"├── index.html")
    print(f"├── MiraLoader.bat")
    print(f"└── README.md")
    print(f"\nДля запуска: MiraLoader.bat")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            input("\nНажмите Enter для выхода...")
        else:
            input("\nПроизошла ошибка. Нажмите Enter для выхода...")
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"\nНеожиданная ошибка: {e}")
        input("Нажмите Enter для выхода...")
