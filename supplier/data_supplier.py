import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# === DATABASE SETUP ===
def get_connection():
    return sqlite3.connect("pos.db")

def create_supplier_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS supplier (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT,
            address TEXT
        )
    ''')
    conn.commit()
    conn.close()

# === WINDOW SUPPLIER CRUD ===
class SupplierCRUD(tk.Toplevel): 
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manajemen Supplier")
        self.geometry("700x500")

        self.editing_supplier_id = None
        create_supplier_table()
        self.setup_ui()
        self.refresh_tree()

    def setup_ui(self):
        title = ttk.Label(self, text="Data Supplier", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        # Form Tambah Supplier
        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Nama").grid(row=0, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Telepon").grid(row=1, column=0, padx=5, pady=5)
        self.phone_entry = tk.Entry(form_frame)
        self.phone_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Alamat").grid(row=2, column=0, padx=5, pady=5)
        self.address_text = tk.Text(form_frame, height=3, width=20, font=('arial',9))
        self.address_text.grid(row=2, column=1, padx=5, pady=5)

        # Tombol
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        self.save_btn = ttk.Button(btn_frame, text="Tambah", command=self.add_supplier)
        self.save_btn.grid(row=0, column=0, padx=10)

        self.edit_btn = ttk.Button(btn_frame, text="Edit", command=self.save_edit)
        self.edit_btn.grid(row=0, column=1, padx=10)

        self.cancel_btn = ttk.Button(btn_frame, text="Cancel", command=self.cancel_edit)
        self.cancel_btn.grid(row=0, column=2, padx=10)

        ttk.Button(btn_frame, text="Hapus", command=self.delete_supplier).grid(row=0, column=3, padx=10)

        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(pady=10, fill="both", expand=True, padx=20)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(tree_frame, columns=('ID', 'Name', 'Phone', 'Address'), show='headings', yscrollcommand=tree_scroll.set)
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
        cursor.execute("SELECT id, name, phone, address FROM supplier")
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()

        self.clear_form()

    def clear_form(self):
        self.name_entry.delete(0, tk.END)
        self.phone_entry.delete(0, tk.END)
        self.address_text.delete("1.0", tk.END)
        self.editing_supplier_id = None

    def cancel_edit(self):
        self.clear_form()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        supplier_data = self.tree.item(selected[0])['values']
        self.editing_supplier_id = supplier_data[0]

        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, supplier_data[1])

        self.phone_entry.delete(0, tk.END)
        self.phone_entry.insert(0, supplier_data[2])

        self.address_text.delete("1.0", tk.END)
        self.address_text.insert("1.0", supplier_data[3])

    def add_supplier(self):
        name = self.name_entry.get()
        phone = self.phone_entry.get()
        address = self.address_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Error", "Nama supplier harus diisi!", parent=self)
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO supplier (name, phone, address) VALUES (?, ?, ?)",
                       (name, phone, address))
        conn.commit()
        conn.close()
        self.refresh_tree()
        messagebox.showinfo("Sukses", "Supplier berhasil ditambahkan!", parent=self)

    def save_edit(self):
        if not self.editing_supplier_id:
            return

        name = self.name_entry.get()
        phone = self.phone_entry.get()
        address = self.address_text.get("1.0", tk.END).strip()

        if not name:
            messagebox.showerror("Error", "Nama tidak boleh kosong!", parent=self)
            return

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("""UPDATE supplier SET name=?, phone=?, address=? WHERE id=?""",
                       (name, phone, address, self.editing_supplier_id))
        conn.commit()
        conn.close()
        messagebox.showinfo("Sukses", "Data supplier berhasil diperbarui.", parent=self)
        self.refresh_tree()

    def delete_supplier(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Pilih supplier yang ingin dihapus.", parent=self)
            return

        supplier_id = self.tree.item(selected[0])['values'][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM supplier WHERE id = ?", (supplier_id,))
        conn.commit()
        conn.close()
        self.refresh_tree()
        messagebox.showinfo("Sukses", "Supplier berhasil dihapus.", parent=self)