import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import sqlite3

current_user = None  # Глобальная переменная, объявленная до ее использования

class PlaceholderEntry(ttk.Entry):
    def __init__(self, master=None, placeholder="", color='grey', *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.placeholder = placeholder
        self.placeholder_color = color
        self.default_fg_color = self['foreground']
        self.placeholder_active = True

        self.bind("<FocusIn>", self._clear_placeholder)
        self.bind("<FocusOut>", self._add_placeholder)
        self.bind("<Key>", self._check_placeholder)

        self._add_placeholder()

    def _clear_placeholder(self, e):
        if self.placeholder_active:
            self.delete(0, tk.END)
            self['foreground'] = self.default_fg_color
            self.placeholder_active = False

    def _add_placeholder(self, e=None):
        if not self.get():
            self.insert(0, self.placeholder)
            self['foreground'] = self.placeholder_color
            self.placeholder_active = True

    def _check_placeholder(self, e):
        if self.placeholder_active:
            self._clear_placeholder(e)

# Функции для работы с клиентами
def add_client_to_db(fullname, email, phone, discount, is_regular):
    if not (fullname and email and phone):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO clients (fullname, email, phone, discount, is_regular) VALUES (?, ?, ?, ?, ?)',
                   (fullname, email, phone, discount, is_regular))
    conn.commit()
    conn.close()

    tree_clients.insert('', 'end', values=(fullname, email, phone, discount, is_regular))


def open_add_client_window():
    add_client_window = tk.Toplevel(root)
    add_client_window.title("Добавить клиента")
    add_client_window.geometry("300x400")
    add_client_window.configure(bg="white")

    label_title = tk.Label(add_client_window, text="Клиент", font=("Helvetica", 18, "bold"), bg="white")
    label_title.pack(pady=20)

    entry_fullname = PlaceholderEntry(add_client_window, placeholder="ФИО", font=("Helvetica", 12), width=30)
    entry_fullname.pack(pady=5, ipady=5)

    entry_email = PlaceholderEntry(add_client_window, placeholder="Почта", font=("Helvetica", 12), width=30)
    entry_email.pack(pady=5, ipady=5)

    entry_phone = PlaceholderEntry(add_client_window, placeholder="Телефон", font=("Helvetica", 12), width=30)
    entry_phone.pack(pady=5, ipady=5)

    entry_discount = PlaceholderEntry(add_client_window, placeholder="% скидки", font=("Helvetica", 12), width=30)
    entry_discount.pack(pady=5, ipady=5)

    is_regular = tk.BooleanVar()
    checkbox_regular = tk.Checkbutton(add_client_window, text="Постоянный клиент +10%", variable=is_regular, font=("Helvetica", 12), bg="white")
    checkbox_regular.pack(pady=5)

    def on_add():
        discount = int(entry_discount.get()) if entry_discount.get().isdigit() else 0
        add_client_to_db(entry_fullname.get(), entry_email.get(), entry_phone.get(), discount, is_regular.get())
        add_client_window.destroy()

    btn_add = tk.Button(add_client_window, text="Добавить", font=("Helvetica", 14), bg="black", fg="white", command=on_add)
    btn_add.pack(pady=20)


def open_edit_client_window(item):
    selected_item = tree_clients.item(item)
    values = selected_item['values']

    edit_client_window = tk.Toplevel(root)
    edit_client_window.title("Редактировать клиента")
    edit_client_window.geometry("300x400")
    edit_client_window.configure(bg="white")

    label_title = tk.Label(edit_client_window, text="Клиент", font=("Helvetica", 18, "bold"), bg="white")
    label_title.pack(pady=20)

    entry_fullname = tk.Entry(edit_client_window, font=("Helvetica", 12), width=30)
    entry_fullname.pack(pady=5, ipady=5)
    entry_fullname.insert(0, values[0])

    entry_email = tk.Entry(edit_client_window, font=("Helvetica", 12), width=30)
    entry_email.pack(pady=5, ipady=5)
    entry_email.insert(0, values[1])

    entry_phone = tk.Entry(edit_client_window, font=("Helvetica", 12), width=30)
    entry_phone.pack(pady=5, ipady=5)
    entry_phone.insert(0, values[2])

    entry_discount = tk.Entry(edit_client_window, font=("Helvetica", 12), width=30)
    entry_discount.pack(pady=5, ipady=5)
    entry_discount.insert(0, values[3])

    is_regular = tk.BooleanVar()
    checkbox_regular = tk.Checkbutton(edit_client_window, text="Постоянный клиент +10%", variable=is_regular, font=("Helvetica", 12), bg="white")
    checkbox_regular.pack(pady=5)
    is_regular.set(values[4])

    def on_save():
        new_fullname = entry_fullname.get()
        new_email = entry_email.get()
        new_phone = entry_phone.get()
        new_discount = int(entry_discount.get()) if entry_discount.get().isdigit() else 0
        new_is_regular = is_regular.get()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE clients SET fullname=?, email=?, phone=?, discount=?, is_regular=? WHERE fullname=? AND email=? AND phone=?',
                       (new_fullname, new_email, new_phone, new_discount, new_is_regular, values[0], values[1], values[2]))
        conn.commit()
        conn.close()

        tree_clients.item(item, values=(new_fullname, new_email, new_phone, new_discount, new_is_regular))
        edit_client_window.destroy()

    def on_delete():
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM clients WHERE fullname=? AND email=? AND phone=?', (values[0], values[1], values[2]))
        conn.commit()
        conn.close()

        tree_clients.delete(item)
        edit_client_window.destroy()

    btn_save = tk.Button(edit_client_window, text="Сохранить", font=("Helvetica", 14), bg="black", fg="white", command=on_save)
    btn_save.pack(pady=10, side=tk.LEFT, padx=10)

    btn_delete = tk.Button(edit_client_window, text="Удалить", font=("Helvetica", 14), bg="white", fg="black", command=on_delete)
    btn_delete.pack(pady=10, side=tk.LEFT, padx=10)


# Функции для работы с отелями
def add_hotel_to_db(name, location, rating):
    if not (name and location and rating):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO hotels (name, location, rating) VALUES (?, ?, ?)', (name, location, rating))
    conn.commit()
    conn.close()

    tree_hotels.insert('', 'end', values=(name, location, rating))


def open_add_hotel_window():
    add_hotel_window = tk.Toplevel(root)
    add_hotel_window.title("Добавить отель")
    add_hotel_window.geometry("300x300")
    add_hotel_window.configure(bg="white")

    label_title = tk.Label(add_hotel_window, text="Отель", font=("Helvetica", 18, "bold"), bg="white")
    label_title.pack(pady=20)

    entry_name = PlaceholderEntry(add_hotel_window, placeholder="Название", font=("Helvetica", 12), width=30)
    entry_name.pack(pady=5, ipady=5)

    entry_location = PlaceholderEntry(add_hotel_window, placeholder="Расположение", font=("Helvetica", 12), width=30)
    entry_location.pack(pady=5, ipady=5)

    entry_rating = PlaceholderEntry(add_hotel_window, placeholder="Рейтинг", font=("Helvetica", 12), width=30)
    entry_rating.pack(pady=5, ipady=5)

    def on_add():
        add_hotel_to_db(entry_name.get(), entry_location.get(), entry_rating.get())
        add_hotel_window.destroy()

    btn_add = tk.Button(add_hotel_window, text="Добавить", font=("Helvetica", 14), bg="black", fg="white", command=on_add)
    btn_add.pack(pady=20)


def open_edit_hotel_window(item):
    selected_item = tree_hotels.item(item)
    values = selected_item['values']

    edit_hotel_window = tk.Toplevel(root)
    edit_hotel_window.title("Редактировать отель")
    edit_hotel_window.geometry("300x400")
    edit_hotel_window.configure(bg="white")

    label_title = tk.Label(edit_hotel_window, text="Отель", font=("Helvetica", 18, "bold"), bg="white")
    label_title.pack(pady=20)

    entry_name = tk.Entry(edit_hotel_window, font=("Helvetica", 12), width=30)
    entry_name.pack(pady=5, ipady=5)
    entry_name.insert(0, values[0])

    entry_location = tk.Entry(edit_hotel_window, font=("Helvetica", 12), width=30)
    entry_location.pack(pady=5, ipady=5)
    entry_location.insert(0, values[1])

    entry_rating = tk.Entry(edit_hotel_window, font=("Helvetica", 12), width=30)
    entry_rating.pack(pady=5, ipady=5)
    entry_rating.insert(0, values[2])

    def on_save():
        new_name = entry_name.get()
        new_location = entry_location.get()
        new_rating = entry_rating.get()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE hotels SET name=?, location=?, rating=? WHERE name=? AND location=? AND rating=?',
                       (new_name, new_location, new_rating, values[0], values[1], values[2]))
        conn.commit()
        conn.close()

        tree_hotels.item(item, values=(new_name, new_location, new_rating))
        edit_hotel_window.destroy()

    def on_delete():
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM hotels WHERE name=? AND location=? AND rating=?', (values[0], values[1], values[2]))
        conn.commit()
        conn.close()

        tree_hotels.delete(item)
        edit_hotel_window.destroy()

    btn_save = tk.Button(edit_hotel_window, text="Сохранить", font=("Helvetica", 14), bg="black", fg="white", command=on_save)
    btn_save.pack(pady=10, side=tk.LEFT, padx=10)

    btn_delete = tk.Button(edit_hotel_window, text="Удалить", font=("Helvetica", 14), bg="white", fg="black", command=on_delete)
    btn_delete.pack(pady=10, side=tk.LEFT, padx=10)


# Функции для работы с путевками
def add_tour_to_db(country, dates, climate, hotel):
    if not (country and dates and climate and hotel):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tours (country, dates, climate, hotel) VALUES (?, ?, ?, ?)', (country, dates, climate, hotel))
    conn.commit()
    conn.close()

    tree_tours.insert('', 'end', values=(country, dates, climate, hotel))


def open_add_tour_window():
    add_tour_window = tk.Toplevel(root)
    add_tour_window.title("Добавить путевку")
    add_tour_window.geometry("300x300")
    add_tour_window.configure(bg="white")

    label_title = tk.Label(add_tour_window, text="Путевка", font=("Helvetica", 18, "bold"), bg="white")
    label_title.pack(pady=20)

    entry_country = PlaceholderEntry(add_tour_window, placeholder="Страна", font=("Helvetica", 12), width=30)
    entry_country.pack(pady=5, ipady=5)

    entry_dates = PlaceholderEntry(add_tour_window, placeholder="Даты отдыха", font=("Helvetica", 12), width=30)
    entry_dates.pack(pady=5, ipady=5)

    entry_climate = PlaceholderEntry(add_tour_window, placeholder="Климат", font=("Helvetica", 12), width=30)
    entry_climate.pack(pady=5, ipady=5)

    entry_hotel = PlaceholderEntry(add_tour_window, placeholder="Отель", font=("Helvetica", 12), width=30)
    entry_hotel.pack(pady=5, ipady=5)

    def on_add():
        add_tour_to_db(entry_country.get(), entry_dates.get(), entry_climate.get(), entry_hotel.get())
        add_tour_window.destroy()

    btn_add = tk.Button(add_tour_window, text="Добавить", font=("Helvetica", 14), bg="black", fg="white", command=on_add)
    btn_add.pack(pady=20)


def open_edit_tour_window(item):
    selected_item = tree_tours.item(item)
    values = selected_item['values']

    edit_tour_window = tk.Toplevel(root)
    edit_tour_window.title("Редактировать путевку")
    edit_tour_window.geometry("300x400")
    edit_tour_window.configure(bg="white")

    label_title = tk.Label(edit_tour_window, text="Путевка", font=("Helvetica", 18, "bold"), bg="white")
    label_title.pack(pady=20)

    entry_country = tk.Entry(edit_tour_window, font=("Helvetica", 12), width=30)
    entry_country.pack(pady=5, ipady=5)
    entry_country.insert(0, values[0])

    entry_dates = tk.Entry(edit_tour_window, font=("Helvetica", 12), width=30)
    entry_dates.pack(pady=5, ipady=5)
    entry_dates.insert(0, values[1])

    entry_climate = tk.Entry(edit_tour_window, font=("Helvetica", 12), width=30)
    entry_climate.pack(pady=5, ipady=5)
    entry_climate.insert(0, values[2])

    entry_hotel = tk.Entry(edit_tour_window, font=("Helvetica", 12), width=30)
    entry_hotel.pack(pady=5, ipady=5)
    entry_hotel.insert(0, values[3])

    def on_save():
        new_country = entry_country.get()
        new_dates = entry_dates.get()
        new_climate = entry_climate.get()
        new_hotel = entry_hotel.get()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE tours SET country=?, dates=?, climate=?, hotel=? WHERE country=? AND dates=? AND climate=? AND hotel=?',
                       (new_country, new_dates, new_climate, new_hotel, values[0], values[1], values[2], values[3]))
        conn.commit()
        conn.close()

        tree_tours.item(item, values=(new_country, new_dates, new_climate, new_hotel))
        edit_tour_window.destroy()

    def on_delete():
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tours WHERE country=? AND dates=? AND climate=? AND hotel=?', (values[0], values[1], values[2], values[3]))
        conn.commit()
        conn.close()

        tree_tours.delete(item)
        edit_tour_window.destroy()

    btn_save = tk.Button(edit_tour_window, text="Сохранить", font=("Helvetica", 14), bg="black", fg="white", command=on_save)
    btn_save.pack(pady=10, side=tk.LEFT, padx=10)

    btn_delete = tk.Button(edit_tour_window, text="Удалить", font=("Helvetica", 14), bg="white", fg="black", command=on_delete)
    btn_delete.pack(pady=10, side=tk.LEFT, padx=10)


def add_tour_operator_to_db(name, email, phone):
    if not (name and email and phone):
        messagebox.showerror("Ошибка", "Все поля должны быть заполнены!")
        return

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO tour_operators (name, email, phone) VALUES (?, ?, ?)', (name, email, phone))
    conn.commit()
    conn.close()

    # Обновить отображение списка тур операторов
    tree.insert('', 'end', values=(name, email, phone))


def open_add_operator_window():
    add_operator_window = tk.Toplevel(root)
    add_operator_window.title("Добавить тур оператора")
    add_operator_window.geometry("300x300")
    add_operator_window.configure(bg="white")

    label_title = tk.Label(add_operator_window, text="Тур оператор", font=("Helvetica", 18, "bold"), bg="white")
    label_title.pack(pady=20)

    entry_name = PlaceholderEntry(add_operator_window, placeholder="ФИО", font=("Helvetica", 12), width=30)
    entry_name.pack(pady=5, ipady=5)

    entry_email = PlaceholderEntry(add_operator_window, placeholder="Почта", font=("Helvetica", 12), width=30)
    entry_email.pack(pady=5, ipady=5)

    entry_phone = PlaceholderEntry(add_operator_window, placeholder="Телефон", font=("Helvetica", 12), width=30)
    entry_phone.pack(pady=5, ipady=5)

    def on_add():
        add_tour_operator_to_db(entry_name.get(), entry_email.get(), entry_phone.get())
        add_operator_window.destroy()

    btn_add = tk.Button(add_operator_window, text="Добавить", font=("Helvetica", 14), bg="black", fg="white", command=on_add)
    btn_add.pack(pady=20)


def open_edit_operator_window(item):
    selected_item = tree.item(item)
    values = selected_item['values']

    edit_operator_window = tk.Toplevel(root)
    edit_operator_window.title("Редактировать тур оператора")
    edit_operator_window.geometry("300x400")
    edit_operator_window.configure(bg="white")

    label_title = tk.Label(edit_operator_window, text="Тур оператор", font=("Helvetica", 18, "bold"), bg="white")
    label_title.pack(pady=20)

    entry_name = tk.Entry(edit_operator_window, font=("Helvetica", 12), width=30)
    entry_name.pack(pady=5, ipady=5)
    entry_name.insert(0, values[0])

    entry_email = tk.Entry(edit_operator_window, font=("Helvetica", 12), width=30)
    entry_email.pack(pady=5, ipady=5)
    entry_email.insert(0, values[1])

    entry_phone = tk.Entry(edit_operator_window, font=("Helvetica", 12), width=30)
    entry_phone.pack(pady=5, ipady=5)
    entry_phone.insert(0, values[2])

    def on_save():
        new_name = entry_name.get()
        new_email = entry_email.get()
        new_phone = entry_phone.get()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE tour_operators SET name=?, email=?, phone=? WHERE name=? AND email=? AND phone=?',
                       (new_name, new_email, new_phone, values[0], values[1], values[2]))
        conn.commit()
        conn.close()

        tree.item(item, values=(new_name, new_email, new_phone))
        edit_operator_window.destroy()

    def on_delete():
        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tour_operators WHERE name=? AND email=? AND phone=?', (values[0], values[1], values[2]))
        conn.commit()
        conn.close()

        tree.delete(item)
        edit_operator_window.destroy()

    btn_save = tk.Button(edit_operator_window, text="Сохранить", font=("Helvetica", 14), bg="black", fg="white", command=on_save)
    btn_save.pack(pady=10, side=tk.LEFT, padx=10)

    btn_delete = tk.Button(edit_operator_window, text="Удалить", font=("Helvetica", 14), bg="white", fg="black", command=on_delete)
    btn_delete.pack(pady=10, side=tk.LEFT, padx=10)


def open_main_window(role):
    print("Opening main window...")  # Отладочное сообщение
    main_window = tk.Toplevel(root)
    main_window.title("Main Window")
    main_window.geometry("800x600")
    main_window.configure(bg="white")

    notebook = ttk.Notebook(main_window)
    notebook.pack(expand=True, fill='both')

    if role == 'Администратор':
        create_admin_tabs(notebook)
    elif role == 'Тур оператор':
        create_operator_tabs(notebook)
    elif role == 'Клиент':
        create_client_tabs(notebook)

    # Кнопка "Выйти" в правом нижнем углу
    bottom_frame = tk.Frame(main_window, bg="white")
    bottom_frame.pack(side=tk.BOTTOM, fill=tk.X)

    btn_logout = tk.Button(bottom_frame, text="Выйти", bg="black", fg="white", font=("Helvetica", 12),
                           command=main_window.destroy)
    btn_logout.pack(side=tk.RIGHT, padx=10, pady=10)


def create_admin_tabs(notebook):
    # Создание вкладок
    tour_operators_tab = tk.Frame(notebook, bg="white")
    hotels_tab = tk.Frame(notebook, bg="white")
    tours_tab = tk.Frame(notebook, bg="white")

    notebook.add(tour_operators_tab, text='Тур операторы')
    notebook.add(hotels_tab, text='Отели')
    notebook.add(tours_tab, text='Путевки')

    # Вкладка Тур операторы
    form_frame = tk.Frame(tour_operators_tab, bg="white")
    form_frame.pack(pady=20)

    global tree
    btn_add_operator = tk.Button(form_frame, text="Добавить", font=("Helvetica", 12), bg="black", fg="white",
                                 command=open_add_operator_window)
    btn_add_operator.pack(side=tk.LEFT, padx=10, pady=10)

    tree = ttk.Treeview(tour_operators_tab, columns=("name", "email", "phone"), show="headings")
    tree.heading("name", text="ФИО")
    tree.heading("email", text="Почта")
    tree.heading("phone", text="Телефон")
    tree.pack(pady=20, fill=tk.BOTH, expand=True)

    tree.bind("<Double-1>", lambda event: open_edit_operator_window(tree.selection()[0]))

    # Загрузка существующих тур операторов
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, email, phone FROM tour_operators')
    for row in cursor.fetchall():
        tree.insert('', 'end', values=row)
    conn.close()

    # Вкладка Отели
    form_frame_hotels = tk.Frame(hotels_tab, bg="white")
    form_frame_hotels.pack(pady=20)

    global tree_hotels
    btn_add_hotel = tk.Button(form_frame_hotels, text="Добавить", font=("Helvetica", 12), bg="black", fg="white",
                              command=open_add_hotel_window)
    btn_add_hotel.pack(side=tk.LEFT, padx=10, pady=10)

    tree_hotels = ttk.Treeview(hotels_tab, columns=("name", "location", "rating"), show="headings")
    tree_hotels.heading("name", text="Название")
    tree_hotels.heading("location", text="Расположение")
    tree_hotels.heading("rating", text="Рейтинг")
    tree_hotels.pack(pady=20, fill=tk.BOTH, expand=True)

    tree_hotels.bind("<Double-1>", lambda event: open_edit_hotel_window(tree_hotels.selection()[0]))

    # Загрузка существующих отелей
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT name, location, rating FROM hotels')
    for row in cursor.fetchall():
        tree_hotels.insert('', 'end', values=row)
    conn.close()

    # Вкладка Путевки
    form_frame_tours = tk.Frame(tours_tab, bg="white")
    form_frame_tours.pack(pady=20)

    global tree_tours
    btn_add_tour = tk.Button(form_frame_tours, text="Добавить", font=("Helvetica", 12), bg="black", fg="white",
                             command=open_add_tour_window)
    btn_add_tour.pack(side=tk.LEFT, padx=10, pady=10)

    tree_tours = ttk.Treeview(tours_tab, columns=("country", "dates", "climate", "hotel"), show="headings")
    tree_tours.heading("country", text="Страна")
    tree_tours.heading("dates", text="Даты отдыха")
    tree_tours.heading("climate", text="Климат")
    tree_tours.heading("hotel", text="Отель")
    tree_tours.pack(pady=20, fill=tk.BOTH, expand=True)

    tree_tours.bind("<Double-1>", lambda event: open_edit_tour_window(tree_tours.selection()[0]))

    # Загрузка существующих путевок
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT country, dates, climate, hotel FROM tours')
    for row in cursor.fetchall():
        tree_tours.insert('', 'end', values=row)
    conn.close()


def create_operator_tabs(notebook):
    # Создание вкладок
    tours_tab = tk.Frame(notebook, bg="white")
    clients_tab = tk.Frame(notebook, bg="white")
    profile_tab = tk.Frame(notebook, bg="white")

    notebook.add(tours_tab, text='Путевки')
    notebook.add(clients_tab, text='Клиенты')
    notebook.add(profile_tab, text='Профиль')

    # Вкладка Путевки
    form_frame_tours = tk.Frame(tours_tab, bg="white")
    form_frame_tours.pack(pady=20)

    global tree_tours
    btn_add_tour = tk.Button(form_frame_tours, text="Добавить", font=("Helvetica", 12), bg="black", fg="white",
                             command=open_add_tour_window)
    btn_add_tour.pack(side=tk.LEFT, padx=10, pady=10)

    tree_tours = ttk.Treeview(tours_tab, columns=("country", "dates", "climate", "hotel"), show="headings")
    tree_tours.heading("country", text="Страна")
    tree_tours.heading("dates", text="Даты отдыха")
    tree_tours.heading("climate", text="Климат")
    tree_tours.heading("hotel", text="Отель")
    tree_tours.pack(pady=20, fill=tk.BOTH, expand=True)

    tree_tours.bind("<Double-1>", lambda event: open_edit_tour_window(tree_tours.selection()[0]))

    # Загрузка существующих путевок
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT country, dates, climate, hotel FROM tours')
    for row in cursor.fetchall():
        tree_tours.insert('', 'end', values=row)
    conn.close()

    # Вкладка Клиенты
    form_frame_clients = tk.Frame(clients_tab, bg="white")
    form_frame_clients.pack(pady=20)

    global tree_clients
    btn_add_client = tk.Button(form_frame_clients, text="Добавить", font=("Helvetica", 12), bg="black", fg="white",
                               command=open_add_client_window)
    btn_add_client.pack(side=tk.LEFT, padx=10, pady=10)

    tree_clients = ttk.Treeview(clients_tab, columns=("fullname", "email", "phone", "discount", "is_regular"), show="headings")
    tree_clients.heading("fullname", text="ФИО")
    tree_clients.heading("email", text="Почта")
    tree_clients.heading("phone", text="Телефон")
    tree_clients.heading("discount", text="% скидки")
    tree_clients.heading("is_regular", text="Постоянный клиент")
    tree_clients.pack(pady=20, fill=tk.BOTH, expand=True)

    tree_clients.bind("<Double-1>", lambda event: open_edit_client_window(tree_clients.selection()[0]))

    # Загрузка существующих клиентов
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT fullname, email, phone, discount, is_regular FROM clients')
    for row in cursor.fetchall():
        tree_clients.insert('', 'end', values=row)
    conn.close()

    # Вкладка Профиль
    form_frame_profile = tk.Frame(profile_tab, bg="white")
    form_frame_profile.pack(pady=20)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (current_user,))
    user_data = cursor.fetchone()
    conn.close()

    entry_username = PlaceholderEntry(form_frame_profile, placeholder="Логин", font=("Helvetica", 12), width=30)
    entry_username.pack(pady=5, ipady=5)
    entry_username.insert(0, user_data[1])

    entry_password = PlaceholderEntry(form_frame_profile, placeholder="Пароль", font=("Helvetica", 12), show="*", width=30)
    entry_password.pack(pady=5, ipady=5)
    entry_password.insert(0, user_data[2])

    entry_fullname = PlaceholderEntry(form_frame_profile, placeholder="ФИО", font=("Helvetica", 12), width=30)
    entry_fullname.pack(pady=5, ipady=5)
    entry_fullname.insert(0, user_data[3])

    entry_email = PlaceholderEntry(form_frame_profile, placeholder="Почта", font=("Helvetica", 12), width=30)
    entry_email.pack(pady=5, ipady=5)
    entry_email.insert(0, user_data[4])

    entry_phone = PlaceholderEntry(form_frame_profile, placeholder="Телефон", font=("Helvetica", 12), width=30)
    entry_phone.pack(pady=5, ipady=5)
    entry_phone.insert(0, user_data[5])

    def save_profile():
        new_username = entry_username.get()
        new_password = entry_password.get()
        new_fullname = entry_fullname.get()
        new_email = entry_email.get()
        new_phone = entry_phone.get()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET username=?, password=?, fullname=?, email=?, phone=? WHERE username=?',
                       (new_username, new_password, new_fullname, new_email, new_phone, current_user))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Профиль обновлен!")

    btn_save_profile = tk.Button(form_frame_profile, text="Сохранить", font=("Helvetica", 14), bg="black", fg="white", command=save_profile)
    btn_save_profile.pack(pady=20)


def create_client_tabs(notebook):
    # Создание вкладок
    current_tours_tab = tk.Frame(notebook, bg="white")
    profile_tab = tk.Frame(notebook, bg="white")

    notebook.add(current_tours_tab, text='Текущие путевки')
    notebook.add(profile_tab, text='Профиль')

    # Вкладка Текущие путевки
    form_frame_current_tours = tk.Frame(current_tours_tab, bg="white")
    form_frame_current_tours.pack(pady=20)

    global tree_current_tours
    tree_current_tours = ttk.Treeview(current_tours_tab, columns=("country", "dates", "climate", "hotel"), show="headings")
    tree_current_tours.heading("country", text="Страна")
    tree_current_tours.heading("dates", text="Даты отдыха")
    tree_current_tours.heading("climate", text="Климат")
    tree_current_tours.heading("hotel", text="Отель")
    tree_current_tours.pack(pady=20, fill=tk.BOTH, expand=True)

    # Загрузка существующих путевок
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT country, dates, climate, hotel FROM tours')
    for row in cursor.fetchall():
        tree_current_tours.insert('', 'end', values=row)
    conn.close()

    # Вкладка Профиль
    form_frame_profile = tk.Frame(profile_tab, bg="white")
    form_frame_profile.pack(pady=20)

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=?', (current_user,))
    user_data = cursor.fetchone()
    conn.close()

    entry_username = PlaceholderEntry(form_frame_profile, placeholder="Логин", font=("Helvetica", 12), width=30)
    entry_username.pack(pady=5, ipady=5)
    entry_username.insert(0, user_data[1])

    entry_password = PlaceholderEntry(form_frame_profile, placeholder="Пароль", font=("Helvetica", 12), show="*", width=30)
    entry_password.pack(pady=5, ipady=5)
    entry_password.insert(0, user_data[2])

    entry_fullname = PlaceholderEntry(form_frame_profile, placeholder="ФИО", font=("Helvetica", 12), width=30)
    entry_fullname.pack(pady=5, ipady=5)
    entry_fullname.insert(0, user_data[3])

    entry_email = PlaceholderEntry(form_frame_profile, placeholder="Почта", font=("Helvetica", 12), width=30)
    entry_email.pack(pady=5, ipady=5)
    entry_email.insert(0, user_data[4])

    entry_phone = PlaceholderEntry(form_frame_profile, placeholder="Телефон", font=("Helvetica", 12), width=30)
    entry_phone.pack(pady=5, ipady=5)
    entry_phone.insert(0, user_data[5])

    def save_profile():
        new_username = entry_username.get()
        new_password = entry_password.get()
        new_fullname = entry_fullname.get()
        new_email = entry_email.get()
        new_phone = entry_phone.get()

        conn = sqlite3.connect('users.db')
        cursor = conn.cursor()
        cursor.execute('UPDATE users SET username=?, password=?, fullname=?, email=?, phone=? WHERE username=?',
                       (new_username, new_password, new_fullname, new_email, new_phone, current_user))
        conn.commit()
        conn.close()

        messagebox.showinfo("Успех", "Профиль обновлен!")

    btn_save_profile = tk.Button(form_frame_profile, text="Сохранить", font=("Helvetica", 14), bg="black", fg="white", command=save_profile)
    btn_save_profile.pack(pady=20)


def login():
    global current_user
    username = entry_username.get()
    password = entry_password.get()

    # Подключение к базе данных и проверка логина и пароля
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (username, password))
    result = cursor.fetchone()
    conn.close()

    if result:
        current_user = username
        print("Login successful")  # Отладочное сообщение
        open_main_window(result[3])
        root.withdraw()  # Скрыть окно входа
    else:
        messagebox.showerror("Ошибка входа", "Неправильный логин или пароль")


# Создание главного окна
root = tk.Tk()
root.title("Login")
root.geometry("350x400")
root.configure(bg="white")

# Фрейм для центрирования содержимого
frame = tk.Frame(root, bg="white")
frame.pack(expand=True)

# Метка заголовка
label_title = tk.Label(frame, text="Вход", font=("Helvetica", 24, "bold"), bg="white")
label_title.pack(pady=20)

# Поле для ввода логина с текстом-заполнителем
entry_username = PlaceholderEntry(frame, placeholder="Введите логин", font=("Helvetica", 12), width=30)
entry_username.pack(pady=10, ipady=5)

# Поле для ввода пароля с текстом-заполнителем
entry_password = PlaceholderEntry(frame, placeholder="Введите пароль", font=("Helvetica", 12), show="*", width=30)
entry_password.pack(pady=10, ipady=5)

# Кнопка "Войти"
button_login = tk.Button(frame, text="Войти", font=("Helvetica", 14), bg="black", fg="white", bd=0, padx=10, pady=5,
                         command=login)
button_login.pack(pady=20)

# Запуск главного цикла приложения
root.mainloop()
