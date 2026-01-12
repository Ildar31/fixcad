import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext, Menu
import json
import re
import os
import webbrowser
from tkinter import filedialog
import sys
import subprocess
import shutil

class ProductManager:
    def __init__(self, root):
        self.root = root
        self.root.title("FIXCAD MARKET - Менеджер товаров")
        self.root.geometry("1200x700")
        
        # Устанавливаем минимальный размер окна (нельзя уменьшить)
        self.root.minsize(1200, 700)
        
        self.bg_color = "#f0f0f0"
        self.frame_bg = "#ffffff"
        self.accent_color = "#667eea"
        self.secondary_color = "#764ba2"
        
        self.root.configure(bg=self.bg_color)
        
        # Делаем колонки и строки растягиваемыми
        self.root.grid_rowconfigure(0, weight=1)
        self.root.grid_columnconfigure(0, weight=1)
        
        self.products_js_path = "products.js"
        self.server_js_path = "server.js"
        self.products_data = {}
        self.server_products = {}
        
        # Добавляем список для хранения удаленных товаров
        self.deleted_products = set()
        
        # Создаем контекстное меню
        self.context_menu = Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_text)
        self.context_menu.add_command(label="Вставить", command=self.paste_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Вырезать", command=self.cut_text)
        
        self.setup_ui()
        self.load_data()
        
        # Привязываем контекстное меню ко всему окну
        self.root.bind("<Button-3>", self.show_context_menu)
        
    def setup_ui(self):
        main_container = tk.Frame(self.root, bg=self.bg_color)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Делаем main_container растягиваемым
        main_container.grid_rowconfigure(1, weight=1)
        main_container.grid_columnconfigure(0, weight=1)
        
        top_frame = tk.Frame(main_container, bg=self.bg_color)
        top_frame.pack(fill=tk.X, pady=(0, 10))
        
        tk.Button(top_frame, text="🔄 Обновить данные", command=self.load_data,
                 bg=self.accent_color, fg="white", padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="➕ Добавить товар", command=self.add_product,
                 bg="#4CAF50", fg="white", padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="💾 Сохранить все", command=self.save_all,
                 bg="#2196F3", fg="white", padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        tk.Button(top_frame, text="📋 Инструкция", command=self.show_instructions,
                 bg="#FF9800", fg="white", padx=15, pady=5).pack(side=tk.LEFT, padx=5)
        
        content_frame = tk.Frame(main_container, bg=self.bg_color)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # Делаем content_frame растягиваемым
        content_frame.grid_rowconfigure(0, weight=1)
        content_frame.grid_columnconfigure(1, weight=1)
        
        left_frame = tk.Frame(content_frame, bg=self.frame_bg, relief=tk.RAISED, borderwidth=1)
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, padx=(0, 10))
        
        # Делаем left_frame растягиваемым по высоте
        left_frame.grid_rowconfigure(2, weight=1)
        left_frame.grid_columnconfigure(0, weight=1)
        
        tk.Label(left_frame, text="📦 Товары", font=("Arial", 12, "bold"),
                bg=self.frame_bg).pack(pady=10)
        
        list_controls = tk.Frame(left_frame, bg=self.frame_bg)
        list_controls.pack(fill=tk.X, padx=10, pady=5)
        
        tk.Button(list_controls, text="⬆️", command=self.move_up, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(list_controls, text="⬇️", command=self.move_down, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(list_controls, text="📋", command=self.duplicate_product, width=3).pack(side=tk.LEFT, padx=2)
        tk.Button(list_controls, text="🗑️", command=self.delete_product, width=3).pack(side=tk.LEFT, padx=2)
        
        self.products_listbox = tk.Listbox(left_frame, font=("Arial", 10), selectmode=tk.SINGLE)
        self.products_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.products_listbox.bind('<<ListboxSelect>>', self.on_product_select)
        
        # Привязываем контекстное меню к Listbox
        self.products_listbox.bind("<Button-3>", self.show_context_menu)
        
        right_frame = tk.Frame(content_frame, bg=self.frame_bg, relief=tk.RAISED, borderwidth=1)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        tk.Label(right_frame, text="✏️ Редактирование товара", font=("Arial", 12, "bold"),
                bg=self.frame_bg).pack(pady=10)
        
        self.notebook = ttk.Notebook(right_frame)
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        self.basic_frame = tk.Frame(self.notebook, bg=self.frame_bg)
        self.notebook.add(self.basic_frame, text="Основные")
        self.create_basic_tab()
        
        self.files_frame = tk.Frame(self.notebook, bg=self.frame_bg)
        self.notebook.add(self.files_frame, text="Файлы")
        self.create_files_tab()
        
        self.advanced_frame = tk.Frame(self.notebook, bg=self.frame_bg)
        self.notebook.add(self.advanced_frame, text="Дополнительно")
        self.create_advanced_tab()
        
        # Кнопка сохранения текущего товара
        save_btn = tk.Button(right_frame, text="💾 Сохранить товар", 
                           command=self.save_product,
                           bg="#4CAF50", fg="white", padx=15, pady=5)
        save_btn.pack(pady=10)
        
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = tk.Label(self.root, textvariable=self.status_var,
                            bg=self.accent_color, fg="white", anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        
    def create_basic_tab(self):
        frame = self.basic_frame
        
        # Делаем колонки растягиваемыми
        frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(frame, text="ID товара:", bg=self.frame_bg).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.product_id_var = tk.StringVar()
        self.product_id_entry = tk.Entry(frame, textvariable=self.product_id_var)
        self.product_id_entry.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)
        
        # Привязываем контекстное меню к полям ввода
        self.product_id_entry.bind("<Button-3>", self.show_context_menu)
        
        tk.Label(frame, text="Название:", bg=self.frame_bg).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.name_var = tk.StringVar()
        self.name_entry = tk.Entry(frame, textvariable=self.name_var)
        self.name_entry.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)
        self.name_entry.bind("<Button-3>", self.show_context_menu)
        
        tk.Label(frame, text="Описание:", bg=self.frame_bg).grid(row=2, column=0, sticky=tk.NW, padx=10, pady=5)
        self.desc_text = tk.Text(frame, height=4, wrap=tk.WORD)  # Добавлен перенос слов
        self.desc_text.grid(row=2, column=1, sticky=tk.NSEW, padx=10, pady=5)
        self.desc_text.bind("<Button-3>", self.show_context_menu)
        
        # Делаем строку с текстом растягиваемой
        frame.grid_rowconfigure(2, weight=1)
        
        tk.Label(frame, text="Изображение:", bg=self.frame_bg).grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        image_frame = tk.Frame(frame, bg=self.frame_bg)
        image_frame.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=5)
        image_frame.grid_columnconfigure(0, weight=1)
        self.image_var = tk.StringVar()
        self.image_entry = tk.Entry(image_frame, textvariable=self.image_var)
        self.image_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.image_entry.bind("<Button-3>", self.show_context_menu)
        tk.Button(image_frame, text="📁", command=self.browse_image, width=3).pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame, text="3D модель:", bg=self.frame_bg).grid(row=4, column=0, sticky=tk.W, padx=10, pady=5)
        model_frame = tk.Frame(frame, bg=self.frame_bg)
        model_frame.grid(row=4, column=1, sticky=tk.EW, padx=10, pady=5)
        model_frame.grid_columnconfigure(0, weight=1)
        self.model_var = tk.StringVar()
        self.model_entry = tk.Entry(model_frame, textvariable=self.model_var)
        self.model_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        self.model_entry.bind("<Button-3>", self.show_context_menu)
        tk.Button(model_frame, text="📁", command=self.browse_model, width=3).pack(side=tk.LEFT, padx=5)
        tk.Button(model_frame, text="❌", command=lambda: self.model_var.set(""), width=3).pack(side=tk.LEFT, padx=5)
        
        tk.Label(frame, text="Бейдж формата:", bg=self.frame_bg).grid(row=5, column=0, sticky=tk.W, padx=10, pady=5)
        self.format_var = tk.StringVar()
        self.format_combo = ttk.Combobox(frame, textvariable=self.format_var, 
                                        values=["CDW", "SPW", "A3D", "M3D", "STL", "STEP", "TXT"])
        self.format_combo.grid(row=5, column=1, sticky=tk.EW, padx=10, pady=5)
        self.format_combo.bind("<Button-3>", self.show_context_menu)
        
    def create_files_tab(self):
        frame = self.files_frame
        
        # Делаем колонки растягиваемыми
        frame.grid_columnconfigure(1, weight=1)
        
        tk.Label(frame, text="Ссылка на Яндекс.Диск:", bg=self.frame_bg).grid(row=0, column=0, sticky=tk.W, padx=10, pady=5)
        self.zip_url_var = tk.StringVar()
        self.zip_url_entry = tk.Entry(frame, textvariable=self.zip_url_var)
        self.zip_url_entry.grid(row=0, column=1, sticky=tk.EW, padx=10, pady=5)
        self.zip_url_entry.bind("<Button-3>", self.show_context_menu)
        
        tk.Label(frame, text="Имя архива:", bg=self.frame_bg).grid(row=1, column=0, sticky=tk.W, padx=10, pady=5)
        self.zip_name_var = tk.StringVar()
        self.zip_name_entry = tk.Entry(frame, textvariable=self.zip_name_var)
        self.zip_name_entry.grid(row=1, column=1, sticky=tk.EW, padx=10, pady=5)
        self.zip_name_entry.bind("<Button-3>", self.show_context_menu)
        
        tk.Label(frame, text="Ссылка на оплату (ЮMoney):", bg=self.frame_bg).grid(row=2, column=0, sticky=tk.W, padx=10, pady=5)
        self.payment_url_var = tk.StringVar()
        self.payment_url_entry = tk.Entry(frame, textvariable=self.payment_url_var)
        self.payment_url_entry.grid(row=2, column=1, sticky=tk.EW, padx=10, pady=5)
        self.payment_url_entry.bind("<Button-3>", self.show_context_menu)
        
        tk.Label(frame, text="Форматы файлов:", bg=self.frame_bg).grid(row=3, column=0, sticky=tk.W, padx=10, pady=5)
        self.formats_var = tk.StringVar()
        self.formats_entry = tk.Entry(frame, textvariable=self.formats_var)
        self.formats_entry.grid(row=3, column=1, sticky=tk.EW, padx=10, pady=5)
        self.formats_entry.bind("<Button-3>", self.show_context_menu)
        
    def create_advanced_tab(self):
        frame = self.advanced_frame
        
        # Делаем колонки и строки растягиваемыми
        frame.grid_columnconfigure(1, weight=1)
        frame.grid_rowconfigure(0, weight=1)
        frame.grid_rowconfigure(1, weight=1)
        
        tk.Label(frame, text="Особенности товара:", bg=self.frame_bg).grid(row=0, column=0, sticky=tk.NW, padx=10, pady=5)
        self.features_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)  # Добавлен перенос слов
        self.features_text.grid(row=0, column=1, sticky=tk.NSEW, padx=10, pady=5)
        self.features_text.bind("<Button-3>", self.show_context_menu)
        
        tk.Label(frame, text="Содержимое архива:", bg=self.frame_bg).grid(row=1, column=0, sticky=tk.NW, padx=10, pady=5)
        self.contents_text = scrolledtext.ScrolledText(frame, wrap=tk.WORD)  # Добавлен перенос слов
        self.contents_text.grid(row=1, column=1, sticky=tk.NSEW, padx=10, pady=5)
        self.contents_text.bind("<Button-3>", self.show_context_menu)
        
        tk.Button(frame, text="🔄 Сгенерировать содержимое",
                 command=self.generate_contents,
                 bg=self.accent_color, fg="white").grid(row=2, column=1, sticky=tk.W, padx=10, pady=5)
        
    def show_context_menu(self, event):
        """Показывает контекстное меню для активного виджета"""
        try:
            # Получаем виджет, на котором был клик
            widget = event.widget
            
            # Устанавливаем фокус на виджет
            widget.focus_set()
            
            # Для Text виджетов нужно обеспечить выделение текста
            if isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
                # Получаем позицию клика
                index = widget.index(f"@{event.x},{event.y}")
                
                # Проверяем, есть ли выделение
                try:
                    if widget.selection_get():
                        # Текст уже выделен, ничего не делаем
                        pass
                    else:
                        # Если нет выделения, помещаем курсор в позицию клика
                        widget.mark_set(tk.INSERT, index)
                        widget.see(tk.INSERT)
                except tk.TclError:
                    # Нет выделения
                    pass
            
            # Показываем меню и ждем
            self.context_menu.post(event.x_root, event.y_root)
            
            # Ждем, пока меню не будет закрыто
            self.root.wait_window(self.context_menu)
            
        finally:
            # Гарантируем, что меню будет скрыто
            self.context_menu.unpost()
            
    def copy_text(self):
        """Копирует выделенный текст"""
        widget = self.root.focus_get()
        
        if isinstance(widget, (tk.Entry, ttk.Combobox)):
            # Для Entry и Combobox
            if widget.select_present():
                self.root.clipboard_clear()
                self.root.clipboard_append(widget.selection_get())
                
        elif isinstance(widget, tk.Listbox):
            # Для Listbox
            if widget.curselection():
                self.root.clipboard_clear()
                self.root.clipboard_append(widget.get(widget.curselection()))
                
        elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            # Для Text и ScrolledText
            try:
                selected_text = widget.selection_get()
                if selected_text:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(selected_text)
            except tk.TclError:
                # Нет выделения
                pass
                
    def paste_text(self):
        """Вставляет текст из буфера обмена"""
        widget = self.root.focus_get()
        clipboard_text = self.root.clipboard_get()
        
        if not clipboard_text:
            return
            
        if isinstance(widget, tk.Entry):
            # Для Entry
            if widget.select_present():
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            widget.insert(tk.INSERT, clipboard_text)
            
        elif isinstance(widget, ttk.Combobox):
            # Для Combobox
            widget.delete(0, tk.END)
            widget.insert(0, clipboard_text)
            
        elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            # Для Text и ScrolledText
            try:
                if widget.selection_get():
                    # Удаляем выделенный текст
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                pass
            widget.insert(tk.INSERT, clipboard_text)
            
    def cut_text(self):
        """Вырезает выделенный текст"""
        widget = self.root.focus_get()
        
        if isinstance(widget, tk.Entry):
            # Для Entry
            if widget.select_present():
                self.root.clipboard_clear()
                self.root.clipboard_append(widget.selection_get())
                widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
                
        elif isinstance(widget, (tk.Text, scrolledtext.ScrolledText)):
            # Для Text и ScrolledText
            try:
                selected_text = widget.selection_get()
                if selected_text:
                    self.root.clipboard_clear()
                    self.root.clipboard_append(selected_text)
                    widget.delete(tk.SEL_FIRST, tk.SEL_LAST)
            except tk.TclError:
                # Нет выделения
                pass
    
    def browse_image(self):
        filename = filedialog.askopenfilename(
            title="Выберите изображение",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif"), ("All files", "*.*")]
        )
        if filename:
            dest = os.path.join("images", os.path.basename(filename))
            if not os.path.exists("images"):
                os.makedirs("images")
            try:
                shutil.copy2(filename, dest)
                self.image_var.set(f"images/{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось скопировать файл: {str(e)}")
            
    def browse_model(self):
        filename = filedialog.askopenfilename(
            title="Выберите 3D модель",
            filetypes=[("STL files", "*.stl"), ("All files", "*.*")]
        )
        if filename:
            dest = os.path.join("models", os.path.basename(filename))
            if not os.path.exists("models"):
                os.makedirs("models")
            try:
                shutil.copy2(filename, dest)
                self.model_var.set(f"models/{os.path.basename(filename)}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось скопировать файл: {str(e)}")
    
    def load_data(self):
        try:
            print("=" * 60)
            print("ЗАГРУЗКА ДАННЫХ")
            print("=" * 60)
            
            # Очищаем список удаленных товаров при загрузке
            self.deleted_products.clear()
            
            # Загружаем products.js с помощью eval
            with open(self.products_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            print(f"📄 Прочитан products.js ({len(content)} символов)")
            
            # Извлекаем объект PRODUCTS_DATA
            match = re.search(r'const PRODUCTS_DATA\s*=\s*({.*?});', content, re.DOTALL)
            if match:
                js_data = match.group(1)
                print(f"🔍 Найден объект PRODUCTS_DATA ({len(js_data)} символов)")
                
                # Используем безопасный eval
                self.products_data = self.safe_eval_js_object(js_data)
                print(f"✅ Загружено {len(self.products_data)} товаров из products.js")
                
                # Отладочный вывод
                for product_id, product_data in self.products_data.items():
                    print(f"\n📦 {product_id}:")
                    for key, value in product_data.items():
                        if isinstance(value, list):
                            print(f"  {key}: список из {len(value)} элементов: {value}")
                        else:
                            print(f"  {key}: {value}")
            
            # Загружаем server.js
            with open(self.server_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            print(f"\n📄 Прочитан server.js ({len(content)} символов)")
            
            # Извлекаем объект PRODUCTS
            match = re.search(r'const PRODUCTS\s*=\s*({.*?});', content, re.DOTALL)
            if match:
                js_data = match.group(1)
                print(f"🔍 Найден объект PRODUCTS ({len(js_data)} символов)")
                
                # Используем безопасный eval
                self.server_products = self.safe_eval_js_object(js_data)
                print(f"✅ Загружено {len(self.server_products)} товаров из server.js")
            
            # Обновляем список
            self.update_products_list()
            self.status_var.set(f"Загружено {len(self.products_data)} товаров")
            print(f"\n🎉 Загрузка завершена успешно!")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Ошибка при загрузке данных: {error_details}")
            messagebox.showerror("Ошибка", f"Не удалось загрузить данные:\n{str(e)}")
    
    def safe_eval_js_object(self, js_string):
        """Безопасный eval для JS объектов"""
        # Очищаем строку
        js_string = js_string.strip()
        
        # Заменяем JS значения на Python
        js_string = js_string.replace('null', 'None')
        js_string = js_string.replace('true', 'True')
        js_string = js_string.replace('false', 'False')
        
        # Убираем trailing commas
        js_string = re.sub(r',\s*}', '}', js_string)
        js_string = re.sub(r',\s*]', ']', js_string)
        
        # Обработка строк с экранированными кавычками
        # Сначала находим все строки в кавычках и временно заменяем их
        strings = []
        def replace_string(match):
            strings.append(match.group(0))
            return f'__STRING_{len(strings)-1}__'
        
        # Заменяем строкы в одинарных и двойных кавычках
        js_string = re.sub(r"'([^'\\]*(?:\\.[^'\\]*)*)'", replace_string, js_string)
        js_string = re.sub(r'"([^"\\]*(?:\\.[^"\\]*)*)"', replace_string, js_string)
        
        # Теперь заменяем ключи без кавычек (имена свойств JS объектов)
        # Находим паттерны: ключ: (где ключ без кавычек)
        pattern = r'([a-zA-Z_$][a-zA-Z0-9_$]*)\s*:'
        
        def add_quotes_to_key(match):
            key = match.group(1)
            return f'"{key}":'
        
        js_string = re.sub(pattern, add_quotes_to_key, js_string)
        
        # Восстанавливаем строки
        for i, string in enumerate(strings):
            js_string = js_string.replace(f'__STRING_{i}__', string)
        
        # Пробуем eval
        try:
            result = eval(js_string)
            return result
        except Exception as e:
            print(f"❌ Ошибка eval: {e}")
            print(f"📝 Очищенная строка (первые 500 символов): {js_string[:500]}")
            
            # Если не сработало, пробуем ручной парсинг
            return self.parse_js_object_manually(js_string)
    
    def parse_js_object_manually(self, js_string):
        """Ручной парсинг JS объекта"""
        result = {}
        
        # Убираем внешние фигурные скобки
        js_string = js_string.strip()
        if js_string.startswith('{'):
            js_string = js_string[1:].rstrip('}')
        
        # Разбиваем на товары
        # Ищем паттерн: "ключ": {
        pattern = r'"([a-zA-Z0-9_]+)"\s*:\s*\{'
        matches = list(re.finditer(pattern, js_string))
        
        for i, match in enumerate(matches):
            product_id = match.group(1)
            start_pos = match.start()
            
            # Находим конец объекта
            end_pos = len(js_string)
            if i < len(matches) - 1:
                end_pos = matches[i + 1].start()
            
            obj_str = js_string[start_pos:end_pos]
            
            # Парсим объект товара
            product_data = self.parse_product_object(obj_str)
            if product_data:
                result[product_id] = product_data
        
        return result
    
    def parse_product_object(self, obj_str):
        """Парсит объект товара"""
        result = {}
        
        # Убираем "ключ": в начале
        colon_pos = obj_str.find(':')
        if colon_pos != -1:
            obj_str = obj_str[colon_pos + 1:].strip()
        
        # Убираем внешние фигурные скобки
        if obj_str.startswith('{'):
            obj_str = obj_str[1:].rstrip('}')
        
        # Разбиваем на строки
        lines = [line.strip() for line in obj_str.split('\n') if line.strip()]
        
        current_key = None
        current_value = []
        in_array = False
        array_depth = 0
        
        for line in lines:
            if not line:
                continue
            
            # Если мы внутри массива
            if in_array:
                current_value.append(line)
                array_depth += line.count('[') - line.count(']')
                
                if array_depth == 0 and (line.endswith('],') or line.endswith(']')):
                    # Завершаем массив
                    array_str = '\n'.join(current_value)
                    parsed_array = self.parse_js_array(array_str)
                    result[current_key] = parsed_array
                    in_array = False
                    current_key = None
                    current_value = []
                continue
            
            # Ищем ключ: значение
            if ':' in line:
                # Находим позицию первого двоеточия вне строки
                in_string = False
                string_char = None
                colon_pos = -1
                
                for i, char in enumerate(line):
                    if char in ['"', "'"] and (not in_string or char == string_char):
                        in_string = not in_string
                        if in_string:
                            string_char = char
                        else:
                            string_char = None
                    elif char == ':' and not in_string:
                        colon_pos = i
                        break
                
                if colon_pos != -1:
                    key = line[:colon_pos].strip()
                    value = line[colon_pos + 1:].strip()
                    
                    # Убираем кавычки с ключа
                    if (key.startswith('"') and key.endswith('"')) or (key.startswith("'") and key.endswith("'")):
                        key = key[1:-1]
                    
                    # Проверяем, является ли значение массивом
                    if value.startswith('['):
                        in_array = True
                        array_depth = 1
                        current_key = key
                        current_value = [value]
                    else:
                        # Простое значение
                        value = self.parse_js_value(value.rstrip(','))
                        result[key] = value
        
        return result
    
    def parse_js_value(self, value_str):
        """Парсит JS значение"""
        value_str = value_str.strip().rstrip(',')
        
        if value_str == 'None':
            return None
        elif value_str == 'True':
            return True
        elif value_str == 'False':
            return False
        elif (value_str.startswith("'") and value_str.endswith("'")):
            return value_str[1:-1]
        elif (value_str.startswith('"') and value_str.endswith('"')):
            return value_str[1:-1]
        else:
            # Пробуем как число
            try:
                return float(value_str) if '.' in value_str else int(value_str)
            except:
                return value_str
    
    def parse_js_array(self, array_str):
        """Парсит JS массив"""
        array_str = array_str.strip()
        if not array_str.startswith('[') or not array_str.endswith(']'):
            return []
        
        # Убираем скобки
        array_str = array_str[1:-1].strip()
        if not array_str:
            return []
        
        items = []
        current_item = ""
        in_string = False
        string_char = None
        brace_depth = 0
        bracket_depth = 0
        
        for char in array_str:
            if char in ['"', "'"] and (not in_string or char == string_char):
                in_string = not in_string
                if in_string:
                    string_char = char
                else:
                    string_char = None
                current_item += char
            elif char == '{':
                brace_depth += 1
                current_item += char
            elif char == '}':
                brace_depth -= 1
                current_item += char
            elif char == '[':
                bracket_depth += 1
                current_item += char
            elif char == ']':
                bracket_depth -= 1
                current_item += char
            elif char == ',' and not in_string and brace_depth == 0 and bracket_depth == 0:
                if current_item.strip():
                    items.append(self.parse_js_value(current_item.strip()))
                current_item = ""
            else:
                current_item += char
        
        if current_item.strip():
            items.append(self.parse_js_value(current_item.strip()))
        
        return items
    
    def update_products_list(self):
        """Обновляет список товаров"""
        self.products_listbox.delete(0, tk.END)
        
        if not isinstance(self.products_data, dict):
            print("❌ Ошибка: products_data не является словарем")
            return
        
        for product_id, product_data in self.products_data.items():
            if not isinstance(product_data, dict):
                print(f"❌ Ошибка: данные товара {product_id} не являются словарем")
                continue
                
            name = product_data.get('name', 'Без названия')
            self.products_listbox.insert(tk.END, f"{product_id}: {name[:50]}...")
    
    def on_product_select(self, event):
        selection = self.products_listbox.curselection()
        if not selection:
            return
            
        product_id = self.products_listbox.get(selection[0]).split(":")[0].strip()
        self.load_product_data(product_id)
    
    def load_product_data(self, product_id):
        """Загружает данные выбранного товара"""
        print(f"\n📥 Загружаем данные товара: {product_id}")
        
        if product_id in self.products_data:
            product = self.products_data[product_id]
            server_product = self.server_products.get(product_id, {})
            
            if not isinstance(product, dict):
                print(f"❌ Ошибка: product не словарь для {product_id}")
                return
            if not isinstance(server_product, dict):
                server_product = {}
            
            # Отладочный вывод ВСЕХ полей
            print(f"📊 Данные из products.js для {product_id}:")
            for key, value in product.items():
                print(f"  {key}: {value}")
            
            print(f"\n📊 Данные из server.js для {product_id}:")
            for key, value in server_product.items():
                print(f"  {key}: {value}")
            
            # Основные параметры
            self.product_id_var.set(product_id)
            self.name_var.set(product.get('name', ''))
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(1.0, product.get('description', ''))
            self.image_var.set(product.get('image', ''))
            self.model_var.set(product.get('model', ''))
            self.format_var.set(product.get('formatBadge', ''))
            
            # Файлы и ссылки
            self.zip_url_var.set(server_product.get('zipUrl', ''))
            self.zip_name_var.set(server_product.get('zipName', ''))
            
            # Ссылка на оплату и форматы
            self.payment_url_var.set(product.get('paymentUrl', ''))
            
            # Форматы
            formats = product.get('formats', [])
            if isinstance(formats, list):
                self.formats_var.set(', '.join(formats))
            else:
                self.formats_var.set(str(formats))
            
            # Особенности
            self.features_text.delete(1.0, tk.END)
            features = product.get('features', [])
            if isinstance(features, list):
                cleaned_features = []
                for feature in features:
                    if isinstance(feature, str):
                        feature = feature.strip()
                        cleaned_features.append(feature)
                self.features_text.insert(1.0, '\n'.join(cleaned_features))
            elif features:
                self.features_text.insert(1.0, str(features))
            
            # Содержимое архива
            self.contents_text.delete(1.0, tk.END)
            contents = server_product.get('contents', [])
            if isinstance(contents, list):
                cleaned_contents = []
                for content in contents:
                    if isinstance(content, str):
                        content = content.strip()
                        cleaned_contents.append(content)
                self.contents_text.insert(1.0, '\n'.join(cleaned_contents))
            elif contents:
                self.contents_text.insert(1.0, str(contents))
            
            print(f"✅ Данные товара {product_id} загружены в интерфейс")
    
    def save_product(self):
        """Сохраняет текущий товар (без записи в файлы)"""
        product_id = self.product_id_var.get().strip()
        if not product_id:
            messagebox.showwarning("Внимание", "Введите ID товара!")
            return
            
        if not re.match(r'^[a-zA-Z0-9_]+$', product_id):
            messagebox.showwarning("Внимание", "ID должен содержать только латинские буквы, цифры и подчеркивания!")
            return
            
        # Обновляем products.js данные
        self.products_data[product_id] = {
            'name': self.name_var.get().strip(),
            'description': self.desc_text.get(1.0, tk.END).strip(),
            'image': self.image_var.get().strip(),
            'model': self.model_var.get().strip(),
            'formatBadge': self.format_var.get().strip(),
            'formats': [f.strip() for f in self.formats_var.get().split(',') if f.strip()],
            'features': [f.strip() for f in self.features_text.get(1.0, tk.END).strip().split('\n') if f.strip()],
            'paymentUrl': self.payment_url_var.get().strip()
        }
        
        # Обновляем server.js данные
        self.server_products[product_id] = {
            'name': self.name_var.get().strip(),
            'description': self.desc_text.get(1.0, tk.END).strip(),
            'zipUrl': self.zip_url_var.get().strip(),
            'zipName': self.zip_name_var.get().strip(),
            'contents': [c.strip() for c in self.contents_text.get(1.0, tk.END).strip().split('\n') if c.strip()]
        }
        
        self.update_products_list()
        self.status_var.set(f"Товар '{product_id}' сохранен в памяти")
        
        # Находим и выделяем сохраненный товар в списке
        for i in range(self.products_listbox.size()):
            if self.products_listbox.get(i).startswith(product_id + ":"):
                self.products_listbox.selection_clear(0, tk.END)
                self.products_listbox.selection_set(i)
                self.products_listbox.see(i)
                break
    
    def add_product(self):
        # Сбрасываем поля
        self.product_id_var.set("")
        self.name_var.set("")
        self.desc_text.delete(1.0, tk.END)
        self.image_var.set("")
        self.model_var.set("")
        self.format_var.set("CDW")
        self.zip_url_var.set("")
        self.zip_name_var.set("")
        self.payment_url_var.set("")
        self.formats_var.set("")
        self.features_text.delete(1.0, tk.END)
        self.contents_text.delete(1.0, tk.END)
        
        base_id = "new_product"
        counter = 1
        while f"{base_id}_{counter}" in self.products_data:
            counter += 1
        new_id = f"{base_id}_{counter}"
        self.product_id_var.set(new_id)
        
        # Заполняем значения по умолчанию для нового товара
        self.name_var.set(f"Новый товар {counter}")
        self.desc_text.insert(1.0, "Описание нового товара")
        self.image_var.set("images/default.jpg")
        self.zip_url_var.set("https://disk.yandex.ru/d/...")
        self.zip_name_var.set(f"product_{counter}.zip")
        self.payment_url_var.set("https://yoomoney.ru/...")
        self.formats_var.set("CDW, PDF, DWG")
        
        # Сохраняем новый товар в памяти
        self.save_product()
        
        # Фокусируемся на поле названия
        self.name_entry.focus()
        self.name_entry.select_range(0, tk.END)
        
        self.status_var.set(f"Создан новый товар: {new_id}")
    
    def duplicate_product(self):
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар для дублирования!")
            return
            
        old_id = self.products_listbox.get(selection[0]).split(":")[0].strip()
        
        base_id = old_id + "_copy"
        counter = 1
        while f"{base_id}_{counter}" in self.products_data:
            counter += 1
        new_id = f"{base_id}_{counter}"
        
        if old_id in self.products_data:
            # Глубокое копирование данных
            import copy
            self.products_data[new_id] = copy.deepcopy(self.products_data[old_id])
            self.products_data[new_id]['name'] = f"Копия: {self.products_data[new_id]['name']}"
            
        if old_id in self.server_products:
            self.server_products[new_id] = copy.deepcopy(self.server_products[old_id])
            self.server_products[new_id]['name'] = f"Копия: {self.server_products[new_id]['name']}"
        
        self.update_products_list()
        self.load_product_data(new_id)
        self.status_var.set(f"Товар '{old_id}' дублирован как '{new_id}'")
    
    def delete_product(self):
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар для удаления!")
            return
            
        product_id = self.products_listbox.get(selection[0]).split(":")[0].strip()
        
        if messagebox.askyesno("Подтверждение", f"Вы уверены, что хотите удалить товар '{product_id}'?"):
            # Добавляем товар в список удаленных
            self.deleted_products.add(product_id)
            
            # Удаляем из данных в памяти
            if product_id in self.products_data:
                del self.products_data[product_id]
            
            if product_id in self.server_products:
                del self.server_products[product_id]
            
            # Обновляем список
            self.update_products_list()
            
            # Очищаем поля редактирования
            self.product_id_var.set("")
            self.name_var.set("")
            self.desc_text.delete(1.0, tk.END)
            self.image_var.set("")
            self.model_var.set("")
            self.format_var.set("")
            self.zip_url_var.set("")
            self.zip_name_var.set("")
            self.payment_url_var.set("")
            self.formats_var.set("")
            self.features_text.delete(1.0, tk.END)
            self.contents_text.delete(1.0, tk.END)
            
            self.status_var.set(f"Товар '{product_id}' помечен на удаление")
    
    def move_up(self):
        selection = self.products_listbox.curselection()
        if not selection or selection[0] == 0:
            return
            
        idx = selection[0]
        product_id = self.products_listbox.get(idx).split(":")[0].strip()
        
        product_ids = list(self.products_data.keys())
        if product_id in product_ids:
            current_idx = product_ids.index(product_id)
            if current_idx > 0:
                product_ids[current_idx], product_ids[current_idx-1] = product_ids[current_idx-1], product_ids[current_idx]
                
                new_products_data = {}
                new_server_products = {}
                
                for pid in product_ids:
                    if pid in self.products_data:
                        new_products_data[pid] = self.products_data[pid]
                    if pid in self.server_products:
                        new_server_products[pid] = self.server_products[pid]
                
                self.products_data = new_products_data
                self.server_products = new_server_products
                
                self.update_products_list()
                self.products_listbox.selection_set(idx-1)
                self.status_var.set(f"Товар '{product_id}' перемещен вверх")
    
    def move_down(self):
        selection = self.products_listbox.curselection()
        if not selection or selection[0] == self.products_listbox.size() - 1:
            return
            
        idx = selection[0]
        product_id = self.products_listbox.get(idx).split(":")[0].strip()
        
        product_ids = list(self.products_data.keys())
        if product_id in product_ids:
            current_idx = product_ids.index(product_id)
            if current_idx < len(product_ids) - 1:
                product_ids[current_idx], product_ids[current_idx+1] = product_ids[current_idx+1], product_ids[current_idx]
                
                new_products_data = {}
                new_server_products = {}
                
                for pid in product_ids:
                    if pid in self.products_data:
                        new_products_data[pid] = self.products_data[pid]
                    if pid in self.server_products:
                        new_server_products[pid] = self.server_products[pid]
                
                self.products_data = new_products_data
                self.server_products = new_server_products
                
                self.update_products_list()
                self.products_listbox.selection_set(idx+1)
                self.status_var.set(f"Товар '{product_id}' перемещен вниз")
    
    def generate_contents(self):
        features = self.features_text.get(1.0, tk.END).strip().split('\n')
        if features:
            self.contents_text.delete(1.0, tk.END)
            self.contents_text.insert(1.0, '\n'.join(features))
    
    def save_all(self):
        """Сохраняет все изменения в файлы"""
        try:
            # Сначала сохраняем текущий товар (если он редактировался)
            current_id = self.product_id_var.get().strip()
            if current_id and current_id not in self.deleted_products:
                self.save_product()
            
            # Создаем резервные копии
            import datetime
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            
            for filepath in [self.products_js_path, self.server_js_path]:
                if os.path.exists(filepath):
                    backup_path = f"{filepath}.backup_{timestamp}"
                    try:
                        shutil.copy2(filepath, backup_path)
                        print(f"📁 Создана резервная копия: {backup_path}")
                    except Exception as e:
                        print(f"❌ Не удалось создать резервную копию {filepath}: {e}")
            
            # Удаляем товары, помеченные на удаление
            # Фильтруем данные, исключая удаленные товары
            filtered_products_data = {k: v for k, v in self.products_data.items() 
                                     if k not in self.deleted_products}
            filtered_server_products = {k: v for k, v in self.server_products.items() 
                                       if k not in self.deleted_products}
            
            # Очищаем список удаленных после сохранения
            self.deleted_products.clear()
            
            # Сохраняем products.js
            self.save_products_js(filtered_products_data)
            
            # Сохраняем server.js
            self.save_server_js(filtered_server_products)
            
            # Обновляем внутренние данные
            self.products_data = filtered_products_data
            self.server_products = filtered_server_products
            
            # Обновляем список товаров
            self.update_products_list()
            
            self.status_var.set(f"✅ Все изменения сохранены в {len(self.products_data)} товаров")
            messagebox.showinfo("Сохранено", "Все изменения успешно сохранены!\n\nСозданы резервные копии файлов.")
            
        except Exception as e:
            import traceback
            error_details = traceback.format_exc()
            print(f"❌ Ошибка при сохранении: {error_details}")
            messagebox.showerror("Ошибка", f"Не удалось сохранить данные:\n{str(e)}")
    
    def save_products_js(self, products_data):
        """Сохраняет данные в products.js"""
        print("💾 Сохраняем products.js...")
        
        products_js = """// products.js

// Данные товаров для генерации карточек и микроразметки
const PRODUCTS_DATA = {
"""
        
        for i, (product_id, product) in enumerate(products_data.items()):
            products_js += f"    {product_id}: {{\n"
            products_js += f"        name: \"{product['name']}\",\n"
            products_js += f"        description: \"{product['description']}\",\n"
            products_js += f"        image: \"{product['image']}\",\n"
            
            # ИСПРАВЛЕНИЕ: используем null вместо "None" для пустой модели
            if not product['model']:
                products_js += f"        model: null,\n"
            else:
                products_js += f"        model: \"{product['model']}\",\n"
            
            products_js += f"        formatBadge: \"{product['formatBadge']}\",\n"
            products_js += f"        formats: {json.dumps(product['formats'], ensure_ascii=False)},\n"
            products_js += f"        features: {json.dumps(product['features'], ensure_ascii=False)},\n"
            products_js += f"        paymentUrl: '{product['paymentUrl']}'\n"
            products_js += "    }"
            if i < len(products_data) - 1:
                products_js += ","
            products_js += "\n"
        
        products_js += """};

// Функция для генерации HTML карточек товаров
function generateProductsHTML() {
    const productsGrid = document.querySelector('.products-grid');
    if (!productsGrid) return;
    
    let html = '';
    
    for (const [productId, product] of Object.entries(PRODUCTS_DATA)) {
        const hasModel = product.model !== null;
        
        html += `
        <div class="product-card">
            <div class="product-image" data-image="${product.image}" ${hasModel ? `data-model="${product.model}"` : ''} tabindex="0" role="button" aria-label="Просмотр ${product.name}">
                <img src="${product.image}" alt="${product.name}" loading="lazy">
                <div class="format-badge">${product.formatBadge}</div>
                <div class="model-indicator">${hasModel ? '3D просмотр' : 'Изображение'}</div>
            </div>
            <div class="product-title">${product.name}</div>
            <div class="product-description">${product.description}</div>
            <div class="formats-list">
                ${product.formats.map(format => `<span class="format-tag">${format}</span>`).join('')}
            </div>
            <ul class="product-features">
                ${product.features.map(feature => `<li>${feature}</li>`).join('')}
            </ul>
            <button class="buy-button" data-product="${productId}" aria-label="Купить ${product.name} за 100 рублей">
                Купить за 100 руб.
            </button>
        </div>
        `;
    }
    
    productsGrid.innerHTML = html;
}

// Функция для генерации данных для микроразметки
function generateProductStructuredData() {
    const productsData = [];
    
    for (const [productId, product] of Object.entries(PRODUCTS_DATA)) {
        const productMarkup = {
            "@context": "https://schema.org/",
            "@type": "Product",
            "name": product.name,
            "description": product.description,
            "image": `https://fixcad.ru/${product.image}`,
            "offers": {
                "@type": "Offer",
                "price": "100",
                "priceCurrency": "RUB",
                "availability": "https://schema.org/InStock"
            },
            "brand": {
                "@type": "Brand",
                "name": "FIXCAD MARKET"
            }
        };
        productsData.push(productMarkup);
    }
    
    return productsData;
}

// Функция для получения URL оплаты
function getPaymentUrl(productId) {
    return PRODUCTS_DATA[productId]?.paymentUrl || '';
}

// Функция для получения названия товара
function getProductName(productId) {
    return PRODUCTS_DATA[productId]?.name || '';
}

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', function() {
    generateProductsHTML();
    
    // Добавляем микроразметку
    const productsData = generateProductStructuredData();
    productsData.forEach(markup => {
        const script = document.createElement('script');
        script.type = 'application/ld+json';
        script.textContent = JSON.stringify(markup);
        document.head.appendChild(script);
    });
});
"""
        
        with open(self.products_js_path, 'w', encoding='utf-8') as f:
            f.write(products_js)
        print(f"✅ products.js сохранен ({len(products_data)} товаров)")
    
    def save_server_js(self, server_products):
        """Сохраняет данные в server.js"""
        print("💾 Сохраняем server.js...")
        
        with open(self.server_js_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        start_match = re.search(r'const PRODUCTS\s*=\s*\{', content)
        if not start_match:
            messagebox.showerror("Ошибка", "Не найден объект PRODUCTS в server.js")
            return
        
        start_idx = start_match.start()
        text_after_start = content[start_idx:]
        
        brace_count = 0
        end_idx = 0
        
        for i, char in enumerate(text_after_start):
            if char == '{':
                brace_count += 1
            elif char == '}':
                brace_count -= 1
                if brace_count == 0:
                    end_idx = start_idx + i + 1
                    break
        
        if end_idx == 0:
            messagebox.showerror("Ошибка", "Не удалось найти конец объекта PRODUCTS")
            return
        
        new_products = "const PRODUCTS = {\n"
        
        for i, (product_id, product) in enumerate(server_products.items()):
            new_products += f"  {product_id}: {{\n"
            new_products += f"    name: '{product['name']}',\n"
            new_products += f"    description: '{product['description']}',\n"
            new_products += f"    zipUrl: '{product['zipUrl']}',\n"
            new_products += f"    zipName: '{product['zipName']}',\n"
            new_products += f"    contents: {json.dumps(product['contents'], ensure_ascii=False)}\n"
            new_products += "  }"
            if i < len(server_products) - 1:
                new_products += ","
            new_products += "\n"
        
        new_products += "};\n"
        
        new_content = content[:start_idx] + new_products + content[end_idx:]
        
        with open(self.server_js_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ server.js сохранен ({len(server_products)} товаров)")
    
    def show_instructions(self):
        instructions = """
═══════════════════════════════════════════════════════════════
                    ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ
═══════════════════════════════════════════════════════════════

1. 📦 ЗАГРУЗКА ДАННЫХ
   • Нажмите "🔄 Обновить данные"
   • Программа использует улучшенный парсинг JS объектов

2. ➕ ДОБАВЛЕНИЕ ТОВАРА
   • Нажмите "➕ Добавить товар"
   • Автоматически создается товар с заполненными полями по умолчанию
   • Отредактируйте поля и сохраните

3. ✏️ РЕДАКТИРОВАНИЕ ТОВАРА
   • Основные: название, описание, изображение, 3D модель
   • Файлы: ВСЕ ссылки и форматы файлов
   • Дополнительно: особенности и содержимое архива

4. 📋 КОНТЕКСТНОЕ МЕНЮ
   • Правый клик в любом поле редактирования:
     - Копировать (Ctrl+C)
     - Вставить (Ctrl+V) 
     - Вырезать (Ctrl+X)
   • Работает со ВСЕМИ полями, включая "Особенности" и "Содержимое"

5. 🔄 УПРАВЛЕНИЕ СПИСКОМ
   • ⬆️/⬇️ - переместить товар вверх/вниз
   • 📋 - создать копию товара
   • 🗑️ - удалить товар (нужно сохранить изменения)

6. 💾 СОХРАНЕНИЕ
   • "💾 Сохранить товар" - сохраняет изменения текущего товара
   • "💾 Сохранить все" - сохраняет ВСЕ изменения в файлы
   • Автоматически создаются резервные копии
   • Удаленные товары не сохраняются в файлы

⚠️ ВАЖНО: Удаленные товары окончательно удаляются только после
сохранения всех изменений ("💾 Сохранить все")

═══════════════════════════════════════════════════════════════
        Для вопросов: irashitov79@mail.ru | FIXCAD MARKET
═══════════════════════════════════════════════════════════════
        """
        
        instr_window = tk.Toplevel(self.root)
        instr_window.title("Инструкция")
        instr_window.geometry("800x600")
        instr_window.minsize(800, 600)  # Делаем и окно инструкции неуменьшаемым
        
        # Делаем растягиваемым
        instr_window.grid_rowconfigure(0, weight=1)
        instr_window.grid_columnconfigure(0, weight=1)
        
        text_widget = scrolledtext.ScrolledText(instr_window, wrap=tk.WORD, 
                                               font=("Courier", 10))
        text_widget.grid(row=0, column=0, sticky=tk.NSEW, padx=10, pady=10)
        text_widget.insert(1.0, instructions)
        text_widget.config(state=tk.DISABLED)
        
        button_frame = tk.Frame(instr_window)
        button_frame.grid(row=1, column=0, pady=10)
        tk.Button(button_frame, text="Закрыть", command=instr_window.destroy,
                 bg=self.accent_color, fg="white", padx=20, pady=5).pack()

def main():
    root = tk.Tk()
    app = ProductManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()