import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import shutil
import threading
import time
from pathlib import Path

class CS GOInstaller:
    def __init__(self, root):
        self.root = root
        self.root.title("Установщик модификации CS:GO")
        self.root.geometry("900x700")
        self.root.configure(bg='#0a0a0a')
        
        # Переменные
        self.current_step = 1
        self.install_path = tk.StringVar(value="C:\\Program Files (x86)\\Steam\\steamapps\\common\\Counter-Strike Global Offensive")
        self.installation_progress = tk.IntVar(value=0)
        self.installation_running = False
        
        # Создаем стиль
        self.setup_styles()
        
        # Создаем интерфейс
        self.create_widgets()
        
        # Показываем первый шаг
        self.show_step(1)
    
    def setup_styles(self):
        """Настройка стилей для компонентов"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Стиль для кнопок
        style.configure('Primary.TButton',
                       background='#0066cc',
                       foreground='white',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 11, 'bold'))
        
        style.map('Primary.TButton',
                 background=[('active', '#0052a3')])
        
        style.configure('Secondary.TButton',
                       background='white',
                       foreground='#333333',
                       borderwidth=0,
                       focuscolor='none',
                       font=('Segoe UI', 11, 'bold'))
        
        style.map('Secondary.TButton',
                 background=[('active', '#f0f0f0')])
        
        # Стиль для прогресс-бара
        style.configure('Custom.Horizontal.TProgressbar',
                       background='#0066cc',
                       troughcolor='#333333',
                       borderwidth=0,
                       lightcolor='#0066cc',
                       darkcolor='#0066cc')
    
    def create_widgets(self):
        """Создание всех виджетов интерфейса"""
        # Заголовок
        header_frame = tk.Frame(self.root, bg='#000000', height=80)
        header_frame.pack(fill='x', padx=0, pady=0)
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(header_frame, 
                              text="[⚡] Установщик модификации CS:GO",
                              font=('Segoe UI', 20, 'bold'),
                              fg='#0066cc',
                              bg='#000000')
        title_label.pack(expand=True)
        
        # Основной контент
        self.content_frame = tk.Frame(self.root, bg='#0a0a0a')
        self.content_frame.pack(fill='both', expand=True, padx=20, pady=20)
        
        # Создаем все шаги
        self.create_step1()
        self.create_step2()
        self.create_step3()
        self.create_step4()
        self.create_step5()
    
    def create_step1(self):
        """Шаг 1: О проекте"""
        self.step1_frame = tk.Frame(self.content_frame, bg='#141414', relief='solid', bd=1)
        
        # Индикаторы шагов
        steps_frame = tk.Frame(self.step1_frame, bg='#141414')
        steps_frame.pack(pady=(30, 20))
        
        for i in range(1, 6):
            step_color = '#0066cc' if i == 1 else '#333333'
            step_label = tk.Label(steps_frame, text=str(i),
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg=step_color,
                                 width=4, height=2)
            step_label.pack(side='left', padx=5)
        
        # Контент
        info_frame = tk.Frame(self.step1_frame, bg='#141414')
        info_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        title = tk.Label(info_frame, text="[🔥] Модификация CS:GO",
                        font=('Segoe UI', 18, 'bold'),
                        fg='#0066cc', bg='#141414')
        title.pack(pady=(0, 20))
        
        texts = [
            "Добро пожаловать в установщик передовой модификации для Counter-Strike: Global Offensive!",
            "Эта модификация добавит совершенно новый игровой опыт с улучшенной графикой,",
            "новыми возможностями и уникальными функциями.",
            "Следуйте инструкциям установщика для корректной установки всех компонентов."
        ]
        
        for text in texts:
            label = tk.Label(info_frame, text=text,
                           font=('Segoe UI', 11),
                           fg='#cccccc', bg='#141414',
                           wraplength=600)
            label.pack(pady=5)
        
        # Кнопки
        buttons_frame = tk.Frame(self.step1_frame, bg='#141414')
        buttons_frame.pack(pady=30)
        
        start_btn = self.create_button(buttons_frame, "Начать установку", self.start_installation, 'primary')
        start_btn.pack(side='left', padx=10)
        
        telegram_btn = self.create_button(buttons_frame, "Канал разработчика", self.open_telegram, 'secondary')
        telegram_btn.pack(side='left', padx=10)
    
    def create_step2(self):
        """Шаг 2: Выбор пути установки"""
        self.step2_frame = tk.Frame(self.content_frame, bg='#141414', relief='solid', bd=1)
        
        # Индикаторы шагов
        steps_frame = tk.Frame(self.step2_frame, bg='#141414')
        steps_frame.pack(pady=(30, 20))
        
        for i in range(1, 6):
            if i < 2:
                step_color = '#00aa00'
                step_text = '✓'
            elif i == 2:
                step_color = '#0066cc'
                step_text = str(i)
            else:
                step_color = '#333333'
                step_text = str(i)
            
            step_label = tk.Label(steps_frame, text=step_text,
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg=step_color,
                                 width=4, height=2)
            step_label.pack(side='left', padx=5)
        
        # Контент
        info_frame = tk.Frame(self.step2_frame, bg='#141414')
        info_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        title = tk.Label(info_frame, text="[📁] Выбор пути установки",
                        font=('Segoe UI', 18, 'bold'),
                        fg='#0066cc', bg='#141414')
        title.pack(pady=(0, 20))
        
        tk.Label(info_frame, text="Выберите путь установки модификации:",
                font=('Segoe UI', 12),
                fg='#cccccc', bg='#141414').pack(pady=5)
        
        tk.Label(info_frame, text="Укажите директорию, где установлена ваша игра CS:GO",
                font=('Segoe UI', 12),
                fg='#cccccc', bg='#141414').pack(pady=5)
        
        # Поле для пути
        path_frame = tk.Frame(info_frame, bg='#141414')
        path_frame.pack(pady=20, fill='x', padx=20)
        
        self.path_entry = tk.Entry(path_frame, textvariable=self.install_path,
                                  font=('Segoe UI', 11),
                                  bg='#333333', fg='white',
                                  insertbackground='white',
                                  relief='solid', bd=1)
        self.path_entry.pack(side='left', fill='x', expand=True, padx=(0, 10))
        
        browse_btn = self.create_button(path_frame, "Обзор", self.browse_path, 'secondary')
        browse_btn.pack(side='right')
        
        # Кнопки
        buttons_frame = tk.Frame(self.step2_frame, bg='#141414')
        buttons_frame.pack(pady=30)
        
        back_btn = self.create_button(buttons_frame, "Назад", lambda: self.show_step(1), 'secondary')
        back_btn.pack(side='left', padx=10)
        
        next_btn = self.create_button(buttons_frame, "Далее", lambda: self.show_step(3), 'primary')
        next_btn.pack(side='left', padx=10)
    
    def create_step3(self):
        """Шаг 3: Процесс установки"""
        self.step3_frame = tk.Frame(self.content_frame, bg='#141414', relief='solid', bd=1)
        
        # Индикаторы шагов
        steps_frame = tk.Frame(self.step3_frame, bg='#141414')
        steps_frame.pack(pady=(30, 20))
        
        for i in range(1, 6):
            if i < 3:
                step_color = '#00aa00'
                step_text = '✓'
            elif i == 3:
                step_color = '#0066cc'
                step_text = str(i)
            else:
                step_color = '#333333'
                step_text = str(i)
            
            step_label = tk.Label(steps_frame, text=step_text,
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg=step_color,
                                 width=4, height=2)
            step_label.pack(side='left', padx=5)
        
        # Контент
        info_frame = tk.Frame(self.step3_frame, bg='#141414')
        info_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        title = tk.Label(info_frame, text="[⚡] Установка модификации",
                        font=('Segoe UI', 18, 'bold'),
                        fg='#0066cc', bg='#141414')
        title.pack(pady=(0, 20))
        
        tk.Label(info_frame, text="Идет установка файлов модификации...",
                font=('Segoe UI', 12),
                fg='#cccccc', bg='#141414').pack(pady=5)
        
        # Статус
        self.status_label = tk.Label(info_frame, text="Подготовка к установке...",
                                    font=('Segoe UI', 14, 'bold'),
                                    fg='#0066cc', bg='#141414')
        self.status_label.pack(pady=20)
        
        # Прогресс-бар
        progress_frame = tk.Frame(info_frame, bg='#141414')
        progress_frame.pack(pady=20, fill='x', padx=20)
        
        self.progress_bar = ttk.Progressbar(progress_frame, 
                                           variable=self.installation_progress,
                                           maximum=100,
                                           style='Custom.Horizontal.TProgressbar',
                                           length=400)
        self.progress_bar.pack(fill='x')
        
        self.progress_label = tk.Label(progress_frame, text="0%",
                                      font=('Segoe UI', 11, 'bold'),
                                      fg='white', bg='#141414')
        self.progress_label.pack(pady=5)
        
        # Список файлов
        files_frame = tk.Frame(info_frame, bg='#141414')
        files_frame.pack(pady=20, fill='both', expand=True, padx=20)
        
        tk.Label(files_frame, text="Устанавливаемые файлы:",
                font=('Segoe UI', 11, 'bold'),
                fg='#cccccc', bg='#141414').pack(anchor='w')
        
        # Текстовое поле для списка файлов
        self.files_text = tk.Text(files_frame, height=8, width=60,
                                 font=('Consolas', 10),
                                 bg='#000000', fg='#cccccc',
                                 relief='solid', bd=1)
        self.files_text.pack(fill='both', expand=True, pady=5)
        self.files_text.insert('1.0', "[📦] Подготовка установочных файлов...\n")
        self.files_text.config(state='disabled')
        
        # Кнопки
        buttons_frame = tk.Frame(self.step3_frame, bg='#141414')
        buttons_frame.pack(pady=30)
        
        back_btn = self.create_button(buttons_frame, "Назад", lambda: self.show_step(2), 'secondary')
        back_btn.pack(side='left', padx=10)
        
        self.complete_btn = self.create_button(buttons_frame, "Готово", lambda: self.show_step(4), 'primary')
        self.complete_btn.pack(side='left', padx=10)
        self.complete_btn.config(state='disabled')
    
    def create_step4(self):
        """Шаг 4: Инструкция"""
        self.step4_frame = tk.Frame(self.content_frame, bg='#141414', relief='solid', bd=1)
        
        # Индикаторы шагов
        steps_frame = tk.Frame(self.step4_frame, bg='#141414')
        steps_frame.pack(pady=(30, 20))
        
        for i in range(1, 6):
            if i < 4:
                step_color = '#00aa00'
                step_text = '✓'
            elif i == 4:
                step_color = '#0066cc'
                step_text = str(i)
            else:
                step_color = '#333333'
                step_text = str(i)
            
            step_label = tk.Label(steps_frame, text=step_text,
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg=step_color,
                                 width=4, height=2)
            step_label.pack(side='left', padx=5)
        
        # Контент
        info_frame = tk.Frame(self.step4_frame, bg='#141414')
        info_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        title = tk.Label(info_frame, text="[📖] Инструкция по использованию",
                        font=('Segoe UI', 18, 'bold'),
                        fg='#0066cc', bg='#141414')
        title.pack(pady=(0, 20))
        
        tk.Label(info_frame, text="Здесь будет размещена подробная инструкция по использованию модификации.",
                font=('Segoe UI', 12),
                fg='#cccccc', bg='#141414').pack(pady=5)
        
        # Поле для инструкции
        instruction_frame = tk.Frame(info_frame, bg='#141414')
        instruction_frame.pack(pady=20, fill='both', expand=True, padx=20)
        
        self.instruction_text = tk.Text(instruction_frame, height=12, width=60,
                                      font=('Segoe UI', 11),
                                      bg='#000000', fg='#cccccc',
                                      relief='solid', bd=1,
                                      wrap='word')
        self.instruction_text.pack(fill='both', expand=True)
        
        default_instruction = """Инструкция по использованию модификации:

[•] Первый шаг использования
[•] Второй шаг использования  
[•] Третий шаг использования
[•] И так далее...

Здесь вы можете написать свою инструкцию по использованию модификации."""
        
        self.instruction_text.insert('1.0', default_instruction)
        
        # Кнопки
        buttons_frame = tk.Frame(self.step4_frame, bg='#141414')
        buttons_frame.pack(pady=30)
        
        back_btn = self.create_button(buttons_frame, "Назад", lambda: self.show_step(3), 'secondary')
        back_btn.pack(side='left', padx=10)
        
        next_btn = self.create_button(buttons_frame, "Далее", lambda: self.show_step(5), 'primary')
        next_btn.pack(side='left', padx=10)
    
    def create_step5(self):
        """Шаг 5: Завершение"""
        self.step5_frame = tk.Frame(self.content_frame, bg='#141414', relief='solid', bd=1)
        
        # Индикаторы шагов
        steps_frame = tk.Frame(self.step5_frame, bg='#141414')
        steps_frame.pack(pady=(30, 20))
        
        for i in range(1, 6):
            if i < 5:
                step_color = '#00aa00'
                step_text = '✓'
            else:
                step_color = '#0066cc'
                step_text = str(i)
            
            step_label = tk.Label(steps_frame, text=step_text,
                                 font=('Segoe UI', 12, 'bold'),
                                 fg='white', bg=step_color,
                                 width=4, height=2)
            step_label.pack(side='left', padx=5)
        
        # Контент
        info_frame = tk.Frame(self.step5_frame, bg='#141414')
        info_frame.pack(pady=20, padx=40, fill='both', expand=True)
        
        # Иконка успеха
        success_label = tk.Label(info_frame, text="[✅]",
                                font=('Segoe UI', 48, 'bold'),
                                fg='#00aa00', bg='#141414')
        success_label.pack(pady=20)
        
        title = tk.Label(info_frame, text="[🎉] Установка завершена!",
                        font=('Segoe UI', 18, 'bold'),
                        fg='#0066cc', bg='#141414')
        title.pack(pady=(0, 20))
        
        texts = [
            "Все файлы модификации успешно установлены!",
            "Спасибо за установку нашей модификации CS:GO!",
            "Теперь вы можете наслаждаться всеми преимуществами новой модификации."
        ]
        
        for text in texts:
            label = tk.Label(info_frame, text=text,
                           font=('Segoe UI', 11),
                           fg='#cccccc', bg='#141414',
                           wraplength=600)
            label.pack(pady=5)
        
        # Кнопка
        buttons_frame = tk.Frame(self.step5_frame, bg='#141414')
        buttons_frame.pack(pady=30)
        
        close_btn = self.create_button(buttons_frame, "Закрыть установщик", self.close_installer, 'primary')
        close_btn.pack()
    
    def create_button(self, parent, text, command, btn_type='primary'):
        """Создание стилизованной кнопки"""
        if btn_type == 'primary':
            btn = tk.Button(parent, text=text, command=command,
                           font=('Segoe UI', 11, 'bold'),
                           bg='#0066cc', fg='white',
                           activebackground='#0052a3',
                           activeforeground='white',
                           relief='flat', bd=0,
                           padx=30, pady=12,
                           cursor='hand2')
        else:
            btn = tk.Button(parent, text=text, command=command,
                           font=('Segoe UI', 11, 'bold'),
                           bg='white', fg='#333333',
                           activebackground='#f0f0f0',
                           activeforeground='#333333',
                           relief='flat', bd=0,
                           padx=30, pady=12,
                           cursor='hand2')
        
        return btn
    
    def show_step(self, step_number):
        """Показать указанный шаг"""
        # Скрыть все шаги
        for i in range(1, 6):
            getattr(self, f'step{i}_frame').pack_forget()
        
        # Показать нужный шаг
        getattr(self, f'step{step_number}_frame').pack(fill='both', expand=True)
        self.current_step = step_number
        
        # Если это шаг 3, начинаем установку
        if step_number == 3 and not self.installation_running:
            self.installation_running = True
            threading.Thread(target=self.start_installation_process, daemon=True).start()
    
    def start_installation(self):
        """Начать установку"""
        self.show_step(2)
    
    def browse_path(self):
        """Выбрать путь установки"""
        path = filedialog.askdirectory(initialdir=self.install_path.get())
        if path:
            self.install_path.set(path)
    
    def open_telegram(self):
        """Открыть канал разработчика"""
        import webbrowser
        webbrowser.open('https://t.me/your_channel')
    
    def start_installation_process(self):
        """Процесс установки в отдельном потоке"""
        files = [
            "[📦] Загрузка основных файлов модификации...",
            "[🎨] Установка текстур и моделей...",
            "[🔊] Настройка звуковых файлов...",
            "[⚙️] Конфигурация игровых параметров...",
            "[📝] Обновление конфигурационных файлов...",
            "[🔍] Проверка целостности файлов...",
            "[🎮] Интеграция с игрой...",
            "[✅] Завершение установки..."
        ]
        
        for i, file_msg in enumerate(files):
            progress = (i + 1) * 12.5
            
            # Обновляем прогресс-бар
            self.installation_progress.set(progress)
            self.progress_label.config(text=f"{int(progress)}%")
            
            # Обновляем статус
            if progress < 25:
                status = "Загрузка файлов..."
            elif progress < 50:
                status = "Установка компонентов..."
            elif progress < 75:
                status = "Настройка модификации..."
            else:
                status = "Завершение установки..."
            
            self.status_label.config(text=status)
            
            # Добавляем файл в список
            self.files_text.config(state='normal')
            self.files_text.insert('end', f"{file_msg}\n")
            self.files_text.see('end')
            self.files_text.config(state='disabled')
            
            # Симуляция времени установки
            time.sleep(1.5)
        
        # Завершение установки
        self.installation_progress.set(100)
        self.progress_label.config(text="100%")
        self.status_label.config(text="Установка завершена!")
        
        self.files_text.config(state='normal')
        self.files_text.insert('end', "[🎉] Все файлы успешно установлены!\n")
        self.files_text.config(state='disabled')
        
        # Активируем кнопку "Готово"
        self.complete_btn.config(state='normal')
        
        # Здесь можно добавить реальную логику копирования файлов
        self.copy_modification_files()
    
    def copy_modification_files(self):
        """Реальное копирование файлов модификации"""
        try:
            install_path = self.install_path.get()
            if os.path.exists(install_path):
                # Здесь можно добавить логику копирования файлов
                # Например, копировать файлы из папки с модификацией в папку игры
                pass
        except Exception as e:
            print(f"Ошибка при копировании файлов: {e}")
    
    def close_installer(self):
        """Закрыть установщик"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите закрыть установщик?"):
            self.root.quit()

def main():
    root = tk.Tk()
    app = CS GOInstaller(root)
    root.mainloop()

if __name__ == "__main__":
    main()
