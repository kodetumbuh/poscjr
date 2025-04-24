import tkinter as tk
from tkinter import messagebox
from main import main  # Import fungsi main dari main.py

def check_login(username, password):
    # Contoh data login hardcoded
    return username == "admin" and password == "1234"

def attempt_login():
    user = entry_username.get()
    pwd = entry_password.get()

    if check_login(user, pwd):
        root.destroy()  # Tutup jendela login
        main()          # Masuk ke aplikasi utama
    else:
        messagebox.showerror("Login Gagal", "Username atau Password salah!")

root = tk.Tk()
root.title("Login")
root.geometry("300x150")
root.resizable(False, False)

tk.Label(root, text="Username").pack(pady=(10, 0))
entry_username = tk.Entry(root)
entry_username.pack()

tk.Label(root, text="Password").pack()
entry_password = tk.Entry(root, show="*")
entry_password.pack()

tk.Button(root, text="Login", command=attempt_login).pack(pady=10)

root.mainloop()