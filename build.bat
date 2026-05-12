@echo off
echo ========================================
echo Сборка MIRA Loader
echo ========================================
echo.

REM Проверяем наличие Python
python --version >nul 2>&1
if errorlevel 1 (
    py --version >nul 2>&1
    if errorlevel 1 (
        echo Ошибка: Python не найден!
        echo Пожалуйста, установите Python с https://python.org
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=py
    )
) else (
    set PYTHON_CMD=python
)

REM Установка зависимостей
echo Установка зависимостей...
%PYTHON_CMD% -m pip install -r requirements.txt
if errorlevel 1 (
    echo Ошибка при установке зависимостей!
    pause
    exit /b 1
)

echo Зависимости успешно установлены.
echo.

REM Сборка EXE файла
echo Сборка исполняемого файла...
%PYTHON_CMD% -m PyInstaller --onefile --windowed --name "MIRA_Loader" --icon="Avatar.ico" --add-data="index.html;." --add-data="Avatar.ico;." loader.py
if errorlevel 1 (
    echo Ошибка при сборке EXE файла!
    pause
    exit /b 1
)

echo.
echo ========================================
echo Сборка завершена успешно!
echo ========================================
echo.
echo Исполняемый файл находится в папке: dist\MIRA_Loader.exe
echo.
echo Для запуска установщика:
echo 1. Перейдите в папку dist
echo 2. Запустите MIRA_Loader.exe
echo.

REM Копирование HTML файла в папку dist
echo Копирование HTML файла...
copy index.html dist\ >nul
if errorlevel 1 (
    echo Предупреждение: Не удалось скопировать index.html
)

REM Создание папки для файлов модификации
if not exist "dist\modification_files" (
    mkdir "dist\modification_files"
    echo Создана папка для файлов модификации
)

echo.
echo Готово! Нажмите любую клавишу для выхода...
pause >nul
