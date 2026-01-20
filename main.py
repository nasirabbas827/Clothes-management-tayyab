import tkinter as tk
from tkinter import messagebox
import sqlite3

class PharmacyApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Clothes Management System - Professional Login")
        self.root.geometry("1100x600")
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"  # Your Pale Green
        self.card_color = "#ffffff" # White Card
        self.primary_color = "#2e7d32" # Dark Green for Text/Buttons
        self.accent_color = "#1976D2"  # Blue for highlights
        
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        self.current_user = None
        self.create_login_page()

    def create_login_page(self):
        # Clear the window
        for widget in self.root.winfo_children():
            widget.destroy()

        # Main Card Container
        # We use a frame with a highlightthickness to simulate a subtle shadow/border
        login_card = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        login_card.place(relx=0.5, rely=0.5, anchor="center", width=450, height=500)

        # Header Section
        tk.Label(login_card, text="WELCOME BACK", font=("Helvetica", 10, "bold"), 
                 bg=self.card_color, fg="#757575").pack(pady=(40, 5))
        
        tk.Label(login_card, text="Clothes Management", font=("Segoe UI", 20, "bold"), 
                 bg=self.card_color, fg=self.primary_color).pack(pady=(0, 30))

        # Input Area Frame
        input_frame = tk.Frame(login_card, bg=self.card_color)
        input_frame.pack(padx=50, fill="x")

        # Username
        tk.Label(input_frame, text="Username", font=("Segoe UI", 10, "bold"), 
                 bg=self.card_color, fg="#424242").pack(anchor="w", pady=(10, 5))
        self.username_entry = tk.Entry(input_frame, font=("Segoe UI", 12),
                                      bg="#f5f5f5", bd=0, highlightthickness=1, 
                                      highlightbackground="#e0e0e0", highlightcolor=self.primary_color)
        self.username_entry.pack(fill="x", ipady=8)

        # Password
        tk.Label(input_frame, text="Password", font=("Segoe UI", 10, "bold"), 
                 bg=self.card_color, fg="#424242").pack(anchor="w", pady=(20, 5))
        self.password_entry = tk.Entry(input_frame, show="●", font=("Segoe UI", 12),
                                      bg="#f5f5f5", bd=0, highlightthickness=1, 
                                      highlightbackground="#e0e0e0", highlightcolor=self.primary_color)
        self.password_entry.pack(fill="x", ipady=8)

        # Button Section
        btn_frame = tk.Frame(login_card, bg=self.card_color)
        btn_frame.pack(fill="x", padx=50, pady=40)

        # Login Button
        login_btn = tk.Button(btn_frame, text="LOGIN TO SYSTEM", command=self.login,
                             bg=self.primary_color, fg="white", font=("Segoe UI", 11, "bold"),
                             bd=0, cursor="hand2", activebackground="#1b5e20", activeforeground="white")
        login_btn.pack(fill="x", ipady=12)

        # Clear Button (Subtle link style)
        clear_btn = tk.Button(btn_frame, text="Clear Fields", command=self.clear_entries,
                             bg=self.card_color, fg="#757575", font=("Segoe UI", 9, "underline"),
                             bd=0, cursor="hand2", activebackground=self.card_color)
        clear_btn.pack(pady=10)

    def clear_entries(self):
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)

    def login(self):
        username = self.username_entry.get()
        password = self.password_entry.get()
        
        if not username or not password:
            messagebox.showerror("Login Failed", "Username and Password fields cannot be empty.")
            return

        self.cursor.execute("SELECT user_id, username, password, role, full_name FROM Users WHERE username = ? AND password = ?",
                          (username, password))
        user = self.cursor.fetchone()
        
        if user:
            self.current_user = {
                'user_id': user[0],
                'username': user[1],
                'role': user[3],
                'full_name': user[4]
            }
            if self.current_user['role'] == 'admin':
                self.show_admin_dashboard()
            else:
                self.show_user_dashboard()
        else:
            messagebox.showerror("Access Denied", "The credentials you entered are incorrect.")

    def show_admin_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        try:
            from admin_dashboard import AdminDashboard
            AdminDashboard(self.root, self.current_user, self.show_login_page)
        except ImportError:
            messagebox.showerror("Error", "Admin Dashboard file not found!")

    def show_user_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        try:
            from user_dashboard import UserDashboard
            UserDashboard(self.root, self.current_user, self.show_login_page)
        except ImportError:
            messagebox.showerror("Error", "User Dashboard file not found!")

    def show_login_page(self):
        self.current_user = None
        self.create_login_page()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()

if __name__ == "__main__":
    root = tk.Tk()
    app = PharmacyApp(root)
    root.mainloop()