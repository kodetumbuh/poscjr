import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib

# === DATABASE SETUP ===
def get_connection():
    return sqlite3.connect("pos.db")

def create_user_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT CHECK(role IN ('admin', 'kasir')) NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

# === WINDOW USER CRUD ===
class UserCRUD(tk.Toplevel): 
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manajemen Pengguna Kasir")
        self.geometry("700x500")

        create_user_table()
        self.setup_ui()
        self.refresh_tree()

    def setup_ui(self):
        # Judul
        title = ttk.Label(self, text="Data Pengguna Kasir", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        # Form
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Nama").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = ttk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Username").grid(row=1, column=0, padx=5, pady=5)
        self.username_entry = ttk.Entry(form_frame)
        self.username_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Password").grid(row=2, column=0, padx=5, pady=5)
        self.password_entry = ttk.Entry(form_frame, show="*")
        self.password_entry.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Role").grid(row=3, column=0, padx=5, pady=5)
        self.role_var = tk.StringVar()
        self.role_combo = ttk.Combobox(form_frame, textvariable=self.role_var, values=["admin", "kasir"], state="readonly")
        self.role_combo.grid(row=3, column=1, padx=5, pady=5)
        self.role_combo.set("admin")

        # Tombol
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Tambah", command=self.add_user).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Hapus", command=self.delete_user).grid(row=0, column=1, padx=10)

        # Treeview Frame + Scrollbar
        tree_frame = ttk.Frame(self)
        tree_frame.pack(pady=10, fill="both", expand=True, padx=20)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Username', 'Role'), show='headings', yscrollcommand=tree_scroll.set)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, role FROM user")
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

    def add_user(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not all([name, username, password, role]):
            messagebox.showerror("Error", "Semua field harus diisi!")
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO user (name, username, password, role) VALUES (?, ?, ?, ?)",
                           (name, username, hash_password(password), role))
            conn.commit()
            self.refresh_tree()
            messagebox.showinfo("Sukses", "User berhasil ditambahkan!")
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username sudah digunakan!")
        finally:
            conn.close()

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Pilih user yang ingin dihapus.")
            return

        user_id = self.tree.item(selected[0])['values'][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        self.refresh_tree()
        messagebox.showinfo("Sukses", "User berhasil dihapus.")
