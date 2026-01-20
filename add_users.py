import tkinter as tk
from tkinter import messagebox
import sqlite3

class AddUsers:
    def __init__(self, root, current_user, back_callback):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Your Pale Green background
        self.card_color = "#ffffff"     # White Card for modern feel
        self.primary_color = "#2e7d32" # Professional Green for Save
        self.view_btn_color = "#2196F3" # Modern Blue for View
        self.back_btn_color = "#616161" # Professional Gray for Back
        
        self.root.title("Clothes Management - Add/Edit User")
        self.root.geometry("1100x600")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        self.user_id = None  
        
        self.create_form()

    def create_form(self):
        # Clear existing widgets to reset the view
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container (Centered)
        form_card = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        form_card.place(relx=0.5, rely=0.5, anchor="center", width=520, height=560)

        # Title Label
        self.title_label = tk.Label(form_card, text="Register New User", font=("Segoe UI", 18, "bold"), 
                                   bg=self.card_color, fg=self.primary_color)
        self.title_label.pack(pady=(30, 20))

        # 2. Input Fields Container
        fields_frame = tk.Frame(form_card, bg=self.card_color)
        fields_frame.pack(padx=60, fill="x")

        # Modern Styled Entry Helper
        def add_styled_entry(label_text, is_password=False):
            tk.Label(fields_frame, text=label_text, font=("Segoe UI", 9, "bold"), 
                     bg=self.card_color, fg="#424242").pack(anchor="w", pady=(8, 2))
            entry = tk.Entry(fields_frame, font=("Segoe UI", 11), bg="#f5f5f5", bd=0, 
                             highlightthickness=1, highlightbackground="#e0e0e0", 
                             show="●" if is_password else "")
            entry.pack(fill="x", ipady=7)
            return entry

        self.username_entry = add_styled_entry("Username")
        self.password_entry = add_styled_entry("Password", is_password=True)
        self.email_entry = add_styled_entry("Email Address")
        self.full_name_entry = add_styled_entry("Full Name")

        # Role Selection (Radio Buttons)
        tk.Label(fields_frame, text="Assign User Role", font=("Segoe UI", 9, "bold"), 
                 bg=self.card_color, fg="#424242").pack(anchor="w", pady=(12, 2))
        
        role_frame = tk.Frame(fields_frame, bg=self.card_color)
        role_frame.pack(fill="x")
        self.role_var = tk.StringVar(value="user")
        
        tk.Radiobutton(role_frame, text="Admin", variable=self.role_var, value="admin",
                       bg=self.card_color, font=("Segoe UI", 10), cursor="hand2").pack(side="left", padx=5)
        tk.Radiobutton(role_frame, text="User", variable=self.role_var, value="user",
                       bg=self.card_color, font=("Segoe UI", 10), cursor="hand2").pack(side="left", padx=20)

        # 3. ALL THREE BUTTONS (Modern Structure)
        btn_container = tk.Frame(form_card, bg=self.card_color)
        btn_container.pack(fill="x", padx=60, pady=(25, 0))

        # --- SAVE USER BUTTON (Primary) ---
        tk.Button(
            btn_container, text="SAVE USER", command=self.save_user,
            bg=self.primary_color, fg="white", font=("Segoe UI", 10, "bold"),
            bd=0, cursor="hand2", activebackground="#1b5e20", activeforeground="white"
        ).pack(fill="x", ipady=10)

        # --- VIEW AND BACK BUTTONS (Secondary Row) ---
        nav_frame = tk.Frame(btn_container, bg=self.card_color)
        nav_frame.pack(fill="x", pady=15)

        tk.Button(
            nav_frame, text="View All Users", command=self.view_users,
            bg=self.view_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
            bd=0, cursor="hand2", activebackground="#1565C0", width=18
        ).pack(side="left", ipady=8)

        tk.Button(
            nav_frame, text="Back to Dashboard", command=self.back_callback,
            bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
            bd=0, cursor="hand2", activebackground="#424242", width=18
        ).pack(side="right", ipady=8)

    def load_user(self, user_id):
        self.user_id = user_id
        self.title_label.config(text="Edit Existing User")
        self.cursor.execute("SELECT username, password, email, full_name, role FROM Users WHERE user_id = ?", (user_id,))
        user = self.cursor.fetchone()
        if user:
            self.username_entry.delete(0, tk.END)
            self.username_entry.insert(0, user[0])
            self.password_entry.delete(0, tk.END)
            self.password_entry.insert(0, user[1])
            self.email_entry.delete(0, tk.END)
            self.email_entry.insert(0, user[2])
            self.full_name_entry.delete(0, tk.END)
            self.full_name_entry.insert(0, user[3])
            self.role_var.set(user[4])

    def save_user(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        email = self.email_entry.get().strip()
        full_name = self.full_name_entry.get().strip()
        role = self.role_var.get()

        if not all([username, password, email, full_name]):
            messagebox.showerror("Error", "All fields are required")
            return

        try:
            if self.user_id:  # Update existing user
                self.cursor.execute('''
                    UPDATE Users SET username = ?, password = ?, email = ?, full_name = ?, role = ?
                    WHERE user_id = ?
                ''', (username, password, email, full_name, role, self.user_id))
                messagebox.showinfo("Success", "User updated successfully")
            else:  # Add new user
                self.cursor.execute('''
                    INSERT INTO Users (username, password, email, full_name, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, password, email, full_name, role))
                messagebox.showinfo("Success", "User added successfully")
            
            self.conn.commit()
            self.clear_form()
            self.back_callback() # Take back to dashboard after save
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "Username or email already exists")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save user: {e}")

    def clear_form(self):
        self.user_id = None
        self.username_entry.delete(0, tk.END)
        self.password_entry.delete(0, tk.END)
        self.email_entry.delete(0, tk.END)
        self.full_name_entry.delete(0, tk.END)
        self.role_var.set("user")

    def view_users(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from view_users import ViewUsers
        ViewUsers(self.root, self.current_user, self.back_callback)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()