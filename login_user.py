import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import hashlib
import subprocess

def get_connection():
    return sqlite3.connect("pos.db")

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

class LoginWindow:
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.geometry("300x200")

        ttk.Label(root, text="Username:").pack(pady=5)
        self.username_entry = ttk.Entry(root)
        self.username_entry.pack(pady=5)


        ttk.Label(root, text="Password:").pack(pady=5)
        self.password_entry = ttk.Entry(root, show="*")
        self.password_entry.pack(pady=5)
        
        #bind tekan tombol enter
        self.root.bind('<Return>', lambda event: self.login())

        ttk.Button(root, text="Login", command=self.login).pack(pady=10)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()

        conn = get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT role, password FROM user WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            role, stored_hash = result
            if hash_password(password) == stored_hash:
                messagebox.showinfo("Login Berhasil", f"Selamat datang, {username} ({role})")
                self.root.destroy()
                if role == "admin":
                    subprocess.Popen(["python", "main.py"])
                else:
                    subprocess.Popen(["python", "main2.py"])
            else:
                messagebox.showerror("Error", "Password salah")
        else:
            messagebox.showerror("Error", "User tidak ditemukan")

if __name__ == "__main__":
    root = tk.Tk()
    app = LoginWindow(root)
    root.mainloop()