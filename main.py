import tkinter as tk
from tkinter import ttk
from menu.menubar import MenuBar

def main():
    root = tk.Tk()
    root.title("Sistem POS")
    
    root.state('zoomed')

    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    title = ttk.Label(container, text="Data Pengguna Admin", font=("Arial", 20, "bold"))
    title.pack(pady=10)

    menu = MenuBar(root, container)
    root.config(menu=menu)

    root.mainloop()

if __name__ == "__main__":
    main()
