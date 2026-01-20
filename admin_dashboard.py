import tkinter as tk
from tkinter import messagebox

class AdminDashboard:
    def __init__(self, root, user, logout_callback):
        self.root = root
        self.user = user
        self.logout_callback = logout_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Pale Green background
        self.header_color = "#2e7d32"   # Dark Green header
        self.card_color = "#ffffff"     # White for content
        self.btn_color = "#43a047"      # Medium Green for buttons
        
        self.root.title("Clothes Management - Admin Panel")
        self.root.geometry("1100x600")
        self.root.configure(bg=self.bg_color)
        
        self.create_dashboard()

    def create_dashboard(self):
        # 1. Header Section
        header = tk.Frame(self.root, bg=self.header_color, height=80)
        header.pack(fill="x", side="top")
        
        welcome_txt = f"Welcome, {self.user['full_name']} (Administrator)"
        tk.Label(header, text=welcome_txt, font=("Segoe UI", 16, "bold"), 
                 bg=self.header_color, fg="white").pack(side="left", padx=30, pady=20)
        
        tk.Button(header, text="Logout", command=self.logout, font=("Segoe UI", 10, "bold"),
                  bg="#d32f2f", fg="white", bd=0, padx=20, cursor="hand2").pack(side="right", padx=30)

        # 2. Main Content Area (Centered Card)
        content_card = tk.Frame(self.root, bg=self.card_color, bd=0, 
                               highlightbackground="#d1d1d1", highlightthickness=1)
        content_card.place(relx=0.5, rely=0.55, anchor="center", width=950, height=450)

        tk.Label(content_card, text="MANAGEMENT CONTROL PANEL", font=("Helvetica", 12, "bold"),
                 bg=self.card_color, fg="#757575").pack(pady=(20, 10))

        # 3. Button Grid Container
        grid_frame = tk.Frame(content_card, bg=self.card_color)
        grid_frame.pack(expand=True, padx=40, pady=20)

        # Define button data: (Text, Command)
        buttons = [
            ("Add User", self.add_user), ("View Users", self.view_users),
            ("Add Categories", self.add_categories), ("View Categories", self.view_categories),
            ("Add Items", self.add_items), ("View Items", self.view_items),
            ("Add Purchase", self.add_purchase), ("View Purchases", self.view_purchases),
            ("View Sales", self.view_sales), ("Reports", self.generate_reports)
        ]

        # Create Buttons in a 2x5 grid
        row, col = 0, 0
        for text, cmd in buttons:
            btn = tk.Button(grid_frame, text=text, command=cmd, width=18,
                            bg=self.btn_color, fg="white", font=("Segoe UI", 11, "bold"),
                            bd=0, cursor="hand2", activebackground="#2e7d32", activeforeground="white")
            btn.grid(row=row, column=col, padx=10, pady=10, ipady=12)
            
            col += 1
            if col > 3: # Move to next row after 4 columns
                col = 0
                row += 1

    # --- Navigation Logic ---
    def add_user(self):
        self.clear_root()
        from add_users import AddUsers
        AddUsers(self.root, self.user, self.show_dashboard)

    def view_users(self):
        self.clear_root()
        from view_users import ViewUsers
        ViewUsers(self.root, self.user, self.show_dashboard)

    def add_categories(self):
        self.clear_root()
        from add_categories import AddCategories
        AddCategories(self.root, self.user, self.show_dashboard)

    def view_categories(self):
        self.clear_root()
        from view_categories import ViewCategories
        ViewCategories(self.root, self.user, self.show_dashboard)

    def add_items(self):
        self.clear_root()
        from add_items import AddItems
        AddItems(self.root, self.user, self.show_dashboard)

    def view_items(self):
        self.clear_root()
        from view_items import ViewItems
        ViewItems(self.root, self.user, self.show_dashboard)

    def add_purchase(self):
        self.clear_root()
        from add_purchase import AddPurchase
        AddPurchase(self.root, self.user, self.show_dashboard)

    def view_purchases(self):
        self.clear_root()
        from view_purchase import ViewPurchases
        ViewPurchases(self.root, self.user, self.show_dashboard)

    def view_sales(self):
        self.clear_root()
        from view_sales import ViewSales
        ViewSales(self.root, self.user, self.show_dashboard)

    def generate_reports(self):
        self.clear_root()
        from generate_reports import GenerateReports
        GenerateReports(self.root, self.user, self.show_dashboard)

    def clear_root(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def show_dashboard(self):
        self.clear_root()
        self.create_dashboard()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to logout?"):
            self.logout_callback()