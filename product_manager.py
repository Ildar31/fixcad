import tkinter as tk
from tkinter import ttk, messagebox, filedialog, Menu
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
        self.setup_context_menu()
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
        
        # Контекстное меню для поля ID
        self.product_id_context_menu = Menu(self.product_id_entry, tearoff=0)
        self.product_id_context_menu.add_command(label="Копировать", command=self.copy_product_id)
        self.product_id_context_menu.add_command(label="Вставить", command=self.paste_to_product_id)
        self.product_id_context_menu.add_separator()
        self.product_id_context_menu.add_command(label="Вырезать", command=self.cut_product_id)
        self.product_id_context_menu.add_command(label="Выделить все", command=lambda: self.product_id_entry.select_range(0, tk.END))
        
        ttk.Label(form_frame, text="Название:").grid(row=1, column=0, sticky=tk.W, pady=2)
        self.name_var = tk.StringVar()
        self.name_entry = ttk.Entry(form_frame, textvariable=self.name_var, width=30)
        self.name_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Контекстное меню для поля названия
        self.name_context_menu = Menu(self.name_entry, tearoff=0)
        self.name_context_menu.add_command(label="Копировать", command=self.copy_name)
        self.name_context_menu.add_command(label="Вставить", command=self.paste_to_name)
        self.name_context_menu.add_separator()
        self.name_context_menu.add_command(label="Вырезать", command=self.cut_name)
        self.name_context_menu.add_command(label="Выделить все", command=lambda: self.name_entry.select_range(0, tk.END))
        
        ttk.Label(form_frame, text="Описание:").grid(row=2, column=0, sticky=tk.W, pady=2)
        self.desc_var = tk.StringVar()
        self.desc_entry = ttk.Entry(form_frame, textvariable=self.desc_var, width=30)
        self.desc_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Контекстное меню для поля описания
        self.desc_context_menu = Menu(self.desc_entry, tearoff=0)
        self.desc_context_menu.add_command(label="Копировать", command=self.copy_desc)
        self.desc_context_menu.add_command(label="Вставить", command=self.paste_to_desc)
        self.desc_context_menu.add_separator()
        self.desc_context_menu.add_command(label="Вырезать", command=self.cut_desc)
        self.desc_context_menu.add_command(label="Выделить все", command=lambda: self.desc_entry.select_range(0, tk.END))
        
        ttk.Label(form_frame, text="Ссылка Яндекс.Диск:").grid(row=3, column=0, sticky=tk.W, pady=2)
        self.zip_url_var = tk.StringVar()
        self.zip_url_entry = ttk.Entry(form_frame, textvariable=self.zip_url_var, width=40)
        self.zip_url_entry.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Контекстное меню для поля ссылки
        self.zip_url_context_menu = Menu(self.zip_url_entry, tearoff=0)
        self.zip_url_context_menu.add_command(label="Копировать", command=self.copy_zip_url)
        self.zip_url_context_menu.add_command(label="Вставить", command=self.paste_to_zip_url)
        self.zip_url_context_menu.add_separator()
        self.zip_url_context_menu.add_command(label="Вырезать", command=self.cut_zip_url)
        self.zip_url_context_menu.add_command(label="Выделить все", command=lambda: self.zip_url_entry.select_range(0, tk.END))
        
        ttk.Label(form_frame, text="Имя архива:").grid(row=4, column=0, sticky=tk.W, pady=2)
        self.zip_name_var = tk.StringVar()
        self.zip_name_entry = ttk.Entry(form_frame, textvariable=self.zip_name_var, width=30)
        self.zip_name_entry.grid(row=4, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Контекстное меню для поля имени архива
        self.zip_name_context_menu = Menu(self.zip_name_entry, tearoff=0)
        self.zip_name_context_menu.add_command(label="Копировать", command=self.copy_zip_name)
        self.zip_name_context_menu.add_command(label="Вставить", command=self.paste_to_zip_name)
        self.zip_name_context_menu.add_separator()
        self.zip_name_context_menu.add_command(label="Вырезать", command=self.cut_zip_name)
        self.zip_name_context_menu.add_command(label="Выделить все", command=lambda: self.zip_name_entry.select_range(0, tk.END))
        
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
        self.image_path_entry = ttk.Entry(file_frame, textvariable=self.image_path_var, width=25)
        self.image_path_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(file_frame, text="Выбрать...", command=self.select_image).pack(side=tk.LEFT)
        
        # Контекстное меню для поля пути к изображению
        self.image_path_context_menu = Menu(self.image_path_entry, tearoff=0)
        self.image_path_context_menu.add_command(label="Копировать", command=self.copy_image_path)
        self.image_path_context_menu.add_command(label="Вставить", command=self.paste_to_image_path)
        self.image_path_context_menu.add_separator()
        self.image_path_context_menu.add_command(label="Вырезать", command=self.cut_image_path)
        self.image_path_context_menu.add_command(label="Выделить все", command=lambda: self.image_path_entry.select_range(0, tk.END))
        
        ttk.Label(form_frame, text="3D модель (STL):").grid(row=8, column=0, sticky=tk.W, pady=2)
        model_frame = ttk.Frame(form_frame)
        model_frame.grid(row=8, column=1, sticky=(tk.W, tk.E), pady=2)
        
        self.model_path_var = tk.StringVar()
        self.model_path_entry = ttk.Entry(model_frame, textvariable=self.model_path_var, width=25)
        self.model_path_entry.pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(model_frame, text="Выбрать...", command=self.select_model).pack(side=tk.LEFT)
        
        # Контекстное меню для поля пути к модели
        self.model_path_context_menu = Menu(self.model_path_entry, tearoff=0)
        self.model_path_context_menu.add_command(label="Копировать", command=self.copy_model_path)
        self.model_path_context_menu.add_command(label="Вставить", command=self.paste_to_model_path)
        self.model_path_context_menu.add_separator()
        self.model_path_context_menu.add_command(label="Вырезать", command=self.cut_model_path)
        self.model_path_context_menu.add_command(label="Выделить все", command=lambda: self.model_path_entry.select_range(0, tk.END))
        
        # Содержимое архива
        ttk.Label(form_frame, text="Содержимое архива:").grid(row=9, column=0, sticky=tk.W, pady=2)
        self.contents_text = tk.Text(form_frame, width=30, height=4)
        self.contents_text.grid(row=9, column=1, sticky=(tk.W, tk.E), pady=2)
        
        # Контекстное меню для текстового поля содержимого архива
        self.contents_text_context_menu = Menu(self.contents_text, tearoff=0)
        self.contents_text_context_menu.add_command(label="Копировать", command=self.copy_contents_text)
        self.contents_text_context_menu.add_command(label="Вставить", command=self.paste_to_contents_text)
        self.contents_text_context_menu.add_separator()
        self.contents_text_context_menu.add_command(label="Вырезать", command=self.cut_contents_text)
        self.contents_text_context_menu.add_command(label="Выделить все", command=lambda: self.contents_text.tag_add(tk.SEL, "1.0", tk.END))
        
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
        
        # Контекстное меню для таблицы
        self.tree_context_menu = Menu(self.tree, tearoff=0)
        self.tree_context_menu.add_command(label="Копировать ID", command=self.copy_selected_id)
        self.tree_context_menu.add_command(label="Копировать название", command=self.copy_selected_name)
        self.tree_context_menu.add_separator()
        self.tree_context_menu.add_command(label="Вставить ID в форму", command=self.paste_id_from_selected)
        
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
        
        ttk.Button(export_frame, text="Обновить index.html", command=self.update_index_html).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Обновить server.js", command=self.update_server_js).pack(side=tk.LEFT, padx=5)
        ttk.Button(export_frame, text="Обновить оба файла", command=self.update_both).pack(side=tk.LEFT, padx=5)
        
        # Кнопки копирования/вставки
        clipboard_frame = ttk.Frame(main_frame)
        clipboard_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        ttk.Button(clipboard_frame, text="Копировать всю форму", command=self.copy_all_form).pack(side=tk.LEFT, padx=5)
        ttk.Button(clipboard_frame, text="Вставить ID", command=self.paste_to_product_id).pack(side=tk.LEFT, padx=5)
        ttk.Button(clipboard_frame, text="Горячие клавиши", command=self.show_hotkeys).pack(side=tk.LEFT, padx=5)
        
        # Привязка событий
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_tree_context_menu)
        
        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(1, weight=1)
        form_frame.columnconfigure(1, weight=1)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)
        
    def setup_context_menu(self):
        """Настройка контекстных меню для всех текстовых полей"""
        # Привязка правой кнопки мыши для всех полей ввода
        entries = [
            (self.product_id_entry, self.product_id_context_menu),
            (self.name_entry, self.name_context_menu),
            (self.desc_entry, self.desc_context_menu),
            (self.zip_url_entry, self.zip_url_context_menu),
            (self.zip_name_entry, self.zip_name_context_menu),
            (self.image_path_entry, self.image_path_context_menu),
            (self.model_path_entry, self.model_path_context_menu)
        ]
        
        for entry, menu in entries:
            entry.bind("<Button-3>", lambda event, m=menu: self.show_context_menu(event, m))
        
        # Для текстового поля
        self.contents_text.bind("<Button-3>", lambda event: self.show_context_menu(event, self.contents_text_context_menu))
        
        # Горячие клавиши
        self.root.bind("<Control-c>", self.copy_from_focused)
        self.root.bind("<Control-v>", self.paste_to_focused)
        self.root.bind("<Control-x>", self.cut_from_focused)
        self.root.bind("<Control-a>", self.select_all_in_focused)
        
    def show_context_menu(self, event, menu):
        """Показывает контекстное меню"""
        try:
            menu.tk_popup(event.x_root, event.y_root)
        finally:
            menu.grab_release()
            
    def show_tree_context_menu(self, event):
        """Показывает контекстное меню для таблицы"""
        try:
            self.tree_context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.tree_context_menu.grab_release()
    
    # Методы для копирования из полей формы
    def copy_product_id(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.product_id_var.get())
        
    def copy_name(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.name_var.get())
        
    def copy_desc(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.desc_var.get())
        
    def copy_zip_url(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.zip_url_var.get())
        
    def copy_zip_name(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.zip_name_var.get())
        
    def copy_image_path(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.image_path_var.get())
        
    def copy_model_path(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.model_path_var.get())
        
    def copy_contents_text(self):
        self.root.clipboard_clear()
        self.root.clipboard_append(self.contents_text.get("1.0", tk.END).strip())
    
    # Методы для вставки в поля формы
    def paste_to_product_id(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.product_id_var.set(clipboard_text)
        except:
            pass
            
    def paste_to_name(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.name_var.set(clipboard_text)
        except:
            pass
            
    def paste_to_desc(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.desc_var.set(clipboard_text)
        except:
            pass
            
    def paste_to_zip_url(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.zip_url_var.set(clipboard_text)
        except:
            pass
            
    def paste_to_zip_name(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.zip_name_var.set(clipboard_text)
        except:
            pass
            
    def paste_to_image_path(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.image_path_var.set(clipboard_text)
        except:
            pass
            
    def paste_to_model_path(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.model_path_var.set(clipboard_text)
        except:
            pass
            
    def paste_to_contents_text(self):
        try:
            clipboard_text = self.root.clipboard_get()
            self.contents_text.insert(tk.INSERT, clipboard_text)
        except:
            pass
    
    # Методы для вырезания
    def cut_product_id(self):
        self.copy_product_id()
        self.product_id_var.set("")
        
    def cut_name(self):
        self.copy_name()
        self.name_var.set("")
        
    def cut_desc(self):
        self.copy_desc()
        self.desc_var.set("")
        
    def cut_zip_url(self):
        self.copy_zip_url()
        self.zip_url_var.set("")
        
    def cut_zip_name(self):
        self.copy_zip_name()
        self.zip_name_var.set("")
        
    def cut_image_path(self):
        self.copy_image_path()
        self.image_path_var.set("")
        
    def cut_model_path(self):
        self.copy_model_path()
        self.model_path_var.set("")
        
    def cut_contents_text(self):
        self.copy_contents_text()
        self.contents_text.delete("1.0", tk.END)
    
    # Методы для работы с таблицей
    def copy_selected_id(self):
        selection = self.tree.selection()
        if selection:
            product_id = self.tree.item(selection[0])['values'][0]
            self.root.clipboard_clear()
            self.root.clipboard_append(product_id)
            
    def copy_selected_name(self):
        selection = self.tree.selection()
        if selection:
            product_name = self.tree.item(selection[0])['values'][1]
            self.root.clipboard_clear()
            self.root.clipboard_append(product_name)
            
    def paste_id_from_selected(self):
        selection = self.tree.selection()
        if selection:
            product_id = self.tree.item(selection[0])['values'][0]
            self.product_id_var.set(product_id)
    
    # Методы для горячих клавиш
    def copy_from_focused(self, event=None):
        """Копирует текст из активного поля"""
        widget = self.root.focus_get()
        if widget == self.product_id_entry:
            self.copy_product_id()
        elif widget == self.name_entry:
            self.copy_name()
        elif widget == self.desc_entry:
            self.copy_desc()
        elif widget == self.zip_url_entry:
            self.copy_zip_url()
        elif widget == self.zip_name_entry:
            self.copy_zip_name()
        elif widget == self.image_path_entry:
            self.copy_image_path()
        elif widget == self.model_path_entry:
            self.copy_model_path()
        elif widget == self.contents_text:
            self.copy_contents_text()
        return "break"
        
    def paste_to_focused(self, event=None):
        """Вставляет текст в активное поле"""
        widget = self.root.focus_get()
        if widget == self.product_id_entry:
            self.paste_to_product_id()
        elif widget == self.name_entry:
            self.paste_to_name()
        elif widget == self.desc_entry:
            self.paste_to_desc()
        elif widget == self.zip_url_entry:
            self.paste_to_zip_url()
        elif widget == self.zip_name_entry:
            self.paste_to_zip_name()
        elif widget == self.image_path_entry:
            self.paste_to_image_path()
        elif widget == self.model_path_entry:
            self.paste_to_model_path()
        elif widget == self.contents_text:
            self.paste_to_contents_text()
        return "break"
        
    def cut_from_focused(self, event=None):
        """Вырезает текст из активного поля"""
        widget = self.root.focus_get()
        if widget == self.product_id_entry:
            self.cut_product_id()
        elif widget == self.name_entry:
            self.cut_name()
        elif widget == self.desc_entry:
            self.cut_desc()
        elif widget == self.zip_url_entry:
            self.cut_zip_url()
        elif widget == self.zip_name_entry:
            self.cut_zip_name()
        elif widget == self.image_path_entry:
            self.cut_image_path()
        elif widget == self.model_path_entry:
            self.cut_model_path()
        elif widget == self.contents_text:
            self.cut_contents_text()
        return "break"
        
    def select_all_in_focused(self, event=None):
        """Выделяет весь текст в активном поле"""
        widget = self.root.focus_get()
        if hasattr(widget, 'select_range'):
            widget.select_range(0, tk.END)
        elif widget == self.contents_text:
            widget.tag_add(tk.SEL, "1.0", tk.END)
        return "break"
    
    def copy_all_form(self):
        """Копирует все данные формы в буфер обмена как структурированный текст"""
        form_data = {
            "ID товара": self.product_id_var.get(),
            "Название": self.name_var.get(),
            "Описание": self.desc_var.get(),
            "Ссылка Яндекс.Диск": self.zip_url_var.get(),
            "Имя архива": self.zip_name_var.get(),
            "Форматы": {
                "CDW": self.cdw_var.get(),
                "SPW": self.spw_var.get(),
                "A3D": self.a3d_var.get(),
                "M3D": self.m3d_var.get(),
                "STL": self.stl_var.get(),
                "STEP": self.step_var.get(),
                "PDF": self.pdf_var.get(),
                "DOC": self.doc_var.get(),
                "XLS": self.xls_var.get(),
                "TXT": self.txt_var.get(),
                "EXE": self.exe_var.get()
            },
            "Есть 3D модель": self.has_3d_var.get(),
            "Путь к изображению": self.image_path_var.get(),
            "Путь к 3D модели": self.model_path_var.get(),
            "Содержимое архива": self.contents_text.get("1.0", tk.END).strip()
        }
        
        clipboard_text = "=== ДАННЫЕ ФОРМЫ ТОВАРА ===\n\n"
        for key, value in form_data.items():
            if isinstance(value, dict):
                clipboard_text += f"{key}:\n"
                for sub_key, sub_value in value.items():
                    clipboard_text += f"  {sub_key}: {'✓' if sub_value else '✗'}\n"
            else:
                if key == "Содержимое архива":
                    clipboard_text += f"{key}:\n{value}\n"
                else:
                    clipboard_text += f"{key}: {value}\n"
            clipboard_text += "\n"
        
        self.root.clipboard_clear()
        self.root.clipboard_append(clipboard_text)
        messagebox.showinfo("Успех", "Все данные формы скопированы в буфер обмена!")
    
    def show_hotkeys(self):
        """Показывает справку по горячим клавишам"""
        hotkeys_info = """
Горячие клавиши:

Общие:
Ctrl+C - Копировать из активного поля
Ctrl+V - Вставить в активное поле
Ctrl+X - Вырезать из активного поля
Ctrl+A - Выделить весь текст в активном поле

Контекстное меню:
Правая кнопка мыши на любом текстовом поле - меню Копировать/Вставить

В таблице товаров:
Правая кнопка мыши - меню для копирования ID/названия
"""
        messagebox.showinfo("Горячие клавиши", hotkeys_info)
        
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
        if self.step_var.get(): formats.append("STEP")
        if self.pdf_var.get(): formats.append("PDF")
        if self.doc_var.get(): formats.append("DOC")
        if self.xls_var.get(): formats.append("XLS")
        if self.txt_var.get(): formats.append("TXT")
        if self.exe_var.get(): formats.append("EXE")
            
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
        
        # Копируем файлы
        self.copy_product_files(product_id)
        
        # Собираем форматы
        formats = []
        if self.cdw_var.get(): formats.append("CDW")
        if self.spw_var.get(): formats.append("SPW")
        if self.a3d_var.get(): formats.append("A3D")
        if self.m3d_var.get(): formats.append("M3D")
        if self.stl_var.get(): formats.append("STL")
        if self.step_var.get(): formats.append("STEP")
        if self.pdf_var.get(): formats.append("PDF")
        if self.doc_var.get(): formats.append("DOC")
        if self.xls_var.get(): formats.append("XLS")
        if self.txt_var.get(): formats.append("TXT")
        if self.exe_var.get(): formats.append("EXE")
            
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
            
            with open(self.index_html_path, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            messagebox.showinfo("Успех", "index.html успешно обновлен!")
            
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось обновить index.html: {str(e)}")

    def generate_product_names_js(self):
        """Генерирует JS код для названий товаров"""
        names_js = "{\n"
        for product_id, product_data in self.products.items():
            names_js += f"    {product_id}: '{product_data['name']}',\n"
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

def main():
    root = tk.Tk()
    app = ProductManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()