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
        
        # Добавляем атрибут для отслеживания текущего товара
        self.current_product_id = None
        
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
                                        values=["CDW", "SPW", "A3D", "M3D", "STL", "STEP", "TXT", "EXE"])
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
            self.current_product_id = None
            
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
            if not match:
                # Попробуем найти без точки с запятой
                match = re.search(r'const PRODUCTS\s*=\s*({.*?})\s*\n', content, re.DOTALL)
            
            if match:
                js_data = match.group(1)
                print(f"🔍 Найден объект PRODUCTS ({len(js_data)} символов)")
                
                # Проверяем корректность структуры
                brace_count = js_data.count('{') - js_data.count('}')
                if brace_count != 0:
                    print(f"⚠️  Внимание: несбалансированные скобки в PRODUCTS: {brace_count}")
                
                # Используем безопасный eval
                self.server_products = self.safe_eval_js_object(js_data)
                print(f"✅ Загружено {len(self.server_products)} товаров из server.js")
            else:
                print("❌ Не удалось найти объект PRODUCTS в server.js")
                self.server_products = {}
            
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
        
        # Заменяем строки в одинарных и двойных кавычках
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
        """Обработчик выбора товара в списке"""
        # Сохраняем изменения текущего товара перед переключением
        was_saved = self.auto_save_current_product()
        if was_saved:
            print(f"💾 Изменения сохранены перед переключением")
        
        selection = self.products_listbox.curselection()
        if not selection:
            return
            
        product_id = self.products_listbox.get(selection[0]).split(":")[0].strip()
        self.load_product_data(product_id)
    
    def auto_save_current_product(self):
        """Автоматически сохраняет текущий товар если он редактировался"""
        current_id_in_field = self.product_id_var.get().strip()
        
        # Если нет ID товара в поле
        if not current_id_in_field:
            return False
        
        # Используем current_product_id как старый ID (тот, что был загружен)
        old_id = self.current_product_id
        
        # Если ID в поле изменился относительно загруженного
        if old_id and old_id != current_id_in_field:
            # Проверяем, не занят ли новый ID другим товаром
            if current_id_in_field in self.products_data and current_id_in_field != old_id:
                print(f"⚠️  ID '{current_id_in_field}' уже используется другим товаром, автосохранение отменено")
                # Восстанавливаем старый ID в поле
                self.product_id_var.set(old_id)
                return False
            
            # Разрешаем изменение ID - это будет переименование товара
            print(f"🔄 Обнаружено изменение ID: '{old_id}' → '{current_id_in_field}'")
        
        # Получаем данные из полей интерфейса
        model_value = self.model_var.get().strip()
        if not model_value:
            model_value = None
        
        # Получаем текущую ссылку на оплату
        current_payment_url = self.payment_url_var.get().strip()
        
        # Автоматически обновляем ссылку на оплату при изменении ID
        if old_id and old_id != current_id_in_field and current_payment_url:
            # Если ссылка содержит старый label, обновляем его
            if f"label={old_id}" in current_payment_url:
                current_payment_url = current_payment_url.replace(f"label={old_id}", f"label={current_id_in_field}")
                # Обновляем поле в интерфейсе
                self.payment_url_var.set(current_payment_url)
                print(f"🔗 Автообновление ссылки на оплату с новым label: {current_id_in_field}")
        
        # Подготавливаем новые данные из интерфейса
        new_products_data = {
            'name': self.name_var.get().strip(),
            'description': self.desc_text.get(1.0, tk.END).strip(),
            'image': self.image_var.get().strip(),
            'model': model_value,
            'formatBadge': self.format_var.get().strip(),
            'formats': [f.strip() for f in self.formats_var.get().split(',') if f.strip()],
            'features': [f.strip() for f in self.features_text.get(1.0, tk.END).strip().split('\n') if f.strip()],
            'paymentUrl': current_payment_url
        }
        
        new_server_data = {
            'name': self.name_var.get().strip(),
            'description': self.desc_text.get(1.0, tk.END).strip(),
            'zipUrl': self.zip_url_var.get().strip(),
            'zipName': self.zip_name_var.get().strip(),
            'contents': [c.strip() for c in self.contents_text.get(1.0, tk.END).strip().split('\n') if c.strip()]
        }
        
        # Проверяем, есть ли изменения (сравниваем с сохраненными данными)
        has_changes = False
        
        # Определяем, с какими данными сравнивать
        compare_id = old_id if old_id and old_id in self.products_data else current_id_in_field
        
        if compare_id in self.products_data:
            current_products_data = self.products_data[compare_id]
            
            # Сравниваем каждое поле (кроме ID, который мы уже обработали)
            for key, new_value in new_products_data.items():
                current_value = current_products_data.get(key)
                
                # Особое сравнение для списков
                if isinstance(new_value, list) and isinstance(current_value, list):
                    if sorted(new_value) != sorted(current_value):
                        has_changes = True
                        break
                elif new_value != current_value:
                    has_changes = True
                    break
        
        # Проверяем изменения в server данных
        if not has_changes and compare_id in self.server_products:
            current_server_data = self.server_products[compare_id]
            
            for key, new_value in new_server_data.items():
                current_value = current_server_data.get(key)
                
                if isinstance(new_value, list) and isinstance(current_value, list):
                    if sorted(new_value) != sorted(current_value):
                        has_changes = True
                        break
                elif new_value != current_value:
                    has_changes = True
                    break
        
        # Если ID изменился - это всегда изменения
        if old_id and old_id != current_id_in_field:
            has_changes = True
        
        if has_changes:
            # Если ID изменился, переносим данные
            if old_id and old_id != current_id_in_field:
                if old_id in self.products_data:
                    del self.products_data[old_id]
                if old_id in self.server_products:
                    del self.server_products[old_id]
                if old_id in self.deleted_products:
                    self.deleted_products.remove(old_id)
                
                print(f"🔄 Автосохранение: изменен ID товара '{old_id}' → '{current_id_in_field}'")
            
            # Сохраняем изменения под новым ID
            self.products_data[current_id_in_field] = new_products_data
            self.server_products[current_id_in_field] = new_server_data
            
            # Обновляем current_product_id
            self.current_product_id = current_id_in_field
            
            # Обновляем список товаров
            self.update_products_list()
            
            print(f"💾 Автосохранение товара '{current_id_in_field}'")
            return True
        
        return False
    
    def load_product_data(self, product_id):
        """Загружает данные выбранного товара"""
        print(f"\n📥 Загружаем данные товара: {product_id}")
        
        # Сохраняем текущий ID (тот, что выбран в списке)
        self.current_product_id = product_id
        
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
            
            # Получаем ссылку на оплату
            payment_url = product.get('paymentUrl', '')
            
            # Если ссылка на оплату пустая или не содержит правильного label, генерируем новую
            if not payment_url or f"label={product_id}" not in payment_url:
                payment_url = f"https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label={product_id}"
                # Обновляем в данных
                product['paymentUrl'] = payment_url
            
            # Загружаем данные
            self.product_id_var.set(product_id)
            self.name_var.set(product.get('name', ''))
            self.desc_text.delete(1.0, tk.END)
            self.desc_text.insert(1.0, product.get('description', ''))
            self.image_var.set(product.get('image', ''))
            
            # ИСПРАВЛЕНИЕ: преобразуем None в пустую строку для поля модели
            model_value = product.get('model', '')
            if model_value is None:
                model_value = ''
            self.model_var.set(model_value)
            
            self.format_var.set(product.get('formatBadge', ''))
            
            # Файлы и ссылки (только из server_products)
            self.zip_url_var.set(server_product.get('zipUrl', ''))
            self.zip_name_var.set(server_product.get('zipName', ''))
            
            # Ссылка на оплату и форматы
            self.payment_url_var.set(payment_url)
            
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
            
            # Содержимое архива (только из server_products)
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
        else:
            # Если товар не найден, очищаем поля
            print(f"⚠️ Товар {product_id} не найден в данных")
            self.clear_product_fields()
            self.current_product_id = None
    
    def clear_product_fields(self):
        """Очищает все поля редактирования товара"""
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
    
    def save_product(self):
        """Сохраняет текущий товар (без записи в файлы)"""
        old_id = self.current_product_id  # Запоминаем старый ID (из загруженных данных)
        new_id = self.product_id_var.get().strip()
        
        if not new_id:
            messagebox.showwarning("Внимание", "Введите ID товара!")
            return
            
        if not re.match(r'^[a-zA-Z0-9_]+$', new_id):
            messagebox.showwarning("Внимание", "ID должен содержать только латинские буквы, цифры и подчеркивания!")
            return
        
        # Получаем значение модели и преобразуем пустую строку в None
        model_value = self.model_var.get().strip()
        if not model_value:
            model_value = None
        
        # Получаем текущую ссылку на оплату из поля
        current_payment_url = self.payment_url_var.get().strip()
        
        # Если ссылка на оплату пустая или не содержит правильного label, генерируем новую
        if not current_payment_url or f"label={old_id if old_id else new_id}" not in current_payment_url:
            # Формируем новую ссылку на оплату с новым ID
            payment_url = f"https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label={new_id}"
        else:
            # Обновляем label в существующей ссылке, если ID изменился
            if old_id and old_id != new_id:
                # Заменяем старый label на новый в ссылке
                payment_url = current_payment_url.replace(f"label={old_id}", f"label={new_id}")
            else:
                payment_url = current_payment_url
            
        # Подготавливаем данные
        products_data = {
            'name': self.name_var.get().strip(),
            'description': self.desc_text.get(1.0, tk.END).strip(),
            'image': self.image_var.get().strip(),
            'model': model_value,
            'formatBadge': self.format_var.get().strip(),
            'formats': [f.strip() for f in self.formats_var.get().split(',') if f.strip()],
            'features': [f.strip() for f in self.features_text.get(1.0, tk.END).strip().split('\n') if f.strip()],
            'paymentUrl': payment_url
        }
        
        server_data = {
            'name': self.name_var.get().strip(),
            'description': self.desc_text.get(1.0, tk.END).strip(),
            'zipUrl': self.zip_url_var.get().strip(),
            'zipName': self.zip_name_var.get().strip(),
            'contents': [c.strip() for c in self.contents_text.get(1.0, tk.END).strip().split('\n') if c.strip()]
        }
        
        # Если ID изменился
        if old_id and old_id != new_id:
            # Проверяем, не занят ли новый ID
            if new_id in self.products_data and new_id != old_id:
                messagebox.showwarning("Внимание", f"ID '{new_id}' уже используется другим товаром!")
                # Восстанавливаем старый ID в поле
                self.product_id_var.set(old_id)
                return
            
            # Переносим данные со старого ID на новый
            if old_id in self.products_data:
                del self.products_data[old_id]
            if old_id in self.server_products:
                del self.server_products[old_id]
            
            # Удаляем старый ID из списка удаленных, если он там был
            if old_id in self.deleted_products:
                self.deleted_products.remove(old_id)
            
            print(f"🔄 Изменен ID товара: '{old_id}' → '{new_id}'")
        
        # Сохраняем данные
        self.products_data[new_id] = products_data
        self.server_products[new_id] = server_data
        
        # Обновляем поле ссылки на оплату в интерфейсе
        self.payment_url_var.set(payment_url)
        
        # Сохраняем текущий ID
        self.current_product_id = new_id
        
        # Обновляем список товаров
        self.update_products_list()
        
        # Находим и выделяем сохраненный товар в списке
        for i in range(self.products_listbox.size()):
            if self.products_listbox.get(i).startswith(new_id + ":"):
                self.products_listbox.selection_clear(0, tk.END)
                self.products_listbox.selection_set(i)
                self.products_listbox.see(i)
                break
        
        self.status_var.set(f"Товар '{new_id}' сохранен")
        print(f"💾 Товар сохранен: '{new_id}'")
    
    def add_product(self):
        # Сначала сохраняем текущий товар если он редактировался
        was_saved = self.auto_save_current_product()
        if was_saved:
            print(f"💾 Изменения сохранены перед созданием нового товара")
        
        # Создаем новый ID для товара
        base_id = "new_product"
        counter = 1
        while f"{base_id}_{counter}" in self.products_data:
            counter += 1
        new_id = f"{base_id}_{counter}"
        
        # Сохраняем текущий ID
        self.current_product_id = new_id
        
        # Формируем ссылку на оплату с ID товара
        payment_url = f"https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label={new_id}"
        
        # Создаем пустую запись в данных
        self.products_data[new_id] = {
            'name': f"Новый товар {counter}",
            'description': "Описание нового товара",
            'image': "images/default.jpg",
            'model': None,
            'formatBadge': "CDW",
            'formats': ["CDW", "PDF", "DWG"],
            'features': ["Особенность 1", "Особенность 2"],
            'paymentUrl': payment_url
        }
        
        self.server_products[new_id] = {
            'name': f"Новый товар {counter}",
            'description': "Описание нового товара",
            'zipUrl': "https://disk.yandex.ru/d/...",
            'zipName': f"product_{counter}.zip",
            'contents': ["Содержимое 1", "Содержимое 2"]
        }
        
        # Загружаем данные нового товара в интерфейс
        self.load_product_data(new_id)
        
        # Обновляем список товаров
        self.update_products_list()
        
        # Выделяем новый товар в списке
        for i in range(self.products_listbox.size()):
            if self.products_listbox.get(i).startswith(new_id + ":"):
                self.products_listbox.selection_clear(0, tk.END)
                self.products_listbox.selection_set(i)
                self.products_listbox.see(i)
                break
        
        # Фокусируемся на поле названия
        self.name_entry.focus()
        self.name_entry.select_range(0, tk.END)
        
        self.status_var.set(f"Создан новый товар: {new_id}")
        print(f"➕ Создан новый товар: {new_id}")
    
    def duplicate_product(self):
        selection = self.products_listbox.curselection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар для дублирования!")
            return
            
        old_id = self.products_listbox.get(selection[0]).split(":")[0].strip()
        
        # Сначала сохраняем текущий товар если он редактировался
        was_saved = self.auto_save_current_product()
        if was_saved:
            print(f"💾 Изменения сохранены перед дублированием")
        
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
            
            # Если удаляем текущий товар, сбрасываем current_product_id
            if product_id == self.current_product_id:
                self.current_product_id = None
            
            # Обновляем список
            self.update_products_list()
            
            # Очищаем поля редактирования
            self.clear_product_fields()
            
            self.status_var.set(f"Товар '{product_id}' помечен на удаление")
    
    def move_up(self):
        selection = self.products_listbox.curselection()
        if not selection or selection[0] == 0:
            return
            
        idx = selection[0]
        product_id = self.products_listbox.get(idx).split(":")[0].strip()
        
        # Сначала сохраняем текущий товар если он редактировался
        was_saved = self.auto_save_current_product()
        if was_saved:
            print(f"💾 Изменения сохранены перед перемещением вверх")
        
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
        
        # Сначала сохраняем текущий товар если он редактировался
        was_saved = self.auto_save_current_product()
        if was_saved:
            print(f"💾 Изменения сохранены перед перемещением вниз")
        
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
            <button class="buy-button" data-product="${productId}" aria-label="Скачать ${product.name} за 100 рублей">
                Скачать за 100 руб.
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
        
        # Ищем начало объекта PRODUCTS
        start_match = re.search(r'const PRODUCTS\s*=\s*\{', content)
        if not start_match:
            messagebox.showerror("Ошибка", "Не найден объект PRODUCTS в server.js")
            return
        
        start_idx = start_match.start()
        
        # Находим конец объекта PRODUCTS с учетом вложенных объектов
        brace_count = 0
        in_string = False
        string_char = None
        end_idx = start_idx
        
        # Проходим от начала объекта до конца файла
        for i in range(start_idx, len(content)):
            char = content[i]
            
            # Учитываем строковые литералы
            if char in ['"', "'"] and (i == 0 or content[i-1] != '\\'):
                if not in_string:
                    in_string = True
                    string_char = char
                elif char == string_char:
                    in_string = False
                    string_char = None
            
            # Считаем фигурные скобки только вне строк
            if not in_string:
                if char == '{':
                    brace_count += 1
                elif char == '}':
                    brace_count -= 1
                    if brace_count == 0:
                        # Нашли закрывающую скобку объекта PRODUCTS
                        # Ищем точку с запятой после скобки
                        j = i + 1
                        while j < len(content) and content[j].isspace():
                            j += 1
                        if j < len(content) and content[j] == ';':
                            end_idx = j + 1
                        else:
                            end_idx = i + 1
                        break
        
        if brace_count != 0:
            messagebox.showerror("Ошибка", "Не удалось найти конец объекта PRODUCTS")
            return
        
        # Генерируем новый объект PRODUCTS
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
        
        new_products += "};\n\n"
        
        # Проверяем, есть ли комментарий или другой код после объекта PRODUCTS
        next_char_idx = end_idx
        while next_char_idx < len(content) and content[next_char_idx].isspace():
            next_char_idx += 1
        
        # Если после объекта есть код (например, комментарий), сохраняем его
        if next_char_idx < len(content):
            new_content = content[:start_idx] + new_products + content[next_char_idx:]
        else:
            new_content = content[:start_idx] + new_products
        
        # Удаляем возможные дублирующиеся пустые строки и точки с запятой
        new_content = re.sub(r';\s*;+', ';', new_content)  # Удаляем множественные ;
        new_content = re.sub(r'\n\s*\n\s*\n+', '\n\n', new_content)  # Удаляем множественные пустые строки
        
        with open(self.server_js_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"✅ server.js сохранен ({len(server_products)} товаров)")
    
    def show_instructions(self):
        instructions = """
═══════════════════════════════════════════════════════════════
            	  ИНСТРУКЦИЯ ПО ИСПОЛЬЗОВАНИЮ
═══════════════════════════════════════════════════════════════

1. 📋 ОБЩИЕ ВОЗМОЖНОСТИ

• Контекстное меню (правый клик в любом поле):
  - Копировать (Ctrl+C) - копирует выделенный текст
  - Вставить (Ctrl+V) - вставляет текст из буфера обмена  
  - Вырезать (Ctrl+X) - вырезает выделенный текст
  - Работает во ВСЕХ полях ввода и текстовых областях

• Автосохранение: при переключении между товарами текущий 
  товар автоматически сохраняется

• Валидация: проверка корректности вводимых данных

2. 🎯 ВЕРХНЯЯ ПАНЕЛЬ КНОПОК

🔄 "Обновить данные"
   - Перезагружает данные с сайта
   - Обновляет список товаров
   - Используйте после ручного редактирования сайта

➕ "Добавить товар"
   - Создает новый товар с заполненными полями по умолчанию
   - Автоматически генерирует ID вида "new_product_1"
   - Создает новую ссылку на оплату с правильным label

💾 "Сохранить все"
   - Сохраняет ВСЕ изменения во ВСЕ файлы
   - Создает резервные копии файлов
   - Товары, удаленные из списка, будут удалены с сайта

📋 "Инструкция"
   - Показывает эту инструкцию

3. 📦 ЛЕВАЯ ПАНЕЛЬ - СПИСОК ТОВАРОВ

• Список всех товаров в формате: "ID: Название..."
• Выбор товара: клик по строке загружает данные в правую панель

Кнопки управления списком:

⬆️ "Вверх" - перемещает выбранный товар на одну позицию вверх
⬇️ "Вниз" - перемещает выбранный товар на одну позицию вниз  
📋 "Дублировать" - создает копию выбранного товара с суффиксом "_copy"
🗑️ "Удалить" - удаляет товар из списка (удалится с сайта после сохранения)

4. ✏️ ПРАВАЯ ПАНЕЛЬ - РЕДАКТИРОВАНИЕ ТОВАРА

───────────────────────────────────────────────────────────────
ВКЛАДКА "ОСНОВНЫЕ"
───────────────────────────────────────────────────────────────

• ID товара:
  - Уникальный идентификатор товара
  - Только латинские буквы, цифры и подчеркивания
  - При изменении ID автоматически обновляется ссылка на оплату
  - Примеры: "valve_01", "pump_industrial"

• Название:
  - Отображается на сайте как заголовок товара
  - Рекомендуется 3-7 слов

• Описание:
  - Подробное описание товара
  - Отображается на сайте под названием
  - Многострочное поле с переносом слов

• Изображение:
  - Путь к файлу изображения товара
  - Форматы: PNG, JPG, JPEG, GIF
  - Кнопка "📁" открывает диалог выбора файла
  - Автоматически копирует файл в папку "images/"

• 3D модель:
  - Путь к файлу 3D модели (STL формат)
  - Кнопка "📁" открывает диалог выбора файла
  - Кнопка "❌" очищает поле (удаляет 3D модель)
  - Автоматически копирует файл в папку "models/"
  - Если поле пустое - товар будет без 3D просмотра

• Бейдж формата:
  - Выпадающий список с форматами
  - Отображается как цветной бейдж на изображении товара
  - Варианты: CDW, SPW, A3D, M3D, STL, STEP, TXT

───────────────────────────────────────────────────────────────
ВКЛАДКА "ФАЙЛЫ"
───────────────────────────────────────────────────────────────

• Ссылка на Яндекс.Диск:
  - Прямая ссылка на скачивание архива с файлами
  - Формат: https://disk.yandex.ru/d/...
  - Используется сервером для предоставления доступа

• Имя архива:
  - Имя ZIP-архива, которое увидит пользователь
  - Пример: "valve_technical_drawings.zip"
  - Автоматически подставляется в ссылку скачивания

• Ссылка на оплату (ЮMoney):
  - Ссылка на оплату через ЮMoney
  - Автоматически генерируется при создании товара
  - Содержит ID товара в параметре "label"
  - Формат: https://yoomoney.ru/quickpay/confirm?receiver=...&label=ID_товара

• Форматы файлов:
  - Список форматов, доступных в архиве
  - Перечисляются через запятую
  - Пример: "CDW, PDF, DWG, STEP"
  - Отображаются как теги под описанием товара

───────────────────────────────────────────────────────────────
ВКЛАДКА "ДОПОЛНИТЕЛЬНО"
───────────────────────────────────────────────────────────────

• Особенности товара:
  - Список ключевых особенностей товара
  - Каждая особенность на новой строке
  - Отображаются как маркированный список на сайте
  - Пример:
    Высокая точность
    Коррозионная стойкость
    Простота установки

• Содержимое архива:
  - Подробное описание того, что находится в архиве
  - Каждый пункт на новой строке
  - Пример:
    Чертежи в формате CDW
    3D модель в формате STEP
    Техническая документация PDF
    Инструкция по монтажу

• Кнопка "🔄 Сгенерировать содержимое":
  - Автоматически копирует текст из "Особенности товара"
    в "Содержимое архива"
  - Полезно для быстрого заполнения

5. 💾 СИСТЕМА СОХРАНЕНИЯ

• Автосохранение в оперативной памяти при:
  - Переключении между товарами
  - Перемещении товаров в списке
  - Дублировании товаров

• Ручное сохранение:
  - "💾 Сохранить все" - полное сохранение
  - Создает резервные копии с timestamp
  - Форматы имен: products.js.backup_20241215_143022

• Файлы:
  - products.js - данные для отображения на сайте
  - server.js - данные для серверной части (скачивание)

6. ⚠️ ВАЖНЫЕ ЗАМЕЧАНИЯ

• Перед закрытием программы для внесения изменений на сайт нажимайте "💾 Сохранить все"

• Удаленные товары окончательно удаляются только после сохранения

• При изменении ID товара автоматически обновляется ссылка на оплату

• Для работы 3D просмотра нужны файлы STL в папке "models/"

• Изображения должны быть в папке "images/"

• Ссылки на Яндекс.Диск должны быть прямыми (не через публичный доступ)

7. 🛠️ ТЕХНИЧЕСКАЯ ИНФОРМАЦИЯ

• Форматы данных:
  - products.js: отображение, микроразметка, оплата
  - server.js: скачивание файлов

• Структура папок:
  /images/ - изображения товаров
  /models/ - 3D модели (STL)
  products.js - основной файл данных
  server.js - серверный файл данных

• Логирование: все действия логируются в консоль

═══════════════════════════════════════════════════════════════
                        УДАЧНОЙ РАБОТЫ!
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