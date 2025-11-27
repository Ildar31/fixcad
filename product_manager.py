import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import json
import os
import re
import shutil

class ProductManager:
    def __init__(self, root):
        self.root = root
        self.root.title("FIXCAD MARKET - Менеджер товаров")
        
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
        
        # Устанавливаем минимальный размер окна
        self.root.update()
        self.root.minsize(1000, 700)
        
    def setup_ui(self):
        # Основной фрейм
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="Управление товарами FIXCAD MARKET", 
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
        
        self.cdw_var = tk.BooleanVar(value=True)
        self.spw_var = tk.BooleanVar(value=True)
        self.a3d_var = tk.BooleanVar(value=True)
        self.m3d_var = tk.BooleanVar(value=True)
        self.stl_var = tk.BooleanVar(value=False)
        
        ttk.Checkbutton(formats_frame, text="CDW", variable=self.cdw_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_frame, text="SPW", variable=self.spw_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_frame, text="A3D", variable=self.a3d_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_frame, text="M3D", variable=self.m3d_var).pack(side=tk.LEFT)
        ttk.Checkbutton(formats_frame, text="STL", variable=self.stl_var).pack(side=tk.LEFT)
        
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
        
        ttk.Button(list_buttons_frame, text="Дублировать", command=self.duplicate_product).pack(side=tk.LEFT, padx=5)
        ttk.Button(list_buttons_frame, text="Удалить", command=self.delete_product).pack(side=tk.LEFT, padx=5)
        
        # Кнопки экспорта
        export_frame = ttk.Frame(main_frame)
        export_frame.grid(row=2, column=0, columnspan=2, pady=20)
        
        ttk.Button(export_frame, text="Обновить index.html", command=self.update_index_html).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Обновить server.js", command=self.update_server_js).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Обновить оба файла", command=self.update_both).pack(side=tk.LEFT, padx=5)
        
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
        
        # Копируем файлы
        self.copy_product_files(product_id)
        
        # Собираем форматы
        formats = []
        if self.cdw_var.get(): formats.append("CDW")
        if self.spw_var.get(): formats.append("SPW")
        if self.a3d_var.get(): formats.append("A3D")
        if self.m3d_var.get(): formats.append("M3D")
        if self.stl_var.get(): formats.append("STL")
            
        self.products[product_id] = {
            'name': self.name_var.get().strip(),
            'description': self.desc_var.get().strip(),
            'zipUrl': self.zip_url_var.get().strip(),
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

    def refresh_tree(self):
        """Обновляет дерево товаров"""
        for item in self.tree.get_children():
            self.tree.delete(item)
            
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
        
        # Копируем файлы
        self.copy_product_files(product_id)
        
        # Собираем форматы
        formats = []
        if self.cdw_var.get(): formats.append("CDW")
        if self.spw_var.get(): formats.append("SPW")
        if self.a3d_var.get(): formats.append("A3D")
        if self.m3d_var.get(): formats.append("M3D")
        if self.stl_var.get(): formats.append("STL")
            
        self.products[product_id] = {
            'name': self.name_var.get().strip(),
            'description': self.desc_var.get().strip(),
            'zipUrl': self.zip_url_var.get().strip(),
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
            
            with open(self.index_html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            messagebox.showinfo("Успех", "index.html успешно обновлен!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить index.html: {str(e)}")

    def generate_products_html(self):
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
            if has_image:
                image_content = f'<img src="images/{product_id}.png" alt="{product_data["name"]}">'
            else:
                image_content = f'<div style="font-size:3em;">📐</div>'
            
            product_html = f"""        <div class="product-card">
            <div class="product-image" data-image="images/{product_id}.png" {"data-model=\"models/" + product_id + ".stl\"" if has_3d else ""}>
                {image_content}
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
            <button class="buy-button" data-product="{product_id}">
                Купить за 100 руб.
            </button>
        </div>"""
            
            html_parts.append(product_html)
        
        return '\n\n'.join(html_parts)

    def update_server_js(self):
        """Обновляет server.js с новыми товарами"""
        try:
            if not os.path.exists(self.server_js_path):
                messagebox.showerror("Ошибка", f"Файл {self.server_js_path} не найден!")
                return
            
            with open(self.server_js_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
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
            
            messagebox.showinfo("Успех", "server.js успешно обновлен!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить server.js: {str(e)}")

    def generate_products_js(self):
        """Генерирует JS код для товаров"""
        products_js = "{\n"
        
        for product_id, product_data in self.products.items():
            # Для server.js нам не нужны форматы и has_3d
            server_data = {
                'name': product_data['name'],
                'description': product_data['description'],
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

def main():
    root = tk.Tk()
    app = ProductManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()