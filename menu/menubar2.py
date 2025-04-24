import tkinter as tk
from tkinter import messagebox
from pengaturan.about import show_about
from pengaturan.user import UserCRUD

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

        # Help Menu
        help_menu = tk.Menu(self, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        self.add_cascade(label="Help", menu=help_menu)
        
    def new_file(self):
        messagebox.showinfo("New File", "Create a new file")

    def open_file(self):
        messagebox.showinfo("Open File", "Open an existing file")

    def show_about(self):
        messagebox.showinfo("About", "Aplikasi ini bersifat beta dan masih dalam pengembangan")

    def show_user_crud(self):
        user_window = UserCRUD(self)
        user_window.grab_set()