import tkinter as tk
from tkinter import ttk, messagebox, filedialog, scrolledtext
import json
import os
import re
import shutil
import tempfile
import webbrowser
from datetime import datetime
import time

class ProductManager:
    def __init__(self, root):
        self.root = root
        self.root.title("FIXCAD MARKET - Менеджер товаров v2.0")
        
        # Пути к файлам и папкам
        self.index_html_path = "index.html"
        self.server_js_path = "server.js"
        self.images_dir = "images"
        self.models_dir = "models"
        
        # Создаем папки если их нет
        os.makedirs(self.images_dir, exist_ok=True)
        os.makedirs(self.models_dir, exist_ok=True)
        
        # Данные товаров
        self.products = {}
        
        self.setup_ui()
        self.load_products_simple()

        # Автоматическая очистка старых временных файлов при запуске
        self.root.after(1000, self.auto_cleanup)  # Запуск через 1 секунду
        
        # Устанавливаем минимальный размер окна
        self.root.update()
        self.root.minsize(1100, 750)
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Управление товарами FIXCAD MARKET v2.0", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 20))
        
        # Форма добавления/редактирования товара
        form_frame = ttk.LabelFrame(main_frame, text="Добавить/Редактировать товар", padding="10")
        form_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), padx=(0, 10))
        
        # Поля формы
        ttk.Label(form_frame, text="ID товара:").grid(row=0, column=0, sticky=tk.W, pady=2)
        self.product_id_var = tk.StringVar()
        self.product_id_entry = ttk.Entry(form_frame, textvariable=self.product_id_var, width=20)
        self.product_id_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(form_frame, text="Название:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(form_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(form_frame, textvariable=self.desc_var, width=30)
        self.desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(form_frame, text="Ссылка Яндекс.Диск:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.zip_url_var = tk.StringVar()
        self.zip_url_entry = ttk.Entry(form_frame, textvariable=self.zip_url_var, width=40)
        self.zip_url_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        ttk.Label(form_frame, text="Имя архива:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.zip_name_var = tk.StringVar()
        self.zip_name_entry = ttk.Entry(form_frame, textvariable=self.zip_name_var, width=30)
        self.zip_name_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Форматы файлов
        ttk.Label(form_frame, text="Форматы файлов:").grid(row=5, column=0, sticky=tk.W, pady=2)
        formats_frame = ttk.Frame(form_frame)
        formats_frame.grid(row=5, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Первый ряд форматов
        formats_row1 = ttk.Frame(formats_frame)
        formats_row1.pack(fill=tk.X)
        
        self.cdw_var = tk.BooleanVar(value=True)
        self.spw_var = tk.BooleanVar(value=True)
        self.a3d_var = tk.BooleanVar(value=True)
        self.m3d_var = tk.BooleanVar(value=True)
        self.stl_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(formats_row1, text="CDW", variable=self.cdw_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row1, text="SPW", variable=self.spw_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row1, text="A3D", variable=self.a3d_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row1, text="M3D", variable=self.m3d_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row1, text="STL", variable=self.stl_var).pack(side=tk.LEFT)
        
        # Второй ряд форматов (новые)
        formats_row2 = ttk.Frame(formats_frame)
        formats_row2.pack(fill=tk.X, pady=(5, 0))
        
        self.step_var = tk.BooleanVar(value=False)
        self.pdf_var = tk.BooleanVar(value=False)
        self.doc_var = tk.BooleanVar(value=False)
        self.xls_var = tk.BooleanVar(value=False)
        self.txt_var = tk.BooleanVar(value=False)
        self.exe_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(formats_row2, text="STEP", variable=self.step_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row2, text="PDF", variable=self.pdf_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row2, text="DOC", variable=self.doc_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row2, text="XLS", variable=self.xls_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row2, text="TXT", variable=self.txt_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_row2, text="EXE", variable=self.exe_var).pack(side=tk.LEFT)
        
        # 3D модель
        ttk.Label(form_frame, text="Есть 3D модель:").grid(row=6, column=0, sticky=tk.W, pady=2)
        self.has_3d_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(form_frame, text="Есть 3D модель (STL)", variable=self.has_3d_var).grid(row=6, column=1, sticky=tk.W, pady=2)
        
        # Загрузка файлов
        ttk.Label(form_frame, text="Изображение товара:").grid(row=7, column=0, sticky=tk.W, pady=2)
        file_frame = ttk.Frame(form_frame)
        file_frame.grid(row=7, column=1, sticky=(tk.W, tk.E), pady=2)
        
        self.image_path_var = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.image_path_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="Выбрать...", command=self.select_image).pack(side=tk.LEFT)
        
        ttk.Label(form_frame, text="3D модель (STL):").grid(row=8, column=0, sticky=tk.W, pady=2)
        model_frame = ttk.Frame(form_frame)
        model_frame.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=2)
        
        self.model_path_var = tk.StringVar()
        ttk.Entry(model_frame, textvariable=self.model_path_var, width=25).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(model_frame, text="Выбрать...", command=self.select_model).pack(side=tk.LEFT)
        
        # Содержимое архива
        ttk.Label(form_frame, text="Содержимое архива:").grid(row=9, column=0, sticky=tk.W, pady=2)
        self.contents_text = tk.Text(form_frame, width=30, height=4)
        self.contents_text.grid(row=9, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Кнопки формы
        button_frame = ttk.Frame(form_frame)
        button_frame.grid(row=10, column=0, columnspan=2, pady=10)
        
        ttk.Button(button_frame, text="Новый товар", command=self.new_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Сохранить", command=self.update_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить форму", command=self.clear_form).pack(side=tk.LEFT, padx=5)
        
        # Список товаров
        list_frame = ttk.LabelFrame(main_frame, text="Список товаров", padding="10")
        list_frame.grid(row=1, column=1, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Таблица товаров
        columns = ("ID", "Название", "Форматы", "3D", "Файлы")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=15)
        
        self.tree.heading("ID", text="ID")
        self.tree.heading("Название", text="Название")
        self.tree.heading("Форматы", text="Форматы")
        self.tree.heading("3D", text="3D")
        self.tree.heading("Файлы", text="Файлы")
        
        self.tree.column("ID", width=80)
        self.tree.column("Название", width=150)
        self.tree.column("Форматы", width=100)
        self.tree.column("3D", width=50)
        self.tree.column("Файлы", width=80)
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Скроллбар для таблицы
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        # Кнопки управления списком
        list_buttons_frame = ttk.Frame(list_frame)
        list_buttons_frame.grid(row=1, column=0, columnspan=2, pady=10)
        
        ttk.Button(list_buttons_frame, text="▲ Вверх", command=self.move_up).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_buttons_frame, text="▼ Вниз", command=self.move_down).pack(side=tk.LEFT, padx=2)
        ttk.Button(list_buttons_frame, text="Дублировать", command=self.duplicate_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_buttons_frame, text="Удалить", command=self.delete_product).pack(side=tk.LEFT, padx=5)

        # Кнопки экспорта
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(export_frame, text="Предпросмотр HTML", command=self.preview_html).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Очистить временные файлы", command=self.cleanup_temp_files).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Обновить index.html", command=self.update_index_html).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Обновить server.js", command=self.update_server_js).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Обновить оба файла", command=self.update_both).pack(side=tk.LEFT, padx=5)
        
        # Панель статуса
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky=(tk.W, tk.E))
        
        self.status_var = tk.StringVar(value="Готов к работе")
        ttk.Label(status_frame, textvariable=self.status_var, foreground="green").pack(side=tk.LEFT)
        
        # Привязка событий
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        form_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
    def new_product(self):
        """Создает новый товар и добавляет его в список"""
        if not self.validate_form():
            return
            
        product_id = self.product_id_var.get().strip()
        if product_id in self.products:
            messagebox.showerror("Ошибка", f"Товар с ID '{product_id}' уже существует!")
            return
        
        # Проверка уникальности zipUrl
        zip_url = self.zip_url_var.get().strip()
        duplicate = self.check_duplicate_url(zip_url, exclude_product=product_id)
        if duplicate:
            if not messagebox.askyesno("Дублирование ссылки", 
                f"Ссылка Яндекс.Диск уже используется товаром '{duplicate['name']}' (ID: {duplicate['id']}).\n"
                "Продолжить?"):
                return
        
        # Копируем файлы
        self.copy_product_files(product_id)
        
        # Собираем форматы
        formats = self.get_selected_formats()
            
        self.products[product_id] = {
            'name': self.name_var.get().strip(),
            'description': self.desc_var.get().strip(),
            'zipUrl': zip_url,
            'zipName': self.zip_name_var.get().strip(),
            'contents': [line.strip() for line in self.contents_text.get("1.0", tk.END).strip().split('\n') if line.strip()],
            'formats': formats,
            'has_3d': self.has_3d_var.get(),
            'has_image': bool(self.image_path_var.get()),
            'has_model': bool(self.model_path_var.get()) and self.has_3d_var.get()
        }
        
        self.refresh_tree()
        messagebox.showinfo("Успех", f"Товар '{self.name_var.get()}' добавлен!")
        
    def select_image(self):
        """Выбор изображения товара"""
        filename = filedialog.askopenfilename(
            title="Выберите изображение товара",
            filetypes=[("Image files", "*.png *.jpg *.jpeg *.gif *.bmp"), ("All files", "*.*")]
        )
        if filename:
            self.image_path_var.set(filename)
            
    def select_model(self):
        """Выбор 3D модели"""
        filename = filedialog.askopenfilename(
            title="Выберите 3D модель (STL)",
            filetypes=[("STL files", "*.stl"), ("All files", "*.*")]
        )
        if filename:
            self.model_path_var.set(filename)
            
    def copy_product_files(self, product_id):
        """Копирует файлы товара в соответствующие папки"""
        # Копируем изображение
        image_src = self.image_path_var.get()
        if image_src and os.path.exists(image_src):
            # Получаем расширение файла
            ext = os.path.splitext(image_src)[1].lower()
            # Создаем имя файла: product_id + расширение
            image_dst = os.path.join(self.images_dir, f"{product_id}{ext}")
            shutil.copy2(image_src, image_dst)
            
        # Копируем 3D модель если есть
        model_src = self.model_path_var.get()
        if model_src and os.path.exists(model_src) and self.has_3d_var.get():
            model_dst = os.path.join(self.models_dir, f"{product_id}.stl")
            shutil.copy2(model_src, model_dst)
        
    def load_products_simple(self):
        """Загрузка реальных товаров"""
        self.products = {
            "stend": {
                "name": "Стенд для пакеров",
                "description": "Полный комплект чертежей и 3D модель",
                "zipUrl": "https://disk.yandex.ru/d/yavUz8k9ce2gAw/download",
                "zipName": "stend.zip",
                "contents": ["Чертежи КОМПАС", "3D модели КОМПАС", "Спецификации", "Паспорт, РЭ"],
                "formats": ["CDW", "SPW", "A3D", "M3D"],
                "has_3d": True,
                "has_image": os.path.exists(os.path.join(self.images_dir, "stend.png")),
                "has_model": os.path.exists(os.path.join(self.models_dir, "stend.stl"))
            },
            "stapel": {
                "name": "Стапель сварочный 3х12 м",
                "description": "Комплект чертежей + 3D модель",
                "zipUrl": "https://disk.yandex.ru/d/Nv7iD6T5JYrKVQ/download",
                "zipName": "stapel.zip",
                "contents": ["Чертежи КОМПАС", "3D модели КОМПАС", "Спецификации"],
                "formats": ["CDW", "SPW", "A3D", "M3D"],
                "has_3d": True,
                "has_image": os.path.exists(os.path.join(self.images_dir, "stapel.png")),
                "has_model": os.path.exists(os.path.join(self.models_dir, "stapel.stl"))
            },
            "level": {
                "name": "Уровнемер механический",
                "description": "Для любого емкостного без давления",
                "zipUrl": "https://disk.yandex.ru/d/79sH_E3uDXdNgw/download",
                "zipName": "level.zip",
                "contents": ["Сборочный чертеж", "Спецификация", "Таблица сварных соединений", "Технические требования"],
                "formats": ["CDW"],
                "has_3d": False,
                "has_image": os.path.exists(os.path.join(self.images_dir, "level.png")),
                "has_model": False
            }
        }
        self.refresh_tree()
        
    def get_selected_formats(self):
        """Получает список выбранных форматов"""
        formats = []
        format_vars = [
            (self.cdw_var, "CDW"),
            (self.spw_var, "SPW"),
            (self.a3d_var, "A3D"),
            (self.m3d_var, "M3D"),
            (self.stl_var, "STL"),
            (self.step_var, "STEP"),
            (self.pdf_var, "PDF"),
            (self.doc_var, "DOC"),
            (self.xls_var, "XLS"),
            (self.txt_var, "TXT"),
            (self.exe_var, "EXE")
        ]
        
        for var, fmt in format_vars:
            if var.get():
                formats.append(fmt)
        return formats

    def refresh_tree(self):
        """Обновляет дерево товаров с сохранением порядка"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        # Сохраняем порядок из словаря products
        for product_id, product_data in self.products.items():
            formats = ", ".join(product_data.get('formats', []))
            has_3d = "✅" if product_data.get('has_3d', False) else "❌"
            
            # Статус файлов
            files_status = ""
            if product_data.get('has_image', False):
                files_status += "🖼️"
            if product_data.get('has_model', False):
                files_status += "📐"
            if not files_status:
                files_status = "❌"
            
            self.tree.insert("", tk.END, values=(
                product_id,
                product_data.get('name', ''),
                formats,
                has_3d,
                files_status
            ))

    def update_product(self):
        """Обновляет существующий товар"""
        if not self.validate_form():
            return
            
        product_id = self.product_id_var.get().strip()
        if product_id not in self.products:
            messagebox.showerror("Ошибка", f"Товар с ID '{product_id}' не найден!")
            return
        
        # Проверка уникальности zipUrl
        zip_url = self.zip_url_var.get().strip()
        duplicate = self.check_duplicate_url(zip_url, exclude_product=product_id)
        if duplicate:
            if not messagebox.askyesno("Дублирование ссылки", 
                f"Ссылка Яндекс.Диск уже используется товаром '{duplicate['name']}' (ID: {duplicate['id']}).\n"
                "Продолжить?"):
                return
        
        # Копируем файлы
        self.copy_product_files(product_id)
        
        # Собираем форматы
        formats = self.get_selected_formats()
            
        self.products[product_id] = {
            'name': self.name_var.get().strip(),
            'description': self.desc_var.get().strip(),
            'zipUrl': zip_url,
            'zipName': self.zip_name_var.get().strip(),
            'contents': [line.strip() for line in self.contents_text.get("1.0", tk.END).strip().split('\n') if line.strip()],
            'formats': formats,
            'has_3d': self.has_3d_var.get(),
            'has_image': bool(self.image_path_var.get()) or self.products[product_id].get('has_image', False),
            'has_model': (bool(self.model_path_var.get()) and self.has_3d_var.get()) or self.products[product_id].get('has_model', False)
        }
        
        self.refresh_tree()
        messagebox.showinfo("Успех", f"Товар '{self.name_var.get()}' обновлен!")

    def duplicate_product(self):
        """Дублирует выбранный товар вместе с файлами"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар для дублирования!")
            return
            
        product_id = self.tree.item(selection[0])['values'][0]
        product_data = self.products[product_id]
        
        # Создаем новый ID на основе старого
        base_id = product_id
        counter = 1
        new_id = f"{base_id}_{counter}"
        
        # Ищем свободный ID
        while new_id in self.products:
            counter += 1
            new_id = f"{base_id}_{counter}"
        
        # Копируем файлы изображения
        has_image = False
        image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
        for ext in image_extensions:
            old_image_path = os.path.join(self.images_dir, f"{product_id}{ext}")
            if os.path.exists(old_image_path):
                new_image_path = os.path.join(self.images_dir, f"{new_id}{ext}")
                shutil.copy2(old_image_path, new_image_path)
                has_image = True
                break
        
        # Копируем файл 3D модели
        has_model = False
        old_model_path = os.path.join(self.models_dir, f"{product_id}.stl")
        if os.path.exists(old_model_path) and product_data.get('has_3d', False):
            new_model_path = os.path.join(self.models_dir, f"{new_id}.stl")
            shutil.copy2(old_model_path, new_model_path)
            has_model = True
        
        # Копируем данные товара
        new_product_data = {
            'name': f"{product_data['name']} (копия {counter})",
            'description': product_data['description'],
            'zipUrl': product_data['zipUrl'],
            'zipName': product_data['zipName'],
            'contents': product_data['contents'][:],
            'formats': product_data['formats'][:],
            'has_3d': product_data.get('has_3d', False),
            'has_image': has_image,
            'has_model': has_model
        }
        
        # Добавляем новый товар
        self.products[new_id] = new_product_data
        
        # Обновляем дерево и очищаем форму
        self.refresh_tree()
        self.clear_form()
        
        messagebox.showinfo("Успех", f"Товар '{product_data['name']}' продублирован как '{new_id}'!")

        # Автоматически заполняем форму для редактирования нового товара
        self.product_id_var.set(new_id)
        self.name_var.set(new_product_data['name'])
        self.desc_var.set(new_product_data['description'])
        self.zip_url_var.set(new_product_data['zipUrl'])
        self.zip_name_var.set(new_product_data['zipName'])
        
        # Устанавливаем форматы
        formats = new_product_data['formats']
        self.cdw_var.set("CDW" in formats)
        self.spw_var.set("SPW" in formats)
        self.a3d_var.set("A3D" in formats)
        self.m3d_var.set("M3D" in formats)
        self.stl_var.set("STL" in formats)
        
        # Устанавливаем 3D модель
        self.has_3d_var.set(new_product_data['has_3d'])
        
        # Показываем статус файлов
        if has_image:
            self.image_path_var.set("(файл скопирован)")
        if has_model:
            self.model_path_var.set("(файл скопирован)")
        
        self.contents_text.delete("1.0", tk.END)
        self.contents_text.insert("1.0", '\n'.join(new_product_data['contents']))

    def delete_product(self):
        """Удаляет выбранный товар"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар для удаления!")
            return
            
        product_id = self.tree.item(selection[0])['values'][0]
        product_name = self.products[product_id]['name']
        
        if messagebox.askyesno("Подтверждение", f"Удалить товар '{product_name}'?"):
            # Удаляем файлы товара
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
            for ext in image_extensions:
                image_path = os.path.join(self.images_dir, f"{product_id}{ext}")
                if os.path.exists(image_path):
                    os.remove(image_path)
                    
            model_path = os.path.join(self.models_dir, f"{product_id}.stl")
            if os.path.exists(model_path):
                os.remove(model_path)
            
            del self.products[product_id]
            self.refresh_tree()
            self.clear_form()
            messagebox.showinfo("Успех", f"Товар '{product_name}' удален!")

    def edit_product(self):
        """Редактирует выбранный товар"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Внимание", "Выберите товар для редактирования!")
            return
            
        product_id = self.tree.item(selection[0])['values'][0]
        product_data = self.products[product_id]
        
        self.clear_form()
        
        self.product_id_var.set(product_id)
        self.name_var.set(product_data['name'])
        self.desc_var.set(product_data['description'])
        self.zip_url_var.set(product_data['zipUrl'])
        self.zip_name_var.set(product_data['zipName'])
        
        # Устанавливаем форматы
        formats = product_data.get('formats', [])
        self.cdw_var.set("CDW" in formats)
        self.spw_var.set("SPW" in formats)
        self.a3d_var.set("A3D" in formats)
        self.m3d_var.set("M3D" in formats)
        self.stl_var.set("STL" in formats)
        self.step_var.set("STEP" in formats)
        self.pdf_var.set("PDF" in formats)
        self.doc_var.set("DOC" in formats)
        self.xls_var.set("XLS" in formats)
        self.txt_var.set("TXT" in formats)
        self.exe_var.set("EXE" in formats)
        
        # Устанавливаем 3D модель
        self.has_3d_var.set(product_data.get('has_3d', False))
        
        # Показываем существующие файлы
        if product_data.get('has_image', False):
            self.image_path_var.set("(файл уже загружен)")
        if product_data.get('has_model', False):
            self.model_path_var.set("(файл уже загружен)")
        
        self.contents_text.delete("1.0", tk.END)
        self.contents_text.insert("1.0", '\n'.join(product_data['contents']))

    def clear_form(self):
        """Очищает форму"""
        self.product_id_var.set("")
        self.name_var.set("")
        self.desc_var.set("")
        self.zip_url_var.set("")
        self.zip_name_var.set("")
        self.cdw_var.set(True)
        self.spw_var.set(True)
        self.a3d_var.set(True)
        self.m3d_var.set(True)
        self.stl_var.set(False)
        self.step_var.set(False)
        self.pdf_var.set(False)
        self.doc_var.set(False)
        self.xls_var.set(False)
        self.txt_var.set(False)
        self.exe_var.set(False)
        self.has_3d_var.set(False)
        self.image_path_var.set("")
        self.model_path_var.set("")
        self.contents_text.delete("1.0", tk.END)

    def validate_form(self):
        """Проверяет заполнение формы"""
        if not all([self.product_id_var.get().strip(),
                   self.name_var.get().strip(),
                   self.desc_var.get().strip(),
                   self.zip_url_var.get().strip(),
                   self.zip_name_var.get().strip()]):
            messagebox.showerror("Ошибка", "Заполните все обязательные поля!")
            return False
            
        # Проверяем что выбран файл изображения для нового товара
        selection = self.tree.selection()
        if not selection and not self.image_path_var.get():
            if not messagebox.askyesno("Подтверждение", "Изображение товара не выбрано. Продолжить без изображения?"):
                return False
                
        return True

    def on_tree_select(self, event):
        """Обработчик выбора товара в дереве"""
        selection = self.tree.selection()
        if selection:
            self.edit_product()
            
    def check_duplicate_url(self, url, exclude_product=None):
        """Проверяет уникальность ссылки Яндекс.Диск"""
        for product_id, product_data in self.products.items():
            if exclude_product and product_id == exclude_product:
                continue
            if product_data.get('zipUrl') == url:
                return {'id': product_id, 'name': product_data['name']}
        return None

    def preview_html(self):
        """Предпросмотр генерируемого HTML"""
        try:
            # Генерируем HTML с учетом предпросмотра
            products_html = self.generate_products_html(for_preview=True)
            
            # Создаем временный файл для предпросмотра
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as temp_file:
                temp_path = temp_file.name
                
                # Подсчитываем статистику для отображения
                total_products = len(self.products)
                products_with_3d = sum(1 for p in self.products.values() if p.get('has_3d', False))
                products_with_images = sum(1 for p in self.products.values() if p.get('has_image', False))
                
                temp_file.write(f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>Предпросмотр товаров FIXCAD MARKET</title>
                    <style>
                        * {{
                            margin: 0;
                            padding: 0;
                            box-sizing: border-box;
                        }}
                        
                        body {{ 
                            font-family: 'Arial', sans-serif; 
                            padding: 20px; 
                            background: #f5f5f5;
                        }}
                        
                        .preview-container {{
                            max-width: 1200px;
                            margin: 0 auto;
                        }}
                        
                        .preview-title {{ 
                            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                            color: white; 
                            padding: 20px; 
                            border-radius: 10px; 
                            text-align: center; 
                            margin-bottom: 30px; 
                            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
                        }}
                        
                        .preview-title h1 {{
                            margin-bottom: 10px;
                            font-size: 28px;
                        }}
                        
                        .preview-info {{
                            display: flex;
                            justify-content: space-around;
                            margin-top: 15px;
                            font-size: 14px;
                            opacity: 0.9;
                        }}
                        
                        .products-grid {{ 
                            display: grid; 
                            grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); 
                            gap: 25px; 
                        }}
                        
                        .product-card {{ 
                            background: white; 
                            border-radius: 15px; 
                            padding: 20px; 
                            box-shadow: 0 10px 30px rgba(0,0,0,0.1);
                            transition: transform 0.2s;
                        }}
                        
                        .product-card:hover {{
                            transform: translateY(-5px);
                            box-shadow: 0 15px 30px rgba(0,0,0,0.2);
                        }}
                        
                        .product-image {{ 
                            width: 100%; 
                            height: 200px; 
                            background: #f0f0f0; 
                            border-radius: 10px; 
                            margin-bottom: 15px; 
                            display: flex; 
                            align-items: center; 
                            justify-content: center; 
                            overflow: hidden; 
                            border: 2px solid #e9ecef;
                            position: relative;
                        }}
                        
                        .product-image img {{ 
                            max-width: 100%; 
                            max-height: 100%; 
                            object-fit: contain;
                        }}
                        
                        .product-image .format-badge {{
                            position: absolute;
                            top: 10px;
                            left: 10px;
                            background: #667eea;
                            color: white;
                            padding: 3px 8px;
                            border-radius: 10px;
                            font-size: 10px;
                            z-index: 1;
                        }}
                        
                        .product-image .model-indicator {{
                            position: absolute;
                            bottom: 10px;
                            right: 10px;
                            background: rgba(0,0,0,0.7);
                            color: white;
                            padding: 5px 10px;
                            border-radius: 15px;
                            font-size: 12px;
                            z-index: 1;
                        }}
                        
                        .product-title {{
                            font-size: 1.2em;
                            font-weight: bold;
                            margin-bottom: 8px;
                            color: #333;
                        }}
                        
                        .product-description {{
                            color: #666;
                            margin-bottom: 12px;
                            font-size: 0.9em;
                        }}
                        
                        .formats-list {{
                            display: flex;
                            flex-wrap: wrap;
                            gap: 5px;
                            margin: 10px 0;
                        }}
                        
                        .format-tag {{
                            background: #e9ecef;
                            padding: 2px 8px;
                            border-radius: 10px;
                            font-size: 0.8em;
                            color: #495057;
                        }}
                        
                        .product-features {{
                            list-style: none;
                            margin: 15px 0;
                            padding-left: 0;
                            font-size: 0.9em;
                        }}
                        
                        .product-features li {{
                            padding: 4px 0;
                            border-bottom: 1px solid #f0f0f0;
                        }}
                        
                        .product-features li:before {{
                            content: "✅ ";
                            margin-right: 8px;
                            font-size: 0.8em;
                        }}
                        
                        .buy-button {{
                            display: block;
                            width: 100%;
                            background: linear-gradient(45deg, #4CAF50, #45a049);
                            color: white;
                            text-decoration: none;
                            padding: 12px;
                            border-radius: 8px;
                            font-weight: bold;
                            text-align: center;
                            margin-top: 10px;
                            border: none;
                            cursor: default;
                        }}
                        
                        .stats-box {{
                            background: white;
                            border-radius: 10px;
                            padding: 15px;
                            margin-bottom: 20px;
                            box-shadow: 0 4px 10px rgba(0,0,0,0.1);
                        }}
                        
                        .stats-grid {{
                            display: grid;
                            grid-template-columns: repeat(3, 1fr);
                            gap: 15px;
                            margin-top: 15px;
                        }}
                        
                        .stat-item {{
                            text-align: center;
                            padding: 10px;
                            background: #f8f9fa;
                            border-radius: 8px;
                        }}
                        
                        .stat-number {{
                            font-size: 24px;
                            font-weight: bold;
                            color: #667eea;
                        }}
                        
                        .stat-label {{
                            font-size: 12px;
                            color: #666;
                            margin-top: 5px;
                        }}

                        .stat-subtext {{
                            font-size: 10px;
                            color: #999;
                            margin-top: 2px;
                        }}
                        
                        @media (max-width: 768px) {{
                            .products-grid {{
                                grid-template-columns: 1fr;
                            }}
                            
                            .stats-grid {{
                                grid-template-columns: 1fr;
                            }}
                            
                            .preview-info {{
                                flex-direction: column;
                                gap: 10px;
                            }}
                        }}
                    </style>
                </head>
                <body>
                    <div class="preview-container">
                        <div class="preview-title">
                            <h1>📐 Предпросмотр товаров FIXCAD MARKET</h1>
                            <p>Здесь показано, как будут выглядеть товары на сайте после обновления</p>
                            <div class="preview-info">
                                <div>🔄 Обновлено: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}</div>
                                <div>📦 Товаров: {total_products}</div>
                                <div>👁️‍🗨️ Режим предпросмотра</div>
                            </div>
                        </div>
                        
                        <div class="stats-box">
                            <h3>📊 Статистика товаров</h3>
                            <div class="stats-grid">
                                <div class="stat-item">
                                    <div class="stat-number">{total_products}</div>
                                    <div class="stat-label">Всего товаров</div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-number">{products_with_3d}</div>
                                    <div class="stat-label">С 3D моделями</div>
                                    <div class="stat-subtext">
                                        из {total_products} товаров
                                    </div>
                                </div>
                                <div class="stat-item">
                                    <div class="stat-number">{products_with_images}</div>
                                    <div class="stat-label">С изображениями</div>
                                    <div class="stat-subtext">
                                        из {total_products} товаров
                                    </div>
                                </div>
                            </div>
                        </div>
                        
                        <div class="products-grid">
                            {products_html}
                        </div>
                        
                        <div style="text-align: center; margin-top: 30px; padding: 20px; background: white; border-radius: 10px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
                            <h3>ℹ️ Информация о предпросмотре</h3>
                            <p style="margin: 10px 0; color: #666;">
                                Это предпросмотр сгенерирован программой "FIXCAD MARKET - Менеджер товаров"
                            </p>
                            <p style="margin: 10px 0; color: #666;">
                                • Изображения показываются из папки <code>images/</code><br>
                                • 3D модели из папки <code>models/</code> в предпросмотре не загружаются<br>
                                • Кнопки "Купить" в предпросмотре неактивны<br>
                                • Для реального обновления сайта нажмите кнопку "Обновить index.html"
                            </p>
                        </div>
                    </div>
                </body>
                </html>
                """)
            
            # Открываем в браузере
            webbrowser.open(f'file://{temp_path}')
            
            self.status_var.set(f"👁️‍🗨️ Предпросмотр открыт ({total_products} товаров)")
            
        except Exception as e:
            self.status_var.set("❌ Ошибка предпросмотра")
            messagebox.showerror("Ошибка", f"Не удалось создать предпросмотр: {str(e)}\n\nПодробности: {traceback.format_exc()}")

    def update_index_html(self):
        """Обновляет index.html с новыми товарами"""
        try:
            if not os.path.exists(self.index_html_path):
                messagebox.showerror("Ошибка", f"Файл {self.index_html_path} не найден!")
                return
            
            with open(self.index_html_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Генерируем HTML для товаров
            products_html = self.generate_products_html()
            
            # Заменяем блок с товарами
            new_content = re.sub(
                r'<div class="products-grid">.*?</div>\s*<!-- Модальное окно формы заказа -->',
                f'<div class="products-grid">\n{products_html}\n    </div>\n\n    <!-- Модальное окно формы заказа -->',
                content,
                flags=re.DOTALL
            )
            
            # Обновляем объект PRODUCT_NAMES в JavaScript
            product_names_js = self.generate_product_names_js()
            new_content = re.sub(
                r'const PRODUCT_NAMES = {.*?};',
                f'const PRODUCT_NAMES = {product_names_js};',
                new_content,
                flags=re.DOTALL
            )
            
            # Обновляем объект PRODUCT_URLS в JavaScript
            product_urls_js = self.generate_product_urls_js()
            new_content = re.sub(
                r'const PRODUCT_URLS = {.*?};',
                f'const PRODUCT_URLS = {product_urls_js};',
                new_content,
                flags=re.DOTALL
            )
            
            # Обновляем микроразметку Schema.org для товаров
            new_content = self.update_schema_markup(new_content)
            
            with open(self.index_html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.status_var.set(f"✅ index.html обновлен ({len(self.products)} товаров)")
            messagebox.showinfo("Успех", f"index.html успешно обновлен!\nДобавлено товаров: {len(self.products)}")
            
        except Exception as e:
            self.status_var.set("❌ Ошибка обновления index.html")
            messagebox.showerror("Ошибка", f"Не удалось обновить index.html: {str(e)}")

    def generate_product_names_js(self):
        """Генерирует JS код для названий товаров"""
        names_js = "{\n"
        for product_id, product_data in self.products.items():
            escaped_name = product_data['name'].replace("'", "\\'")
            names_js += f"    {product_id}: '{escaped_name}',\n"
        names_js += "}"
        return names_js

    def generate_product_urls_js(self):
        """Генерирует JS код для URL товаров"""
        urls_js = "{\n"
        for product_id in self.products.keys():
            # Генерируем URL для ЮMoney с правильной суммой (100 рублей = 10000 копеек)
            url = f"https://yoomoney.ru/quickpay/confirm?receiver=4100119389739602&quickpay-form=button&paymentType=AC&sum=100&label={product_id}"
            urls_js += f"    {product_id}: '{url}',\n"
        urls_js += "}"
        return urls_js

    def generate_products_html(self, for_preview=False):
        """Генерирует HTML код для товаров"""
        html_parts = []
        
        for product_id, product_data in self.products.items():
            has_3d = product_data.get('has_3d', False)
            formats = product_data.get('formats', [])
            has_image = product_data.get('has_image', False)
            
            formats_html = ''.join([f'<span class="format-tag">{fmt}</span>' for fmt in formats])
            features_html = ''.join([f'<li>{feature}</li>' for feature in product_data['contents']])
            
            # Определяем основной формат для бейджа
            main_format = "STL" if has_3d else ("CDW" if "CDW" in formats else formats[0] if formats else "CDW")
            indicator_text = "3D просмотр" if has_3d else "Изображение"
            
            # Если есть изображение - показываем его, иначе placeholder
            if has_image and not for_preview:
                # Для реального сайта - относительные пути
                # Ищем правильное расширение файла
                image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
                image_tag = '<div style="font-size:3em; color:#667eea;">📐</div>'
                for ext in image_extensions:
                    image_path = os.path.join(self.images_dir, f"{product_id}{ext}")
                    if os.path.exists(image_path):
                        image_tag = f'<img src="images/{product_id}{ext}" alt="{product_data["name"]}">'
                        break
            elif has_image and for_preview:
                # Для предпросмотра - абсолютные пути к файлам
                image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
                image_tag = '<div style="font-size:3em; color:#667eea;">📐</div>'
                for ext in image_extensions:
                    image_path = os.path.join(self.images_dir, f"{product_id}{ext}")
                    if os.path.exists(image_path):
                        # Преобразуем путь в формат file:// для браузера
                        abs_path = os.path.abspath(image_path)
                        image_tag = f'<img src="file://{abs_path}" alt="{product_data["name"]}" style="max-width: 100%; max-height: 100%; object-fit: contain;">'
                        break
            else:
                image_tag = f'<div style="font-size:3em; color:#667eea; display: flex; align-items: center; justify-content: center; height: 100%;">📐</div>'
            
            product_html = f"""        <div class="product-card">
            <div class="product-image" {"data-model=\"models/" + product_id + ".stl\"" if has_3d and not for_preview else ""} role="button" tabindex="0" aria-label="Просмотреть изображение {product_data['name']}">
                {image_tag}
                <div class="format-badge">{main_format}</div>
                <div class="model-indicator">{indicator_text}</div>
            </div>
            <div class="product-title">{product_data['name']}</div>
            <div class="product-description">{product_data['description']}</div>
            <div class="formats-list">
                {formats_html}
            </div>
            <ul class="product-features">
                {features_html}
            </ul>
            <button class="buy-button" {"data-product=\"" + product_id + "\"" if not for_preview else ""} aria-label="Купить {product_data['name']} за 100 рублей">
                Купить за 100 руб.
            </button>
        </div>"""
            
            html_parts.append(product_html)
        
        return '\n\n'.join(html_parts)
        
    def update_schema_markup(self, content):
        """Обновляет микроразметку Schema.org для всех товаров"""
        # Генерируем микроразметку для всех товаров
        schema_script = '<script type="application/ld+json">\n'
        schema_script += '    {\n'
        schema_script += '        "@context": "https://schema.org/",\n'
        schema_script += '        "@type": "ItemList",\n'
        schema_script += '        "itemListElement": [\n'
        
        item_list = []
        for i, (product_id, product_data) in enumerate(self.products.items(), 1):
            # Ищем изображение
            image_url = ""
            image_extensions = ['.png', '.jpg', '.jpeg', '.gif', '.bmp']
            for ext in image_extensions:
                if os.path.exists(os.path.join(self.images_dir, f"{product_id}{ext}")):
                    image_url = f"https://fixcad.ru/images/{product_id}{ext}"
                    break
            
            item = f'''            {{
                "@type": "ListItem",
                "position": {i},
                "item": {{
                    "@type": "Product",
                    "name": "{product_data['name']}",
                    "description": "{product_data['description']}",
                    "image": "{image_url if image_url else 'https://fixcad.ru/images/logo.png'}",
                    "offers": {{
                        "@type": "Offer",
                        "price": "100",
                        "priceCurrency": "RUB",
                        "availability": "https://schema.org/InStock"
                    }}
                }}
            }}'''
            item_list.append(item)
        
        schema_script += ',\n'.join(item_list)
        schema_script += '\n        ]\n'
        schema_script += '    }\n'
        schema_script += '</script>'
        
        # Ищем существующую микроразметку ProductCollection и заменяем ее
        if 'ProductCollection' in content:
            # Заменяем существующую микроразметку
            new_content = re.sub(
                r'<script type="application/ld\+json">\s*{\s*"@context":\s*"https://schema\.org",\s*"@type":\s*"ProductCollection".*?</script>',
                schema_script,
                content,
                flags=re.DOTALL
            )
        else:
            # Ищем место для вставки (после других schema скриптов)
            schema_pattern = r'(<script type="application/ld\+json">.*?</script>\s*)'
            matches = list(re.finditer(schema_pattern, content, re.DOTALL))
            
            if matches:
                # Вставляем после последнего schema скрипта
                last_match = matches[-1]
                insert_pos = last_match.end()
                new_content = content[:insert_pos] + '\n' + schema_script + '\n' + content[insert_pos:]
            else:
                # Вставляем перед закрывающим </head>
                new_content = content.replace('</head>', schema_script + '\n</head>')
        
        return new_content

    def update_server_js(self):
        """Обновляет server.js с новыми товарами"""
        try:
            if not os.path.exists(self.server_js_path):
                messagebox.showerror("Ошибка", f"Файл {self.server_js_path} не найден!")
                return
            
            with open(self.server_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Проверяем уникальность всех zipUrl
            duplicates = self.check_all_url_duplicates()
            if duplicates:
                dup_message = "Обнаружены дублирующиеся ссылки Яндекс.Диск:\n\n"
                for url, products in duplicates.items():
                    dup_message += f"Ссылка: {url}\n"
                    for product_id in products:
                        dup_message += f"  - {product_id}: {self.products[product_id]['name']}\n"
                    dup_message += "\n"
                
                dup_message += "Рекомендуется использовать уникальные ссылки для каждого товара."
                if not messagebox.askyesno("Дублирование ссылок", dup_message + "\n\nПродолжить обновление?"):
                    return
            
            # Генерируем JS код для товаров
            products_js = self.generate_products_js()
            
            # Заменяем блок PRODUCTS
            new_content = re.sub(
                r'const PRODUCTS = {.*?};',
                f'const PRODUCTS = {products_js};',
                content,
                flags=re.DOTALL
            )
            
            with open(self.server_js_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            self.status_var.set(f"✅ server.js обновлен ({len(self.products)} товаров)")
            messagebox.showinfo("Успех", f"server.js успешно обновлен!\nДобавлено товаров: {len(self.products)}")
            
        except Exception as e:
            self.status_var.set("❌ Ошибка обновления server.js")
            messagebox.showerror("Ошибка", f"Не удалось обновить server.js: {str(e)}")
            
    def check_all_url_duplicates(self):
        """Проверяет все товары на дублирование ссылок"""
        url_map = {}
        duplicates = {}
        
        for product_id, product_data in self.products.items():
            url = product_data.get('zipUrl', '')
            if url:
                if url not in url_map:
                    url_map[url] = []
                url_map[url].append(product_id)
        
        # Фильтруем только дубликаты
        for url, products in url_map.items():
            if len(products) > 1:
                duplicates[url] = products
                
        return duplicates

    def generate_products_js(self):
        """Генерирует JS код для товаров"""
        products_js = "{\n"
        
        for product_id, product_data in self.products.items():
            # Для server.js нам не нужны форматы и has_3d
            server_data = {
                'name': product_data['name'].replace("'", "\\'"),
                'description': product_data['description'].replace("'", "\\'"),
                'zipUrl': product_data['zipUrl'],
                'zipName': product_data['zipName'],
                'contents': product_data['contents']
            }
            
            contents_js = "[\n      " + ",\n      ".join([f"'{item}'" for item in server_data['contents']]) + "\n    ]"
            
            product_js = f"""  {product_id}: {{
    name: '{server_data['name']}',
    description: '{server_data['description']}',
    zipUrl: '{server_data['zipUrl']}',
    zipName: '{server_data['zipName']}',
    contents: {contents_js}
  }},"""
            products_js += product_js + "\n"
        
        products_js += "}"
        return products_js

    def update_both(self):
        """Обновляет оба файла"""
        self.update_server_js()
        self.update_index_html()
        messagebox.showinfo("Успех", "Оба файла успешно обновлены!")

    def move_up(self):
        """Перемещает выбранный товар вверх"""
        selection = self.tree.selection()
        if not selection:
            return
            
        current_index = self.tree.index(selection[0])
        if current_index == 0:
            return
        
        # Получаем список всех товаров в порядке отображения
        product_ids = list(self.products.keys())
        
        # Меняем местами текущий товар с предыдущим
        product_ids[current_index], product_ids[current_index - 1] = product_ids[current_index - 1], product_ids[current_index]
        
        # Создаем новый упорядоченный словарь
        new_products = {}
        for pid in product_ids:
            new_products[pid] = self.products[pid]
        
        self.products = new_products
        self.refresh_tree()
        
        # Выделяем перемещенный товар
        items = self.tree.get_children()
        if items and current_index - 1 < len(items):
            self.tree.selection_set(items[current_index - 1])

    def move_down(self):
        """Перемещает выбранный товар вниз"""
        selection = self.tree.selection()
        if not selection:
            return
            
        current_index = self.tree.index(selection[0])
        items = self.tree.get_children()
        
        if current_index == len(items) - 1:
            return
        
        # Получаем список всех товаров в порядке отображения
        product_ids = list(self.products.keys())
        
        # Меняем местами текущий товар со следующим
        product_ids[current_index], product_ids[current_index + 1] = product_ids[current_index + 1], product_ids[current_index]
        
        # Создаем новый упорядоченный словарь
        new_products = {}
        for pid in product_ids:
            new_products[pid] = self.products[pid]
        
        self.products = new_products
        self.refresh_tree()
        
        # Выделяем перемещенный товар
        items = self.tree.get_children()
        if items and current_index + 1 < len(items):
            self.tree.selection_set(items[current_index + 1])

    def cleanup_temp_files(self):
        """Очищает временные файлы предпросмотра"""
        try:
            # Ищем временные HTML файлы
            temp_dir = tempfile.gettempdir()
            deleted_files = []
            
            for filename in os.listdir(temp_dir):
                if filename.startswith('tmp') and filename.endswith('.html'):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        # Проверяем, что файл достаточно старый (старше 1 часа)
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > 3600:  # 1 час
                            os.remove(file_path)
                            deleted_files.append(filename)
                    except:
                        pass
            
            if deleted_files:
                messagebox.showinfo("Очистка", f"Удалено временных файлов: {len(deleted_files)}")
                self.status_var.set(f"🧹 Удалено {len(deleted_files)} временных файлов")
            else:
                messagebox.showinfo("Очистка", "Временные файлы не найдены или все актуальны")
                self.status_var.set("✅ Нет файлов для очистки")
                
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось очистить временные файлы: {str(e)}")
            self.status_var.set("❌ Ошибка очистки")

    def auto_cleanup(self):
        """Автоматическая очистка старых временных файлов"""
        try:
            temp_dir = tempfile.gettempdir()
            deleted_count = 0
            
            for filename in os.listdir(temp_dir):
                if filename.startswith('tmp') and filename.endswith('.html'):
                    file_path = os.path.join(temp_dir, filename)
                    try:
                        # Удаляем файлы старше 24 часов
                        file_age = time.time() - os.path.getmtime(file_path)
                        if file_age > 86400:  # 24 часа
                            os.remove(file_path)
                            deleted_count += 1
                    except:
                        pass
            
            if deleted_count > 0:
                print(f"Автоматически удалено {deleted_count} старых временных файлов")
                
        except Exception as e:
            print(f"Ошибка автоматической очистки: {e}")

def main():
    root = tk.Tk()
    app = ProductManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()