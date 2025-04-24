import tkinter as tk
from menu.menubar import MenuBar

def main():
    root = tk.Tk()
    root.title("Sistem POS")
    root.geometry("800x600")

    container = tk.Frame(root)
    container.pack(fill="both", expand=True)

    menu = MenuBar(root, container)
    root.config(menu=menu)

    root.mainloop()

if __name__ == "__main__":
    main()