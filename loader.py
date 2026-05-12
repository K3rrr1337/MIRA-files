import os
import sys
import json
import shutil
import threading
import time
import requests
import py7zr
import tempfile
from pathlib import Path
from datetime import datetime
import webview

class MIRALoader:
    def __init__(self):
        self.config_file = "config.json"
        self.window = None
        self.installation_thread = None
        self.config = self.load_config()
        
    def load_config(self):
        """Загрузка конфигурации"""
        default_config = {
            "path": "",
            "last_run": datetime.now().strftime("%d.%m.%Y"),
            "version": "1.0"
        }
        
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                return {**default_config, **config}
            except:
                return default_config
        else:
            self.save_config(default_config)
            return default_config
    
    def save_config(self, config):
        """Сохранение конфигурации"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Ошибка сохранения конфига: {e}")
    
    def init_app(self):
        """Инициализация приложения"""
        return self.config
    
    def select_folder(self):
        """Выбор папки с игрой"""
        try:
            folder = self.window.create_file_dialog(webview.FOLDER_DIALOG)
            if folder:
                # webview возвращает список, берем первый элемент
                if isinstance(folder, list) and len(folder) > 0:
                    folder = folder[0]
                self.config["path"] = folder
                self.save_config(self.config)
                return folder
            return None
        except Exception as e:
            print(f"Ошибка выбора папки: {e}")
            return None
    
    def start_install(self, game_path):
        """Начало установки модификации"""
        if self.installation_thread and self.installation_thread.is_alive():
            return
        
        self.installation_thread = threading.Thread(
            target=self.install_modification,
            args=(game_path,),
            daemon=True
        )
        self.installation_thread.start()
    
    def download_from_yandex_disk(self, url, download_path):
        """Скачивание файла с Яндекс.Диска без подтверждений"""
        try:
            self.update_ui(f"Запрос ссылки: {url}", 5)
            
            # Получаем прямую ссылку для скачивания
            response = requests.get(url, allow_redirects=True)
            self.update_ui(f"Ответ сервера: {response.status_code}", 10)
            
            if response.status_code != 200:
                raise Exception(f"Не удалось получить доступ к файлу: {response.status_code}")
            
            # Проверяем редирект на скачивание
            if 'download' in response.url or 'get' in response.url:
                self.update_ui("Получена прямая ссылка на скачивание", 15)
            
            # Определяем имя файла из URL или используем стандартное
            filename = "MIRA_archive.7z"
            if 'Content-Disposition' in response.headers:
                import re
                cd = response.headers['Content-Disposition']
                fname_match = re.search(r'filename\*?=(?:UTF-8|utf-8)?\'\'?([^";\n\r]+)', cd)
                if fname_match:
                    filename = fname_match.group(1).strip('"\'')
            
            file_path = os.path.join(download_path, filename)
            self.update_ui(f"Файл будет сохранен как: {file_path}", 20)
            
            # Проверяем размер файла
            total_size = int(response.headers.get('content-length', 0))
            self.update_ui(f"Размер архива: {total_size} байт", 25)
            
            # Скачиваем файл с прогрессом
            with open(file_path, 'wb') as f:
                downloaded = 0
                
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        
                        if total_size > 0:
                            progress = 25 + int((downloaded / total_size) * 20)
                            self.update_ui(f"Скачивание... {downloaded}/{total_size} байт ({int(downloaded/total_size*100)}%)", progress)
            
            self.update_ui(f"Архив успешно скачан: {downloaded} байт", 45)
            return file_path
            
        except Exception as e:
            self.update_ui(f"Ошибка скачивания: {str(e)}", 0)
            return None
    
    def extract_archive(self, archive_path, extract_to):
        """Разархивирование с заменой существующих файлов"""
        try:
            self.update_ui("Подготовка к разархивированию...", 45)
            
            if not os.path.exists(archive_path):
                raise Exception(f"Архив не найден: {archive_path}")
            
            # Создаем временную папку для извлечения
            with tempfile.TemporaryDirectory() as temp_dir:
                self.update_ui("Извлечение файлов из архива...", 50)
                
                # Извлекаем архив во временную папку
                with py7zr.SevenZipFile(archive_path, mode='r') as archive:
                    archive.extractall(temp_dir)
                
                self.update_ui("Копирование файлов в целевую директорию...", 60)
                
                # Копируем файлы с заменой существующих
                copied_files = 0
                total_files = sum(len(files) for _, _, files in os.walk(temp_dir))
                
                for root, dirs, files in os.walk(temp_dir):
                    for file in files:
                        src_path = os.path.join(root, file)
                        # Вычисляем относительный путь
                        rel_path = os.path.relpath(src_path, temp_dir)
                        dst_path = os.path.join(extract_to, rel_path)
                        
                        # Создаем директорию если нужно
                        os.makedirs(os.path.dirname(dst_path), exist_ok=True)
                        
                        # Копируем файл с заменой
                        shutil.copy2(src_path, dst_path)
                        copied_files += 1
                        
                        # Обновляем прогресс
                        if total_files > 0:
                            progress = 60 + int((copied_files / total_files) * 35)
                            self.update_ui(f"Копирование файлов... {copied_files}/{total_files}", progress)
                
                # Удаляем архив после успешного извлечения
                os.remove(archive_path)
                
            self.update_ui(f"Успешно скопировано {copied_files} файлов", 95)
            return True
            
        except Exception as e:
            self.update_ui(f"Ошибка разархивирования: {str(e)}", 0)
            return False
    
    def install_modification(self, game_path):
        """Процесс установки модификации"""
        try:
            self.update_ui(f"Начало установки в папку: {game_path}", 5)
            
            # Проверяем существование папки
            if not os.path.exists(game_path):
                self.update_ui("Ошибка: Указанная папка не существует!", 0)
                return
            
            self.update_ui("Папка игры найдена, проверка CS:GO...", 10)
            
            # Проверяем наличие CS:GO
            csgo_path = os.path.join(game_path, "csgo")
            if not os.path.exists(csgo_path):
                self.update_ui("Ошибка: Папка CS:GO не найдена!", 0)
                return
            
            self.update_ui(f"Папка CS:GO найдена: {csgo_path}", 15)
            
            # URL архива с Яндекс.Диска
            yandex_url = "https://disk.yandex.ru/d/ITwIjUgSW-kl3A"
            self.update_ui("Подготовка к скачиванию архива...", 20)
            
            # Создаем временную папку для скачивания
            temp_dir = tempfile.mkdtemp()
            self.update_ui(f"Временная папка создана: {temp_dir}", 25)
            
            try:
                # Скачиваем архив
                self.update_ui("Начало скачивания архива...", 30)
                archive_path = self.download_from_yandex_disk(yandex_url, temp_dir)
                if not archive_path:
                    self.update_ui("Ошибка: Не удалось скачать архив", 0)
                    return
                
                self.update_ui(f"Архив скачан: {archive_path}", 45)
                
                # Разархивируем в папку CS:GO
                self.update_ui("Начало разархивирования...", 50)
                if self.extract_archive(archive_path, csgo_path):
                    self.update_ui("Файлы успешно разархивированы", 90)
                    
                    # Создаем конфигурационный файл
                    self.configure_modification(csgo_path)
                    
                    # Обновляем конфигурацию
                    self.config["last_run"] = datetime.now().strftime("%d.%m.%Y")
                    self.save_config(self.config)
                    
                    # Завершаем установку
                    self.update_ui("Установка успешно завершена!", 100, True)
                else:
                    self.update_ui("Ошибка при установке файлов!", 0)
                    
            finally:
                # Очищаем временную папку
                shutil.rmtree(temp_dir, ignore_errors=True)
            
        except Exception as e:
            self.update_ui(f"Ошибка установки: {str(e)}", 0)
    
    def create_backup(self, csgo_path):
        """Создание резервной копии"""
        try:
            backup_path = os.path.join(csgo_path, "backup")
            if not os.path.exists(backup_path):
                os.makedirs(backup_path)
                
                # Список файлов для резервного копирования
                backup_files = [
                    "pak_01.dir",
                    "pak_02.dir", 
                    "pak_03.dir",
                    "pak_04.dir",
                    "pak_05.dir"
                ]
                
                for file_name in backup_files:
                    src = os.path.join(csgo_path, file_name)
                    dst = os.path.join(backup_path, file_name)
                    if os.path.exists(src):
                        shutil.copy2(src, dst)
        except Exception as e:
            print(f"Ошибка создания бэкапа: {e}")
    
    def extract_modification_files(self, csgo_path):
        """Извлечение файлов модификации"""
        try:
            # Здесь должна быть логика распаковки файлов модификации
            # Например, из архива или из папки с файлами
            
            mod_files_path = "modification_files"  # Папка с файлами модификации
            if os.path.exists(mod_files_path):
                self.copy_directory(mod_files_path, csgo_path)
            else:
                # Создаем пустые файлы для демонстрации
                demo_files = [
                    "migi.exe",
                    "migi_config.ini",
                    "modification pak_01.dir",
                    "modification pak_02.dir"
                ]
                
                for file_name in demo_files:
                    dst_path = os.path.join(csgo_path, file_name)
                    with open(dst_path, 'w', encoding='utf-8') as f:
                        f.write(f"# Файл модификации MIRA\n# Создан: {datetime.now()}\n")
        except Exception as e:
            print(f"Ошибка извлечения файлов: {e}")
    
    def configure_modification(self, csgo_path):
        """Настройка модификации"""
        try:
            # Создание конфигурационного файла
            config_path = os.path.join(csgo_path, "migi_config.ini")
            
            config_content = f"""[MIRA Modification]
version=1.0
installed_date={datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
game_path={csgo_path}
modification_enabled=true

[Settings]
graphics_quality=high
sound_enabled=true
network_optimization=true
"""
            
            with open(config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
                
        except Exception as e:
            print(f"Ошибка конфигурации: {e}")
    
    def copy_directory(self, src, dst):
        """Копирование директории"""
        try:
            if os.path.exists(src):
                for item in os.listdir(src):
                    src_path = os.path.join(src, item)
                    dst_path = os.path.join(dst, item)
                    
                    if os.path.isdir(src_path):
                        if not os.path.exists(dst_path):
                            os.makedirs(dst_path)
                        self.copy_directory(src_path, dst_path)
                    else:
                        shutil.copy2(src_path, dst_path)
        except Exception as e:
            print(f"Ошибка копирования: {e}")
    
    def update_ui(self, message, progress, done=False):
        """Обновление интерфейса"""
        if self.window:
            self.window.evaluate_js(f"updateUI('{message}', {progress}, {str(done).lower()})")
    
    def minimize(self):
        """Свернуть окно"""
        if self.window:
            self.window.minimize()
    
    def exit(self):
        """Выход из приложения"""
        if self.window:
            self.window.destroy()
    
    def run(self):
        """Запуск приложения"""
        try:
            # Определяем путь к index.html
            if getattr(sys, 'frozen', False):
                # Если запущено как EXE
                base_path = sys._MEIPASS
            else:
                # Если запущено как скрипт
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            html_path = os.path.join(base_path, 'index.html')
            
            # Путь к иконке
            icon_path = os.path.join(base_path, 'Avatar.ico')
            
            # Создание окна
            self.window = webview.create_window(
                'MIRA Loader',
                html_path,
                js_api=self,
                width=900,
                height=700,
                resizable=False,
                frameless=True
            )
            
            # Запуск приложения
            webview.start()
            
        except Exception as e:
            print(f"Ошибка запуска приложения: {e}")

def main():
    """Главная функция"""
    try:
        # Проверяем наличие HTML файла
        if not os.path.exists("index.html"):
            print("Ошибка: Файл index.html не найден!")
            return
        
        # Запуск загрузчика
        loader = MIRALoader()
        loader.run()
        
    except Exception as e:
        print(f"Критическая ошибка: {e}")

if __name__ == "__main__":
    main()
