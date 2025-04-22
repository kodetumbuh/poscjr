import tkinter as tk

def show_about(parent):
    win = tk.Toplevel(parent)
    win.title("Tentang Aplikasi")
    win.geometry("300x200")
    tk.Label(win, text="Aplikasi POS\nVersi 1.0", font=("Arial", 14)).pack(expand=True)