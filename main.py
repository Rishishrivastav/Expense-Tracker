import tkinter as tk
from tkinter import messagebox, ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import sqlite3

# Initialize DB
conn = sqlite3.connect('expense_tracker.db')
c = conn.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT UNIQUE NOT NULL,
    password TEXT NOT NULL
)""")
c.execute("""CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL,
    category TEXT,
    date TEXT,
    type TEXT,
    description TEXT
)""")
conn.commit()

# Global user session
current_user = None

# Login window
def show_login():
    login_frame = tk.Tk()
    login_frame.title("Login")
    login_frame.geometry("300x250")

    tk.Label(login_frame, text="Email").pack()
    email_entry = tk.Entry(login_frame)
    email_entry.pack()

    tk.Label(login_frame, text="Password").pack()
    password_entry = tk.Entry(login_frame, show="*")
    password_entry.pack()

    def login():
        global current_user
        email = email_entry.get()
        password = password_entry.get()
        c.execute("SELECT id FROM users WHERE email=? AND password=?", (email, password))
        user = c.fetchone()
        if user:
            current_user = user[0]
            login_frame.destroy()
            show_dashboard()
        else:
            messagebox.showerror("Error", "Invalid credentials")

    def register():
        login_frame.destroy()
        show_register()

    tk.Button(login_frame, text="Login", command=login).pack(pady=5)
    tk.Button(login_frame, text="Register", command=register).pack()
    login_frame.mainloop()

# Register window
def show_register():
    register_frame = tk.Tk()
    register_frame.title("Register")
    register_frame.geometry("300x250")

    tk.Label(register_frame, text="Email").pack()
    email_entry = tk.Entry(register_frame)
    email_entry.pack()

    tk.Label(register_frame, text="Password").pack()
    password_entry = tk.Entry(register_frame, show="*")
    password_entry.pack()

    def register_user():
        email = email_entry.get()
        password = password_entry.get()
        try:
            c.execute("INSERT INTO users (email, password) VALUES (?, ?)", (email, password))
            conn.commit()
            messagebox.showinfo("Success", "Registered successfully")
            register_frame.destroy()
            show_login()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Email already exists")

    tk.Button(register_frame, text="Register", command=register_user).pack(pady=5)
    tk.Button(register_frame, text="Back to Login", command=lambda: [register_frame.destroy(), show_login()]).pack()
    register_frame.mainloop()

# Dashboard window
def show_dashboard():
    dashboard = tk.Tk()
    dashboard.title("Expense Tracker")
    dashboard.geometry("800x600")

    # Top: Add Transaction
    form_frame = tk.Frame(dashboard)
    form_frame.pack(pady=10)

    entries = {}
    for label in ["Amount", "Category", "Date (YYYY-MM-DD)", "Type (Income/Expense)", "Description"]:
        tk.Label(form_frame, text=label).grid(row=len(entries), column=0)
        entry = tk.Entry(form_frame)
        entry.grid(row=len(entries), column=1)
        entries[label] = entry

    def add_transaction():
        values = [entries["Amount"].get(), entries["Category"].get(), entries["Date (YYYY-MM-DD)"].get(),
                  entries["Type (Income/Expense)"].get(), entries["Description"].get()]
        if values[3] not in ["Income", "Expense"]:
            messagebox.showerror("Error", "Type must be 'Income' or 'Expense'")
            return
        c.execute("INSERT INTO transactions (user_id, amount, category, date, type, description) VALUES (?, ?, ?, ?, ?, ?)",
                  (current_user, float(values[0]), values[1], values[2], values[3], values[4]))
        conn.commit()
        update_table()
        update_chart()

    tk.Button(form_frame, text="Add", command=add_transaction).grid(row=5, column=0, columnspan=2, pady=10)

    # Middle: Table
    table = ttk.Treeview(dashboard, columns=("Amount", "Category", "Date", "Type", "Description"), show="headings")
    for col in table["columns"]:
        table.heading(col, text=col)
    table.pack(pady=10)

    def update_table():
        for row in table.get_children():
            table.delete(row)
        c.execute("SELECT amount, category, date, type, description, id FROM transactions WHERE user_id=?", (current_user,))
        for row in c.fetchall():
            table.insert("", "end", values=row[:-1], iid=row[-1])

    def delete_transaction():
        selected = table.selection()
        if selected:
            c.execute("DELETE FROM transactions WHERE id=?", (selected[0],))
            conn.commit()
            update_table()
            update_chart()

    tk.Button(dashboard, text="Delete Selected", command=delete_transaction).pack()

    # Bottom: Chart
    chart_frame = tk.Frame(dashboard)
    chart_frame.pack(pady=20)

    def update_chart():
        for widget in chart_frame.winfo_children():
            widget.destroy()
        c.execute("SELECT type, SUM(amount) FROM transactions WHERE user_id=? GROUP BY type", (current_user,))
        data = c.fetchall()
        if data:
            types, amounts = zip(*data)
            fig, ax = plt.subplots()
            ax.pie(amounts, labels=types, autopct="%1.1f%%")
            chart = FigureCanvasTkAgg(fig, master=chart_frame)
            chart.draw()
            chart.get_tk_widget().pack()

    update_table()
    update_chart()
    dashboard.mainloop()

# Start
show_login()
