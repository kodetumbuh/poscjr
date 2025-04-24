import tkinter as tk
from tkinter import messagebox
from pengaturan.about import show_about

class MenuBar(tk.Menu):
    def __init__(self, parent):
        super().__init__(parent)

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

        # Pengaturan Menu
        setting_menu = tk.Menu(self, tearoff=0)
        setting_menu.add_command(label="About", command=lambda: show_about(parent))
        self.add_cascade(label="Pengaturan", menu=setting_menu)

    def new_file(self):
        messagebox.showinfo("New File", "Create a new file")

    def open_file(self):
        messagebox.showinfo("Open File", "Open an existing file")

    def show_about(self):
        messagebox.showinfo("About", "Aplikasi ini bersifat beta dan masih dalam pengembangan")
