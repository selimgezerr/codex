import sqlite3
import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import webbrowser
from datetime import date, datetime
import csv

DB_FILE = 'app.db'

# Database helpers

def init_db():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            """CREATE TABLE IF NOT EXISTS customers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT,
                    phone TEXT,
                    email TEXT,
                    hosting_expiry DATE,
                    domain_expiry DATE
                )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS projects (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_id INTEGER,
                    name TEXT,
                    details TEXT,
                    FOREIGN KEY(customer_id) REFERENCES customers(id)
                )"""
        )
        c.execute(
            """CREATE TABLE IF NOT EXISTS todos (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    description TEXT,
                    due_date DATE,
                    completed INTEGER DEFAULT 0
                )"""
        )

# Customer functions

def add_customer(data):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO customers (name, phone, email, hosting_expiry, domain_expiry) VALUES (?,?,?,?,?)",
            data,
        )
        conn.commit()

def get_customers():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, name, phone, email, hosting_expiry, domain_expiry FROM customers"
        )
        rows = c.fetchall()
    return rows

def delete_customer(cid):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM customers WHERE id=?", (cid,))
        conn.commit()

def update_customer(data):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "UPDATE customers SET name=?, phone=?, email=?, hosting_expiry=?, domain_expiry=? WHERE id=?",
            data,
        )
        conn.commit()

# Project functions

def add_project(data):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "INSERT INTO projects (customer_id, name, details) VALUES (?,?,?)",
            data,
        )
        conn.commit()

def get_projects():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, customer_id, name, details FROM projects")
        rows = c.fetchall()
    return rows

def get_project(pid):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(
            "SELECT id, customer_id, name, details FROM projects WHERE id=?",
            (pid,),
        )
        return c.fetchone()

def delete_project(pid):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM projects WHERE id=?", (pid,))
        conn.commit()

def update_project(data):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "UPDATE projects SET customer_id=?, name=?, details=? WHERE id=?",
            data,
        )
        conn.commit()

# Todo functions

def add_todo(data):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("INSERT INTO todos (description, due_date) VALUES (?,?)", data)
        conn.commit()

def get_todos():
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute("SELECT id, description, due_date, completed FROM todos")
        rows = c.fetchall()
    return rows

def delete_todo(tid):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM todos WHERE id=?", (tid,))
        conn.commit()

def complete_todo(tid):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE todos SET completed=1 WHERE id=?", (tid,))
        conn.commit()

def set_todo_completion(tid, status):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("UPDATE todos SET completed=? WHERE id=?", (1 if status else 0, tid))
        conn.commit()

def clear_completed():
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute("DELETE FROM todos WHERE completed=1")
        conn.commit()

def days_left(date_str):
    if not date_str:
        return ""
    try:
        target = datetime.strptime(date_str, "%Y-%m-%d").date()
        return (target - date.today()).days
    except ValueError:
        return ""

def ask_date(title, initial=None):
    while True:
        value = simpledialog.askstring(title, "YYYY-AA-GG:", initialvalue=initial)
        if value is None or value == "":
            return value
        try:
            datetime.strptime(value, "%Y-%m-%d")
            return value
        except ValueError:
            messagebox.showerror("Tarih Hatası", "Lütfen tarihi YYYY-AA-GG biçiminde girin")

def update_todo(data):
    with sqlite3.connect(DB_FILE) as conn:
        conn.execute(
            "UPDATE todos SET description=?, due_date=? WHERE id=?",
            data,
        )
        conn.commit()

def export_table(table, filename):
    with sqlite3.connect(DB_FILE) as conn:
        c = conn.cursor()
        c.execute(f"SELECT * FROM {table}")
        headers = [d[0] for d in c.description]
        rows = c.fetchall()
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(rows)

# UI helpers

def refresh_customers(listbox, search=""):
    listbox.delete(0, tk.END)
    for row in get_customers():
        if search and search.lower() not in row[1].lower():
            continue
        h = days_left(row[4])
        d = days_left(row[5])
        h_txt = f"H {h}g" if h != "" else "H ?"
        d_txt = f"D {d}g" if d != "" else "D ?"
        listbox.insert(
            tk.END,
            f"{row[0]} - {row[1]} ({row[2]}) [{h_txt}, {d_txt}]",
        )


def refresh_projects(listbox):
    listbox.delete(0, tk.END)
    for row in get_projects():
        listbox.insert(tk.END, f"{row[0]} - {row[2]} (Müşteri {row[1]})")


def refresh_todos(listbox, show_completed=True):
    listbox.delete(0, tk.END)
    for row in get_todos():
        if not show_completed and row[3]:
            continue
        status = "✓" if row[3] else "✗"
        left = days_left(row[2])
        left_txt = f"{left}g" if left != "" else "?"
        listbox.insert(tk.END, f"{row[0]} - {row[1]} ({left_txt}) [{status}]")


def whatsapp_send(phone):
    if not phone:
        messagebox.showinfo("WhatsApp", "Telefon numarası boş")
        return
    webbrowser.open(f"https://api.whatsapp.com/send?phone={phone}")

# Main app

def main():
    init_db()
    root = tk.Tk()
    root.title("Müşteri ve Proje Yöneticisi")
    root.geometry("600x400")

    tab_control = ttk.Notebook(root)

    # Customers tab
    cust_tab = ttk.Frame(tab_control)
    search_var = tk.StringVar()
    search_entry = ttk.Entry(cust_tab, textvariable=search_var)
    search_entry.pack(fill=tk.X)
    cust_list = tk.Listbox(cust_tab)
    cust_scroll = ttk.Scrollbar(cust_tab, command=cust_list.yview)
    cust_list.config(yscrollcommand=cust_scroll.set)
    cust_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
    cust_scroll.pack(side=tk.LEFT, fill=tk.Y)
    search_var.trace_add("write", lambda *_: refresh_customers(cust_list, search_var.get()))

    cust_buttons = ttk.Frame(cust_tab)
    cust_buttons.pack(side=tk.RIGHT, fill=tk.Y)

    def add_cust():
        name = simpledialog.askstring("İsim", "Müşteri adı:")
        phone = simpledialog.askstring("Telefon", "Telefon numarası:")
        email = simpledialog.askstring("E-posta", "E-posta:")
        hosting = ask_date("Hosting Bitiş")
        domain = ask_date("Domain Bitiş")
        if name:
            add_customer((name, phone, email, hosting, domain))
            refresh_customers(cust_list)

    def edit_cust():
        sel = cust_list.curselection()
        if sel:
            cid = int(cust_list.get(sel[0]).split(' - ')[0])
            for c in get_customers():
                if c[0] == cid:
                    name = simpledialog.askstring("İsim", "Müşteri adı:", initialvalue=c[1])
                    phone = simpledialog.askstring("Telefon", "Telefon numarası:", initialvalue=c[2])
                    email = simpledialog.askstring("E-posta", "E-posta:", initialvalue=c[3])
                    hosting = ask_date("Hosting Bitiş", c[4])
                    domain = ask_date("Domain Bitiş", c[5])
                    if name:
                        update_customer((name, phone, email, hosting, domain, cid))
                        refresh_customers(cust_list)
                    break

    def delete_cust():
        sel = cust_list.curselection()
        if sel:
            cid = int(cust_list.get(sel[0]).split(' - ')[0])
            if messagebox.askyesno("Sil", "Seçili müşteriyi silmek istiyor musunuz?"):
                delete_customer(cid)
                refresh_customers(cust_list)

    def whatsapp_cust():
        sel = cust_list.curselection()
        if sel:
            idx = int(cust_list.get(sel[0]).split(' - ')[0])
            customers = get_customers()
            for c in customers:
                if c[0] == idx:
                    whatsapp_send(c[2])
                    break

    def export_cust():
        export_table('customers', 'customers.csv')
        messagebox.showinfo('Dışa Aktar', 'Müşteri verileri customers.csv dosyasına kaydedildi')

    ttk.Button(cust_buttons, text="Ekle", command=add_cust).pack(fill=tk.X)
    ttk.Button(cust_buttons, text="Düzenle", command=edit_cust).pack(fill=tk.X)
    ttk.Button(cust_buttons, text="Sil", command=delete_cust).pack(fill=tk.X)
    ttk.Button(cust_buttons, text="WhatsApp", command=whatsapp_cust).pack(fill=tk.X)
    ttk.Button(cust_buttons, text="CSV", command=export_cust).pack(fill=tk.X)

    refresh_customers(cust_list)

    # Projects tab
    proj_tab = ttk.Frame(tab_control)
    proj_list = tk.Listbox(proj_tab)
    proj_scroll = ttk.Scrollbar(proj_tab, command=proj_list.yview)
    proj_list.config(yscrollcommand=proj_scroll.set)
    proj_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
    proj_scroll.pack(side=tk.LEFT, fill=tk.Y)

    proj_buttons = ttk.Frame(proj_tab)
    proj_buttons.pack(side=tk.RIGHT, fill=tk.Y)

    def add_proj():
        customers = get_customers()
        if not customers:
            messagebox.showinfo("Projeler", "Lütfen önce müşteri ekleyin")
            return
        cust_ids = [str(c[0]) for c in customers]
        cid = simpledialog.askstring("Müşteri ID", "Müşteri ID (" + ", ".join(cust_ids) + "):")
        name = simpledialog.askstring("İsim", "Proje adı:")
        details = simpledialog.askstring("Detay", "Proje detayları:")
        if cid and name:
            add_project((cid, name, details))
            refresh_projects(proj_list)

    def edit_proj():
        sel = proj_list.curselection()
        if sel:
            pid = int(proj_list.get(sel[0]).split(' - ')[0])
            for p in get_projects():
                if p[0] == pid:
                    customers = get_customers()
                    cust_ids = [str(c[0]) for c in customers]
                    cid = simpledialog.askstring(
                        "Müşteri ID",
                        "Müşteri ID (" + ", ".join(cust_ids) + "):",
                        initialvalue=p[1],
                    )
                    name = simpledialog.askstring("İsim", "Proje adı:", initialvalue=p[2])
                    details = simpledialog.askstring(
                        "Detay", "Proje detayları:", initialvalue=p[3]
                    )
                    if cid and name:
                        update_project((cid, name, details, pid))
                        refresh_projects(proj_list)
                    break

    def delete_proj():
        sel = proj_list.curselection()
        if sel:
            pid = int(proj_list.get(sel[0]).split(' - ')[0])
            if messagebox.askyesno("Sil", "Seçili projeyi silmek istiyor musunuz?"):
                delete_project(pid)
                refresh_projects(proj_list)

    def export_proj():
        export_table('projects', 'projects.csv')
        messagebox.showinfo('Dışa Aktar', 'Proje verileri projects.csv dosyasına kaydedildi')

    def show_proj_details(event=None):
        sel = proj_list.curselection()
        if sel:
            pid = int(proj_list.get(sel[0]).split(' - ')[0])
            proj = get_project(pid)
            if proj:
                messagebox.showinfo(
                    'Proje Detayı', f"Müşteri ID: {proj[1]}\nAd: {proj[2]}\nDetay:\n{proj[3]}"
                )

    ttk.Button(proj_buttons, text="Ekle", command=add_proj).pack(fill=tk.X)
    ttk.Button(proj_buttons, text="Düzenle", command=edit_proj).pack(fill=tk.X)
    ttk.Button(proj_buttons, text="Sil", command=delete_proj).pack(fill=tk.X)
    ttk.Button(proj_buttons, text="CSV", command=export_proj).pack(fill=tk.X)

    proj_list.bind("<Double-1>", show_proj_details)

    refresh_projects(proj_list)

    # Todo tab
    todo_tab = ttk.Frame(tab_control)
    todo_list = tk.Listbox(todo_tab)
    todo_scroll = ttk.Scrollbar(todo_tab, command=todo_list.yview)
    todo_list.config(yscrollcommand=todo_scroll.set)
    todo_list.pack(fill=tk.BOTH, expand=True, side=tk.LEFT)
    todo_scroll.pack(side=tk.LEFT, fill=tk.Y)

    todo_buttons = ttk.Frame(todo_tab)
    todo_buttons.pack(side=tk.RIGHT, fill=tk.Y)

    show_completed_var = tk.BooleanVar(value=True)
    show_completed = ttk.Checkbutton(
        todo_buttons,
        text="Tamamlananları Göster",
        variable=show_completed_var,
        command=lambda: refresh_todos(todo_list, show_completed_var.get()),
    )
    show_completed.pack(fill=tk.X)

    def add_task():
        desc = simpledialog.askstring("Görev", "Görev açıklaması:")
        due = ask_date("Son Tarih")
        if desc:
            add_todo((desc, due))
            refresh_todos(todo_list, show_completed_var.get())

    def edit_task():
        sel = todo_list.curselection()
        if sel:
            tid = int(todo_list.get(sel[0]).split(' - ')[0])
            for t in get_todos():
                if t[0] == tid:
                    desc = simpledialog.askstring("Görev", "Görev açıklaması:", initialvalue=t[1])
                    due = ask_date("Son Tarih", t[2])
                    if desc:
                        update_todo((desc, due, tid))
                        refresh_todos(todo_list, show_completed_var.get())
                    break

    def delete_task():
        sel = todo_list.curselection()
        if sel:
            tid = int(todo_list.get(sel[0]).split(' - ')[0])
            if messagebox.askyesno("Sil", "Seçili görevi silmek istiyor musunuz?"):
                delete_todo(tid)
                refresh_todos(todo_list, show_completed_var.get())

    def tamamla_task():
        sel = todo_list.curselection()
        if sel:
            tid = int(todo_list.get(sel[0]).split(' - ')[0])
            for t in get_todos():
                if t[0] == tid:
                    set_todo_completion(tid, not t[3])
                    break
            refresh_todos(todo_list, show_completed_var.get())

    def clear_done():
        if messagebox.askyesno("Temizle", "Tamamlanan görevleri silmek istiyor musunuz?"):
            clear_completed()
            refresh_todos(todo_list, show_completed_var.get())

    def export_tasks():
        export_table('todos', 'todos.csv')
        messagebox.showinfo('Dışa Aktar', 'Görev verileri todos.csv dosyasına kaydedildi')

    ttk.Button(todo_buttons, text="Ekle", command=add_task).pack(fill=tk.X)
    ttk.Button(todo_buttons, text="Düzenle", command=edit_task).pack(fill=tk.X)
    ttk.Button(todo_buttons, text="Sil", command=delete_task).pack(fill=tk.X)
    ttk.Button(todo_buttons, text="Tamamlandı", command=tamamla_task).pack(fill=tk.X)
    ttk.Button(todo_buttons, text="Tamamlananları Temizle", command=clear_done).pack(fill=tk.X)
    ttk.Button(todo_buttons, text="CSV", command=export_tasks).pack(fill=tk.X)

    refresh_todos(todo_list, show_completed_var.get())

    tab_control.add(cust_tab, text="Müşteriler")
    tab_control.add(proj_tab, text="Projeler")
    tab_control.add(todo_tab, text="Yapılacaklar")
    tab_control.pack(fill=tk.BOTH, expand=True)

    root.mainloop()

if __name__ == '__main__':
    main()
