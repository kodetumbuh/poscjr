import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

# === DATABASE SETUP ===
def get_connection():
    return sqlite3.connect("pos.db")

def create_product_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS product (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            barcode INTEGER UNIQUE,
            name TEXT NOT NULL,
            category_id INTEGER,
            supplier_id INTEGER,
            purchase_price REAL NOT NULL,
            selling_price REAL NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(id),
            FOREIGN KEY (supplier_id) REFERENCES supplier(id)
        )
    ''')
    conn.commit()
    conn.close()

class ProductCRUD(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manajemen Produk")
        self.geometry("850x600")
        self.minsize(850, 600)

        self.editing_product_id = None
        create_product_table()
        self.setup_ui()
        self.refresh_tree()

    def setup_ui(self):
        title = ttk.Label(self, text="Data Produk", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        form_frame = ttk.Frame(self)
        form_frame.pack(pady=10)

        ttk.Label(form_frame, text="Barcode").grid(row=0, column=0, padx=5, pady=5)
        self.barcode_entry = tk.Entry(form_frame)
        self.barcode_entry.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Nama").grid(row=1, column=0, padx=5, pady=5)
        self.name_entry = tk.Entry(form_frame)
        self.name_entry.grid(row=1, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Kategori").grid(row=2, column=0, padx=5, pady=5)
        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(form_frame, textvariable=self.category_var, state="readonly")
        self.category_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Supplier").grid(row=3, column=0, padx=5, pady=5)
        self.supplier_var = tk.StringVar()
        self.supplier_combo = ttk.Combobox(form_frame, textvariable=self.supplier_var, state="readonly")
        self.supplier_combo.grid(row=3, column=1, padx=5, pady=5)

        ttk.Label(form_frame, text="Harga Beli").grid(row=4, column=0, padx=5, pady=5)
        self.purchase_price_entry = tk.Entry(form_frame)
        self.purchase_price_entry.grid(row=4, column=1, padx=5, pady=5)
        self.purchase_price_entry.bind("<KeyRelease>", self.format_rupiah_live)

        ttk.Label(form_frame, text="Harga Jual").grid(row=5, column=0, padx=5, pady=5)
        self.selling_price_entry = tk.Entry(form_frame)
        self.selling_price_entry.grid(row=5, column=1, padx=5, pady=5)
        self.selling_price_entry.bind("<KeyRelease>", self.format_rupiah_live)

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Tambah", command=self.add_product).grid(row=0, column=0, padx=10)
        ttk.Button(btn_frame, text="Edit", command=self.save_edit).grid(row=0, column=1, padx=10)
        ttk.Button(btn_frame, text="Cancel", command=self.cancel_edit).grid(row=0, column=2, padx=10)
        ttk.Button(btn_frame, text="Hapus", command=self.delete_product).grid(row=0, column=3, padx=10)

        # === BAGIAN TREEVIEW RESPONSIF ===
        tree_frame = ttk.Frame(self)
        tree_frame.pack(padx=20, pady=10, fill="both", expand=True)

        tree_scroll_vertical = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll_horizontal = ttk.Scrollbar(tree_frame, orient="horizontal")

        self.tree = ttk.Treeview(
            tree_frame,
            columns=('ID', 'Barcode', 'Name', 'Category', 'Supplier', 'Purchase', 'Selling'),
            show='headings',
            yscrollcommand=tree_scroll_vertical.set,
            xscrollcommand=tree_scroll_horizontal.set
        )

        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", stretch=True, width=100)

        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scroll_vertical.config(command=self.tree.yview)
        tree_scroll_vertical.grid(row=0, column=1, sticky="ns")
        tree_scroll_horizontal.config(command=self.tree.xview)
        tree_scroll_horizontal.grid(row=1, column=0, sticky="ew")

        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

        self.load_categories()
        self.load_supplier()

    def load_categories(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM categories")
        self.categories = {name: id for id, name in cursor.fetchall()}
        self.category_combo["values"] = list(self.categories.keys())
        conn.close()

    def load_supplier(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM supplier")
        self.supplier = {name: id for id, name in cursor.fetchall()}
        self.supplier_combo["values"] = list(self.supplier.keys())
        conn.close()

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT p.id, p.barcode, p.name, c.name, s.name, p.purchase_price, p.selling_price
            FROM product p
            LEFT JOIN categories c ON p.category_id = c.id
            LEFT JOIN supplier s ON p.supplier_id = s.id
        ''')
        for row in cursor.fetchall():
            formatted_row = list(row)
            formatted_row[5] = "{:,.0f}".format(formatted_row[5]).replace(",", ".")
            formatted_row[6] = "{:,.0f}".format(formatted_row[6]).replace(",", ".")
            self.tree.insert('', 'end', values=formatted_row)
        conn.close()
        self.clear_form()

    def clear_form(self):
        self.barcode_entry.delete(0, tk.END)
        self.name_entry.delete(0, tk.END)
        self.category_combo.set("")
        self.supplier_combo.set("")
        self.purchase_price_entry.delete(0, tk.END)
        self.selling_price_entry.delete(0, tk.END)
        self.editing_product_id = None

    def cancel_edit(self):
        self.clear_form()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return
        data = self.tree.item(selected[0])['values']
        self.editing_product_id = data[0]
        self.barcode_entry.delete(0, tk.END)
        self.barcode_entry.insert(0, data[1])
        self.name_entry.delete(0, tk.END)
        self.name_entry.insert(0, data[2])
        self.category_combo.set(data[3])
        self.supplier_combo.set(data[4])
        self.purchase_price_entry.delete(0, tk.END)
        self.purchase_price_entry.insert(0, data[5])
        self.selling_price_entry.delete(0, tk.END)
        self.selling_price_entry.insert(0, data[6])

    def add_product(self):
        try:
            barcode = int(self.barcode_entry.get())
            name = self.name_entry.get()
            category_id = self.categories.get(self.category_combo.get())
            supplier_id = self.supplier.get(self.supplier_combo.get())
            purchase_price = self.parse_rupiah(self.purchase_price_entry.get())
            selling_price = self.parse_rupiah(self.selling_price_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Barcode dan harga harus berupa angka.", parent=self)
            return

        if not name:
            messagebox.showerror("Error", "Nama dan satuan produk wajib diisi.", parent=self)
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                INSERT INTO product (barcode, name, category_id, supplier_id, purchase_price, selling_price)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (barcode, name, category_id, supplier_id, purchase_price, selling_price))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Barcode sudah terdaftar.", parent=self)
        else:
            self.refresh_tree()
            messagebox.showinfo("Sukses", "Produk sudah dimasukkan.", parent=self)
        conn.close()

    def save_edit(self):
        if self.editing_product_id is None:
            messagebox.showinfo("Info", "Pilih data yang akan diedit terlebih dahulu.", parent=self)
            return

        try:
            barcode = int(self.barcode_entry.get())
            name = self.name_entry.get()
            category_id = self.categories.get(self.category_combo.get())
            supplier_id = self.supplier.get(self.supplier_combo.get())
            purchase_price = self.parse_rupiah(self.purchase_price_entry.get())
            selling_price = self.parse_rupiah(self.selling_price_entry.get())
        except ValueError:
            messagebox.showerror("Error", "Barcode dan harga harus berupa angka.", parent=self)
            return

        if not name:
            messagebox.showerror("Error", "Nama dan satuan produk wajib diisi.", parent=self)
            return

        conn = get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute('''
                UPDATE product SET barcode=?, name=?, category_id=?, supplier_id=?, purchase_price=?, selling_price=?
                WHERE id=?
            ''', (barcode, name, category_id, supplier_id, purchase_price, selling_price, self.editing_product_id))
            conn.commit()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Barcode sudah terdaftar pada produk lain.", parent=self)
        else:
            self.refresh_tree()
            messagebox.showinfo("Sukses", "Produk berhasil diedit.", parent=self)
        conn.close()

    def delete_product(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Pilih data yang akan dihapus terlebih dahulu.", parent=self)
            return

        confirm = messagebox.askyesno("Konfirmasi", "Apakah yakin ingin menghapus data ini?", parent=self)
        if not confirm:
            return

        product_id = self.tree.item(selected[0])['values'][0]

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM product WHERE id=?", (product_id,))
        conn.commit()
        conn.close()
        self.refresh_tree()

    def format_rupiah_live(self, event):
        entry = event.widget
        current_value = entry.get()
        cursor_pos = entry.index(tk.INSERT)
        cleaned = ''.join(filter(str.isdigit, current_value))
        if cleaned:
            formatted = "{:,}".format(int(cleaned)).replace(",", ".")
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
            entry.icursor(tk.END)

    def parse_rupiah(self, value):
        return float(value.replace('.', '').strip())
