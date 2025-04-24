import tkinter as tk
from tkinter import ttk
from menu.menubar2 import MenuBar

def main():
    root = tk.Tk()
    root.title("Sistem POS")
    root.geometry("800x600")

    container = tk.Frame(root)
    title = ttk.Label(text="Data Pengguna Kasir", font=("Arial", 20, "bold"))
    title.pack(pady=10)
    container.pack(fill="both", expand=True)

    menu = MenuBar(root, container)
    root.config(menu=menu)

    root.mainloop()

if __name__ == "__main__":
    main()