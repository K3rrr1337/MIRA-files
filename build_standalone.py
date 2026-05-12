#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Сборка полностью самостоятельного EXE файла
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def build_standalone_exe():
    """Сборка полностью самостоятельного EXE"""
    print("=== Сборка самостоятельного MIRA Loader ===\n")
    
    # Проверяем наличие файлов
    required_files = [
        "loader_standalone.py",
        "Avatar.ico"
    ]
    
    for file in required_files:
        if not Path(file).exists():
            print(f"Ошибка: файл {file} не найден!")
            return False
    
    # Команда для PyInstaller
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                    # Один файл
        "--windowed",                   # Без консоли
        "--name", "MIRA_Loader",        # Имя EXE
        "--icon=Avatar.ico",            # Иконка
        "--add-data=Avatar.ico;.",      # Включить иконку в ресурсы
        "--hidden-import=tkinter",      # Включить tkinter
        "--hidden-import=tkinter.filedialog",  # Включить filedialog
        "loader_standalone.py"
    ]
    
    print("Запуск сборки...")
    print(f"Команда: {' '.join(cmd)}")
    
    try:
        # Запускаем сборку
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        print("Сборка успешно завершена!")
        
        # Проверяем результат
        exe_file = Path("dist/MIRA_Loader.exe")
        if exe_file.exists():
            size_mb = exe_file.stat().st_size / (1024*1024)
            print(f"EXE файл создан: {exe_file.absolute()}")
            print(f"Размер: {size_mb:.1f} МБ")
            
            # Создаем финальную папку
            final_dir = Path("MIRA_Loader_Standalone")
            if final_dir.exists():
                shutil.rmtree(final_dir)
            final_dir.mkdir()
            
            # Копируем EXE
            shutil.copy(exe_file, final_dir / "MIRA_Loader.exe")
            
            print(f"\n=== Готово! ===")
            print(f"Финальная папка: {final_dir.absolute()}")
            print(f"Структура:")
            print(f"MIRA_Loader_Standalone/")
            print(f"└── MIRA_Loader.exe (полностью самостоятельный)")
            print(f"\nДля запуска: дважды кликните MIRA_Loader.exe")
            
            return True
        else:
            print("Ошибка: EXE файл не найден после сборки")
            return False
            
    except subprocess.CalledProcessError as e:
        print(f"Ошибка сборки: {e}")
        print(f"STDOUT: {e.stdout}")
        print(f"STDERR: {e.stderr}")
        return False
    except Exception as e:
        print(f"Неожиданная ошибка: {e}")
        return False

if __name__ == "__main__":
    try:
        success = build_standalone_exe()
        if not success:
            input("\nНажмите Enter для выхода...")
    except KeyboardInterrupt:
        print("\nПрервано пользователем")
    except Exception as e:
        print(f"\nОшибка: {e}")
        input("Нажмите Enter для выхода...")
