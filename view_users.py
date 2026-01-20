import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ViewUsers:
    def __init__(self, root, current_user, back_callback):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Pale Green background
        self.card_color = "#ffffff"     # White Card
        self.primary_color = "#2e7d32"  # Dark Green
        self.back_btn_color = "#F44336"   # Red
        self.add_btn_color = "#4CAF50"    # Success Green
        
        self.root.title("Clothes - User Management")
        self.root.geometry("1100x650")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        
        self.create_view()

    def create_view(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container
        container = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.85)

        # --- TOP NAVIGATION ROW (Title + Buttons) ---
        top_nav = tk.Frame(container, bg=self.card_color)
        top_nav.pack(fill="x", padx=40, pady=(25, 15))

        # Title Section
        title_frame = tk.Frame(top_nav, bg=self.card_color)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="SYSTEM ADMINISTRATION", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(anchor="w")
        tk.Label(title_frame, text="User Directory", font=("Segoe UI", 18, "bold"), 
                 bg=self.card_color, fg=self.primary_color).pack(anchor="w")

        # Action Buttons (Pinned to top right)
        btn_nav = tk.Frame(top_nav, bg=self.card_color)
        btn_nav.pack(side="right", pady=5)

        tk.Button(btn_nav, text="+ ADD NEW USER", command=self.add_user,
                  bg=self.add_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=18).pack(side="left", padx=5, ipady=8)

        tk.Button(btn_nav, text="← DASHBOARD", command=self.back_callback,
                  bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=18).pack(side="left", padx=5, ipady=8)

        # --- 2. INFORMATION BAR ---
        info_bar = tk.Frame(container, bg="#f8f9fa", padx=15, pady=8)
        info_bar.pack(fill="x", padx=40, pady=(0, 10))
        tk.Label(info_bar, text="Double-click a user row to edit their details.", 
                 font=("Segoe UI", 9, "italic"), bg="#f8f9fa", fg="#616161").pack(side="left")

        # --- 3. USERS TABLE ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#f1f1f1")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=35)
        style.map("Treeview", background=[('selected', '#e8f5e9')], foreground=[('selected', 'black')])

        table_frame = tk.Frame(container, bg=self.card_color)
        table_frame.pack(padx=40, pady=(10, 30), fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Username", "Email", "Full Name", "Role"), 
                                 show="headings")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.heading("ID", text="User ID")
        self.tree.heading("Username", text="Username")
        self.tree.heading("Email", text="Email Address")
        self.tree.heading("Full Name", text="Full Name")
        self.tree.heading("Role", text="Role")

        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Username", width=150, anchor="w")
        self.tree.column("Email", width=250, anchor="w")
        self.tree.column("Full Name", width=200, anchor="w")
        self.tree.column("Role", width=120, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_users()
        self.tree.bind("<Double-1>", self.edit_user)

    def load_users(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

        try:
            self.cursor.execute("SELECT user_id, username, email, full_name, role FROM Users")
            for user in self.cursor.fetchall():
                self.tree.insert("", "end", values=user)
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load users: {e}")

    def edit_user(self, event):
        item = self.tree.selection()
        if not item:
            return
        user_id = self.tree.item(item)["values"][0]
        for widget in self.root.winfo_children():
            widget.destroy()
        from add_users import AddUsers
        add_user_page = AddUsers(self.root, self.current_user, self.back_callback)
        add_user_page.load_user(user_id)

    def add_user(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from add_users import AddUsers
        AddUsers(self.root, self.current_user, self.back_callback)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()