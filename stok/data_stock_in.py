import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from tkcalendar import DateEntry, Calendar

# === DATABASE SETUP ===
def get_connection():
    return sqlite3.connect("pos.db")

def create_stock_in_table():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS stock_in (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_id INTEGER NOT NULL,
            supplier_id INTEGER NOT NULL,
            date TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            unit TEXT NOT NULL,
            note TEXT
        )
    ''')
    conn.commit()
    conn.close()

# === CRUD STOCK IN WINDOW ===
class StockInCRUD(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Manajemen Barang Masuk")
        self.geometry("850x500")

        self.editing_id = None
        create_stock_in_table()
        self.products = self.get_products()
        self.suppliers = self.get_suppliers()
        self.setup_ui()
        self.refresh_tree()

    def get_products(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM product")
        result = cursor.fetchall()
        conn.close()
        return {name: pid for pid, name in result}

    def get_suppliers(self):
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, name FROM supplier")
        result = cursor.fetchall()
        conn.close()
        return {name: sid for sid, name in result}

    def setup_ui(self):
        title = ttk.Label(self, text="Data Barang Masuk", font=("Arial", 20, "bold"))
        title.pack(pady=10)

        form = ttk.Frame(self)
        form.pack(pady=10)

        # Form Inputs
        ttk.Label(form, text="Produk").grid(row=0, column=0, padx=5, pady=5, sticky="e")
        self.product_var = tk.StringVar()
        self.product_entry = tk.Entry(form, textvariable=self.product_var, state="normal")
        self.product_entry.grid(row=0, column=1, padx=5, pady=5)
        self.product_entry.bind('<KeyRelease>', self.on_product_keyrelease)  # Event handler for autocomplete

        # Listbox for product suggestions
        self.product_listbox = tk.Listbox(form, width=20, height=5)
        self.product_listbox.grid(row=1, column=1, padx=5, pady=0)
        self.product_listbox.bind("<Double-1>", self.on_product_select)
        self.product_listbox.grid_remove()  # Hide by default

        ttk.Label(form, text="Supplier").grid(row=2, column=0, padx=5, pady=5, sticky="e")
        self.supplier_var = tk.StringVar()
        self.supplier_combo = ttk.Combobox(form, textvariable=self.supplier_var, values=list(self.suppliers.keys()), state="readonly")
        self.supplier_combo.grid(row=2, column=1, padx=5, pady=5)

        ttk.Label(form, text="Tanggal").grid(row=3, column=0, padx=5, pady=5, sticky="e")
        self.date_var = tk.StringVar()
        self.date_entry = tk.Entry(form, textvariable=self.date_var, state="readonly", width=22)
        self.date_entry.grid(row=3, column=1, padx=5, pady=5)
        self.date_entry.bind("<Button-1>", self.show_calendar)

        ttk.Label(form, text="Jumlah").grid(row=4, column=0, padx=5, pady=5, sticky="e")
        self.quantity_entry = tk.Entry(form)
        self.quantity_entry.grid(row=4, column=1, padx=5, pady=5)
        self.quantity_entry.bind("<KeyRelease>", self.format_angka)

        ttk.Label(form, text="Satuan").grid(row=5, column=0, padx=5, pady=5, sticky="e")
        self.unit_entry = tk.Entry(form)
        self.unit_entry.grid(row=5, column=1, padx=5, pady=5)

        ttk.Label(form, text="Catatan").grid(row=6, column=0, padx=5, pady=5, sticky="e")
        self.note_entry = tk.Entry(form)
        self.note_entry.grid(row=6, column=1, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=10)

        ttk.Button(btn_frame, text="Tambah", command=self.add_data).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="Edit", command=self.save_edit).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="Batal", command=self.cancel_edit).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="Hapus", command=self.delete_data).grid(row=0, column=3, padx=5)

        # Treeview
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill="both", expand=True, padx=20, pady=10)

        tree_scroll = ttk.Scrollbar(tree_frame, orient="vertical")
        tree_scroll.pack(side="right", fill="y")

        self.tree = ttk.Treeview(tree_frame, columns=("ID", "Product ID", "Supplier ID", "Date", "Quantity", "Unit", "Note"), show="headings", yscrollcommand=tree_scroll.set)
        for col in self.tree["columns"]:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center")
        self.tree.pack(fill="both", expand=True)
        tree_scroll.config(command=self.tree.yview)

        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)

    def on_product_keyrelease(self, event):
        typed_text = self.product_var.get().lower()
        filtered_products = [p for p in self.products.keys() if typed_text in p.lower()][:6]
        
        # Show listbox if there are matching products
        if filtered_products:
            self.product_listbox.grid()  # Show listbox
            self.product_listbox.delete(0, tk.END)
            for product in filtered_products:
                self.product_listbox.insert(tk.END, product)
        else:
            self.product_listbox.grid_remove()  # Hide listbox if no matches

    def on_product_select(self, event):
        selected_product = self.product_listbox.get(tk.ACTIVE)
        self.product_var.set(selected_product)
        self.product_listbox.grid_remove()  # Hide listbox after selection

    def refresh_tree(self):
        for i in self.tree.get_children():
            self.tree.delete(i)

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM stock_in")
        for row in cursor.fetchall():
            self.tree.insert('', 'end', values=row)
        conn.close()
        self.clear_form()
        
    def show_calendar(self, event=None):
        popup_width = 250
        popup_height = 220

        # Calculate the center position of the screen
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        pos_x = (screen_width // 2) - (popup_width // 2)
        pos_y = (screen_height // 2) - (popup_height // 2)

        top = tk.Toplevel(self)
        top.title("Pilih Tanggal")
        top.geometry(f"{popup_width}x{popup_height}+{pos_x}+{pos_y}")
        top.grab_set()
        top.focus_force()

        cal = Calendar(top, selectmode='day', date_pattern='yyyy-mm-dd', locale='id_ID')
        cal.pack(pady=10)

        def on_date_select(event):
            tanggal = cal.get_date()
            self.date_var.set(tanggal)
            top.destroy()

        cal.bind("<<CalendarSelected>>", on_date_select)
    
    def clear_form(self):
        self.product_var.set("")
        self.supplier_combo.set("")
        self.date_var.set("")
        self.quantity_entry.delete(0, tk.END)
        self.unit_entry.delete(0, tk.END)
        self.note_entry.delete(0, tk.END)
        self.editing_id = None
        self.product_listbox.grid_remove()  # Hide listbox on form clear

    def cancel_edit(self):
        self.clear_form()

    def on_tree_select(self, event):
        selected = self.tree.selection()
        if not selected:
            return

        data = self.tree.item(selected[0])['values']
        self.editing_id = data[0]

        self.product_var.set(self.get_key_by_value(self.products, data[1]))
        self.supplier_combo.set(self.get_key_by_value(self.suppliers, data[2]))
        self.date_var.set(data[3])
        self.quantity_entry.delete(0, tk.END)
        self.quantity_entry.insert(0, data[4])
        self.unit_entry.delete(0, tk.END)
        self.unit_entry.insert(0, data[5])
        self.note_entry.delete(0, tk.END)
        self.note_entry.insert(0, data[6])

    def get_key_by_value(self, dictionary, value):
        for k, v in dictionary.items():
            if v == value:
                return k
        return ""

    def add_data(self):
        try:
            product_id = self.products.get(self.product_var.get())
            supplier_id = self.suppliers.get(self.supplier_var.get())
            date = self.date_var.get()
            quantity = self.quantity_entry.get().replace(".", "")
            unit = self.unit_entry.get()
            note = self.note_entry.get()

            if not all([product_id, supplier_id, date, quantity, unit]):
                raise ValueError("Field wajib diisi kecuali catatan.")

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO stock_in (product_id, supplier_id, date, quantity, unit, note)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (product_id, supplier_id, date, int(quantity), unit, note))
            conn.commit()
            conn.close()
            self.refresh_tree()
            messagebox.showinfo("Sukses", "Data berhasil ditambahkan!", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def save_edit(self):
        if not self.editing_id:
            return
        try:
            product_id = self.products.get(self.product_var.get())
            supplier_id = self.suppliers.get(self.supplier_var.get())
            date = self.date_var.get()
            quantity = self.quantity_entry.get().replace(".", "")
            unit = self.unit_entry.get()
            note = self.note_entry.get()

            if not all([product_id, supplier_id, date, quantity, unit]):
                raise ValueError("Field wajib diisi kecuali catatan.")

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE stock_in
                SET product_id=?, supplier_id=?, date=?, quantity=?, unit=?, note=?
                WHERE id=?
            ''', (product_id, supplier_id, date, int(quantity), unit, note, self.editing_id))
            conn.commit()
            conn.close()
            self.refresh_tree()
            messagebox.showinfo("Sukses", "Data berhasil diperbarui!", parent=self)
        except Exception as e:
            messagebox.showerror("Error", str(e), parent=self)

    def delete_data(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showerror("Error", "Pilih data yang ingin dihapus.", parent=self)
            return

        stock_id = self.tree.item(selected[0])['values'][0]
        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM stock_in WHERE id=?", (stock_id,))
        conn.commit()
        conn.close()
        self.refresh_tree()
        messagebox.showinfo("Sukses", "Data berhasil dihapus.", parent=self)
        
    def format_angka(self, event):
        entry = event.widget
        current_value = entry.get()
        cursor_pos = entry.index(tk.INSERT)
        cleaned = ''.join(filter(str.isdigit, current_value))
        if cleaned:
            formatted = "{:,}".format(int(cleaned)).replace(",", ".")
            entry.delete(0, tk.END)
            entry.insert(0, formatted)
            entry.icursor(cursor_pos)