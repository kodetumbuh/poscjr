import tkinter as tk
from tkinter import messagebox
from pengaturan.about import show_about
from pengaturan.user import UserCRUD
from supplier.data_supplier import SupplierCRUD
from produk.data_kategori import CategoryCRUD
from produk.data_produk import ProductCRUD
from stok.data_stock_in import StockInCRUD

class MenuBar(tk.Menu):
    def __init__(self, parent, container):  # tambahkan container (tempat frame muncul)
        super().__init__(parent)
        self.parent = parent
        self.container = container  # simpan reference ke frame utama

        # File Menu
        file_menu = tk.Menu(self, tearoff=0)
        file_menu.add_command(label="New", command=self.new_file)
        file_menu.add_command(label="Open", command=self.open_file)
        file_menu.add_command(label="Exit", command=parent.quit)
        self.add_cascade(label="File", menu=file_menu)
        
        # Produk
        crud_produk = tk.Menu(self, tearoff=0)
        crud_produk.add_command(label="Produk", command=self.show_produk_data_crud)
        crud_produk.add_command(label="Kategori", command=self.show_produk_kategori_crud)
        self.add_cascade(label="Produk", menu=crud_produk)

        # Data Supplier
        crud_supplier = tk.Menu(self, tearoff=0)
        crud_supplier.add_command(label="Data Supplier", command=self.show_supplier_crud)
        self.add_cascade(label="Supplier", menu=crud_supplier)
        
        # Data Stock
        crud_stock = tk.Menu(self, tearoff=0)
        crud_stock.add_command(label="Data Stock", command=self.show_stok_data_stock_in)
        self.add_cascade(label="Supplier", menu=crud_stock)

        # Help Menu
        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help", menu=help_menu)

        # Pengaturan Menu
        setting_menu = tk.Menu(self, tearoff=0)
        setting_menu.add_command(label="User", command=self.show_user_crud)
        setting_menu.add_command(label="About", command=lambda: show_about(parent))
        self.add_cascade(label="Pengaturan", menu=setting_menu)

    def new_file(self):
        messagebox.showinfo("New File", "Create a new file")

    def open_file(self):
        messagebox.showinfo("Open File", "Open an existing file")

    def show_about(self):
        messagebox.showinfo("About", "Aplikasi ini bersifat beta dan masih dalam pengembangan")

    def show_user_crud(self):
        user_window = UserCRUD(self)
        user_window.grab_set()
        user_window.focus_force()
        
    def show_supplier_crud(self):
        user_window = SupplierCRUD(self)
        user_window.grab_set()
        user_window.focus_force()
        
    def show_produk_kategori_crud(self):
        user_window = CategoryCRUD(self)
        user_window.grab_set()
        user_window.focus_force()
        
    def show_produk_data_crud(self):
        user_window = ProductCRUD(self)
        user_window.grab_set()
        user_window.focus_force()
    
    def show_stok_data_stock_in(self):
        user_window = StockInCRUD(self)
        user_window.grab_set()
        user_window.focus_force()