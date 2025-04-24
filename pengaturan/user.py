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

        self.editing_user_id = None
        create_user_table()
        self.setup_ui()
        self.refresh_tree()

    def setup_ui(self):
        title = ttk.Label(self, text="Data Pengguna Kasir", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        # Form Tambah User
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

        self.save_btn = ttk.Button(btn_frame, text="Tambah", command=self.add_user)
        self.save_btn.grid(row=0, column=0, padx=10)

        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.save_edit)
        self.edit_btn.grid(row=0, column=1, padx=10)

        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_edit)
        self.cancel_btn.grid(row=0, column=2, padx=10)

        ttk.Button(btn_frame, text="Hapus", command=self.delete_user).grid(row=0, column=3, padx=10)

        # Treeview
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

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, username, role FROM user")
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

        self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.role_combo.set("admin")
        self.editing_user_id = None

    def cancel_edit(self):
        self.clear_form()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        user_data = self.tree.item(selected[0])['values']
        self.editing_user_id = user_data[0]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, user_data[1])

        self.username_entry.delete(0, tk.END)
        self.username_entry.insert(0, user_data[2])

        self.password_entry.delete(0, tk.END)
        self.role_combo.set(user_data[3])

    def add_user(self):
        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not all([name, username, password, role]):
            messagebox.showerror("Error", "Semua field harus diisi!", parent=self)
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO user (name, username, password, role) VALUES (?, ?, ?, ?)",
                           (name, username, hash_password(password), role))
            conn.commit()
            self.refresh_tree()
            messagebox.showinfo("Sukses", "User berhasil ditambahkan!", parent=self)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username sudah digunakan!", parent=self)
        finally:
            conn.close()

    def save_edit(self):
        if not self.editing_user_id:
            return

        name = self.name_entry.get()
        username = self.username_entry.get()
        password = self.password_entry.get()
        role = self.role_var.get()

        if not all([name, username, role]):
            messagebox.showerror("Error", "Field tidak boleh kosong!", parent=self)
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            if password:
                cursor.execute("""
                    UPDATE user SET name=?, username=?, password=?, role=? WHERE id=?
                """, (name, username, hash_password(password), role, self.editing_user_id))
            else:
                cursor.execute("""
                    UPDATE user SET name=?, username=?, role=? WHERE id=?
                """, (name, username, role, self.editing_user_id))
            conn.commit()
            messagebox.showinfo("Sukses", "Data user berhasil diperbarui.", parent=self)
            self.refresh_tree()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username sudah digunakan!", parent=self)
        finally:
            conn.close()

    def delete_user(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Pilih user yang ingin dihapus.", parent=self)
            return

        user_id = self.tree.item(selected[0])['values'][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM user WHERE id = ?", (user_id,))
        conn.commit()
        conn.close()
        self.refresh_tree()
        messagebox.showinfo("Sukses", "User berhasil dihapus.", parent=self)