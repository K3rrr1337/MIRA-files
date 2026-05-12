#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MIRA Loader - Полностью самостоятельная версия
Все зависимости встроены в один EXE файл
"""

import os
import sys
import json
import shutil
import threading
import time
import tempfile
from pathlib import Path
from datetime import datetime
import webview

# Встроенные ресурсы (будут добавлены PyInstaller)
ICON_PATH = "Avatar.ico"

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
            from tkinter import Tk, filedialog
            root = Tk()
            root.withdraw()
            root.attributes('-topmost', True)
            
            folder_path = filedialog.askdirectory(
                title="Выберите папку с игрой",
                initialdir=self.config.get('path', '')
            )
            
            root.destroy()
            
            if folder_path:
                self.config['path'] = folder_path
                self.save_config()
                return folder_path
            return ""
        except Exception as e:
            print(f"Ошибка выбора папки: {e}")
            return ""
    
    def start_install(self, path):
        """Начало установки модификации"""
        if not path:
            return
        
        self.installation_thread = threading.Thread(
            target=self._install_modification, 
            args=(path,), 
            daemon=True
        )
        self.installation_thread.start()
    
    def _install_modification(self, path):
        """Процесс установки модификации"""
        steps = [
            ("Проверка файлов игры...", 10),
            ("Создание резервной копии...", 20),
            ("Загрузка модификации...", 40),
            ("Распаковка файлов...", 60),
            ("Установка компонентов...", 80),
            ("Настройка конфигурации...", 90),
            ("Завершение установки...", 100)
        ]
        
        for message, progress in steps:
            if self.window:
                try:
                    self.window.js.update_ui(message, progress, progress == 100)
                except:
                    pass
            time.sleep(2)
    
    def minimize(self):
        """Свернуть окно"""
        if self.window:
            self.window.minimize()
    
    def exit(self):
        """Выход из приложения"""
        if self.window:
            self.window.destroy()
        sys.exit(0)

def get_icon_data():
    """Получение данных иконки"""
    try:
        if hasattr(sys, '_MEIPASS'):
            # Если запущено из PyInstaller
            icon_path = os.path.join(sys._MEIPASS, 'Avatar.ico')
            if os.path.exists(icon_path):
                return icon_path
    except:
        pass
    
    # Для разработки
    if os.path.exists('Avatar.ico'):
        return 'Avatar.ico'
    
    # Если иконка не найдена, возвращаем None
    return None

def create_window():
    """Создание окна приложения"""
    loader = MIRALoader()
    
    # HTML контент со встроенными стилями и скриптами
    html_content = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>MIRA Loader</title>
    <style>
        :root {
            --bg: #141414;
            --panel: #1c1c1c;
            --accent: #ffffff;
            --border: #2d2d2d;
            --text: #e0e0e0;
            --text-muted: #777;
        }

        * { box-sizing: border-box; margin: 0; padding: 0; user-select: none; }
        body {
            font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: var(--bg);
            color: var(--text);
            height: 100vh;
            display: flex;
            flex-direction: column;
            border: 1px solid var(--border);
            overflow: hidden;
        }

        .titlebar {
            height: 40px; background: var(--panel); border-bottom: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between;
            padding: 0 15px; -webkit-app-region: drag;
        }
        .title { font-size: 12px; font-weight: 700; color: var(--text-muted); text-transform: uppercase; letter-spacing: 1px; }
        .win-ctrls { display: flex; gap: 15px; -webkit-app-region: no-drag; }
        .win-btn { cursor: pointer; color: var(--text-muted); transition: 0.2s; background: none; border: none; font-size: 16px; padding: 4px; }
        .win-btn:hover { color: #fff; }

        .wrapper { flex: 1; display: grid; grid-template-columns: 220px 1fr; overflow: hidden; }

        aside {
            background: #181818; border-right: 1px solid var(--border);
            display: flex; flex-direction: column; padding: 20px 0;
        }
        .menu-item {
            padding: 12px 25px; font-size: 13px; font-weight: 500; color: var(--text-muted);
            cursor: pointer; transition: 0.2s; border-left: 3px solid transparent;
        }
        .menu-item:hover { background: #1c1c1c; color: #fff; }
        .menu-item.active { color: var(--accent); border-left-color: var(--accent); background: #1c1c1c; }

        section { padding: 40px; display: flex; flex-direction: column; }
        .tab-content { display: none; height: 100%; }
        .tab-content.active { display: block; }

        h1 { font-size: 28px; font-weight: 900; margin-bottom: 10px; color: #fff; }
        .desc { font-size: 14px; color: var(--text-muted); margin-bottom: 30px; line-height: 1.5; }

        .input-group {
            background: #0f0f0f; border: 1px solid var(--border); padding: 15px;
            display: flex; align-items: center; gap: 15px; cursor: pointer;
            transition: border-color 0.2s;
        }
        .input-group:hover { border-color: #444; }
        .path-info label { display: block; font-size: 10px; color: var(--text-muted); text-transform: uppercase; margin-bottom: 2px; }
        .path-info span { font-family: 'Courier New', monospace; font-size: 12px; color: #aaa; }

        .console {
            margin-top: auto; background: #0a0a0a; border: 1px solid var(--border);
            height: 120px; padding: 10px; font-family: 'Courier New', monospace; font-size: 11px;
            overflow-y: auto; color: #555;
        }
        .log-msg { margin-bottom: 4px; }
        .log-msg.new { color: var(--accent); }

        footer {
            height: 80px; background: var(--panel); border-top: 1px solid var(--border);
            display: flex; align-items: center; justify-content: space-between; padding: 0 30px;
        }

        .progress-box { flex: 1; margin-right: 40px; }
        .p-text { font-size: 11px; color: var(--text-muted); margin-bottom: 8px; display: flex; justify-content: space-between; }
        .p-bar-bg { height: 6px; background: #111; border-radius: 3px; overflow: hidden; }
        .p-bar-fill { height: 100%; background: var(--accent); width: 0%; transition: width 0.3s; }

        .btn-install {
            background: var(--accent); color: #fff; border: none; padding: 12px 35px;
            font-size: 14px; font-weight: 700; text-transform: uppercase; cursor: pointer;
            border-radius: 3px; transition: background-color 0.2s;
        }
        .btn-install:hover { background: #cccccc; }
        .btn-install:disabled { background: #333; color: #555; cursor: not-allowed; }

        .icon {
            width: 20px; height: 20px; display: inline-block;
        }
        .logo-icon {
            font-size: 20px; margin-right: 10px;
        }
    </style>
</head>
<body>
    <div class="titlebar">
        <div style="display: flex; align-items: center; gap: 10px;">
            <span class="logo-icon">🎮</span>
            <div class="title">MIRA Loader</div>
        </div>
        <div class="win-ctrls">
            <button class="win-btn" onclick="pywebview.api.minimize()">−</button>
            <button class="win-btn" onclick="pywebview.api.exit()">×</button>
        </div>
    </div>

    <div class="wrapper">
        <aside>
            <div class="menu-item active" onclick="tab('instructions', this)">Инструкция</div>
            <div class="menu-item" onclick="tab('main', this)">Установка</div>
            <div class="menu-item" onclick="tab('changelog', this)">Что нового</div>
            <div class="menu-item" onclick="tab('settings', this)">Информация</div>
        </aside>

        <section>
            <div id="instructions" class="tab-content active">
                <h1>Инструкция</h1>
                <p class="desc">1. Установите оригинальную CSGO.</p>
                <p class="desc">2. Выберите папку с игрой.</p>
                <p class="desc">3. Нажмите "Установить модификацию".</p>
                <p class="desc">4. Ожидайте установку модификации.</p>
                <p class="desc">5. Готово, закройте установщик, запустите файл migi.exe.</p>
                <p class="desc">6. Нажмите кнопку Update Build.</p>
            </div>

            <div id="main" class="tab-content">
                <h1>Установка модификации</h1>
                <p class="desc">Добро пожаловать в загрузчик модификации MIRA. Пожалуйста, выберите папку с игрой для начала процесса.</p>

                <div class="input-group" onclick="chooseFolder()">
                    <span class="icon">📁</span>
                    <div class="path-info">
                        <label>Целевой путь</label>
                        <span id="path-txt">Путь не выбран</span>
                    </div>
                </div>

                <div class="console" id="console">
                    <div class="log-msg">Ожидание инициализации...</div>
                </div>
            </div>

            <div id="changelog" class="tab-content">
                <h1>Список изменений</h1>
                <div style="font-family:'Courier New', monospace; font-size: 13px; color: #888; white-space: pre-wrap; line-height: 1.6;">
1. Новый вид загрузчика.
2. Рабочие новости в CSGO.
3. Исправлены баги.
4. Добавлен режим "Запретная зона" для CSGO.
5. Добавлены карты для запретной зоны.</div>
            </div>

            <div id="settings" class="tab-content">
                <h1>Информация</h1>
                <div style="color: #888; font-size: 14px; line-height: 2;">
                    <div>Версия лаунчера: <b style="color:#eee">1.0</b></div>
                    <div>Последняя проверка: <b id="last-check" style="color:#eee">12.05.2026</b></div>
                    <div>Разработчик: <b style="color:#eee">Kerrr1337</b></div>
                    <div>Дизайнер загрузчика: <b style="color:#eee">Teto</b></div>
                    <div>Около-разработчик: <b style="color:#eee">PelmemDev</b></div>
                    <div>Телеграм канал разработчика: <b style="color:#eee">t.me/kerrr1337_pub</b></div>
                    <div>Телеграм канал около-разработчика: <b style="color:#eee">t.me/CSGOINVENTORY123</b></div>
                </div>
            </div>
        </section>
    </div>

    <footer>
        <div class="progress-box">
            <div class="p-text">
                <span id="status-txt">Готов к работе</span>
                <span id="percent-txt">0%</span>
            </div>
            <div class="p-bar-bg">
                <div class="p-bar-fill" id="p-fill"></div>
            </div>
        </div>
        <button class="btn-install" id="action-btn" onclick="install()">Установить</button>
    </footer>

    <script>
        let currentGamePath = "";

        window.addEventListener('pywebviewready', async () => {
            try {
                const cfg = await pywebview.api.init_app();
                if(cfg.path) {
                    currentGamePath = cfg.path;
                    document.getElementById('path-txt').innerText = cfg.path;
                    addLog(`Загружена конфигурация: ${cfg.path}`);
                }
                document.getElementById('last-check').innerText = cfg.last_run;
            } catch(e) {
                addLog('Ошибка инициализации: ' + e.message);
            }
        });

        function tab(id, el) {
            document.querySelectorAll('.tab-content').forEach(t => t.classList.remove('active'));
            document.querySelectorAll('.menu-item').forEach(m => m.classList.remove('active'));
            document.getElementById(id).classList.add('active');
            el.classList.add('active');
        }

        async function chooseFolder() {
            try {
                const res = await pywebview.api.select_folder();
                if(res) {
                    currentGamePath = res;
                    document.getElementById('path-txt').innerText = res;
                    addLog(`Выбран новый путь: ${res}`);
                }
            } catch(e) {
                addLog('Ошибка выбора папки: ' + e.message);
            }
        }

        function install() {
            if(!currentGamePath) {
                alert("Укажите папку с игрой!");
                return;
            }
            document.getElementById('action-btn').disabled = true;
            try {
                pywebview.api.start_install(currentGamePath);
            } catch(e) {
                addLog('Ошибка запуска установки: ' + e.message);
                document.getElementById('action-btn').disabled = false;
            }
        }

        function update_ui(msg, prg, done = null) {
            document.getElementById('status-txt').innerText = msg;
            document.getElementById('percent-txt').innerText = prg + "%";
            document.getElementById('p-fill').style.width = prg + "%";
            addLog(msg, true);

            if(done === true) {
                document.getElementById('action-btn').disabled = false;
                document.getElementById('action-btn').innerText = "ЗАПУСТИТЬ";
                addLog("Процесс успешно завершен.");
            }
        }

        function addLog(text, highlight = false) {
            const con = document.getElementById('console');
            const div = document.createElement('div');
            div.className = highlight ? 'log-msg new' : 'log-msg';
            div.innerText = `[${new Date().toLocaleTimeString()}] ${text}`;
            con.appendChild(div);
            con.scrollTop = con.scrollHeight;
        }
    </script>
</body>
</html>
    """
    
    # Получаем путь к иконке
    icon_path = get_icon_data()
    
    # Создаем окно
    window = webview.create_window(
        'MIRA Loader',
        html=html_content,
        js_api=loader,
        width=900,
        height=700,
        resizable=False,
        frameless=True,
        icon=icon_path
    )
    
    loader.window = window
    return window

if __name__ == "__main__":
    try:
        window = create_window()
        webview.start()
    except Exception as e:
        print(f"Ошибка запуска: {e}")
        # Просто выводим ошибку и выходим
        import sys
        print("Нажмите Ctrl+C для выхода...")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            sys.exit(1)
