import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# === DATABASE SETUP ===
def get_connection():
    return sqlite3.connect("pos.db")

def create_category_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL UNIQUE
        )
    ''')
    conn.commit()
    conn.close()

# === WINDOW CATEGORY CRUD ===
class CategoryCRUD(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manajemen Kategori Produk")
        self.geometry("600x450")

        self.editing_category_id = None
        create_category_table()
        self.setup_ui()
        self.refresh_tree()

    def setup_ui(self):
        title = ttk.Label(self, text="Data Kategori Produk", font=("Arial", 18, "bold"))
        title.pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Nama Kategori").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        self.save_btn = ttk.Button(btn_frame, text="Tambah", command=self.add_category)
        self.save_btn.grid(row=0, column=0, padx=10)

        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.save_edit)
        self.edit_btn.grid(row=0, column=1, padx=10)

        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_edit)
        self.cancel_btn.grid(row=0, column=2, padx=10)

        ttk.Button(btn_frame, text="Hapus", command=self.delete_category).grid(row=0, column=3, padx=10)

        tree_frame = ttk.Frame(self)
        tree_frame.pack(pady=10, fill="both", expand=True, padx=20)

        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Nama'), show='headings')
        for col in ('ID', 'Nama'):
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

        self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.editing_category_id = None

    def cancel_edit(self):
        self.clear_form()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        cat_data = self.tree.item(selected[0])['values']
        self.editing_category_id = cat_data[0]
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, cat_data[1])

    def add_category(self):
        name = self.name_entry.get()

        if not name:
            messagebox.showerror("Error", "Nama kategori harus diisi!", parent=self)
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            conn.commit()
            self.refresh_tree()
            messagebox.showinfo("Sukses", "Kategori berhasil ditambahkan!", parent=self)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Nama kategori sudah ada!", parent=self)
        finally:
            conn.close()

    def save_edit(self):
        if not self.editing_category_id:
            return

        name = self.name_entry.get()

        if not name:
            messagebox.showerror("Error", "Nama kategori tidak boleh kosong!", parent=self)
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("UPDATE categories SET name=? WHERE id=?",
                           (name, self.editing_category_id))
            conn.commit()
            self.refresh_tree()
            messagebox.showinfo("Sukses", "Kategori berhasil diperbarui.", parent=self)
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Nama kategori sudah digunakan!", parent=self)
        finally:
            conn.close()

    def delete_category(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Pilih kategori yang ingin dihapus.", parent=self)
            return

        cat_id = self.tree.item(selected[0])['values'][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM categories WHERE id = ?", (cat_id,))
        conn.commit()
        conn.close()
        self.refresh_tree()
        messagebox.showinfo("Sukses", "Kategori berhasil dihapus.", parent=self)