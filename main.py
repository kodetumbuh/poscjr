import tkinter as tk
from menubar import MenuBar

def main():
    root = tk.Tk()
    root.title("Aplikasi dengan MenuBar")

    root.state('zoomed')  # Berfungsi di Windows

    menu = MenuBar(root)
    root.config(menu=menu)

    root.mainloop()

if __name__ == "__main__":
    main()