import tkinter as tk
from tkinter import messagebox
import sqlite3

class AddCategories:
    def __init__(self, root, current_user, back_callback):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Pale Green background
        self.card_color = "#ffffff"     # White Card
        self.primary_color = "#2e7d32" # Dark Green for Save
        self.view_btn_color = "#1976D2" # Bright Blue for View
        self.back_btn_color = "#616161" # Professional Gray for Back
        
        self.root.title("Clothes Management - Add/Edit Category")
        self.root.geometry("1100x600")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        self.category_id = None  
        
        self.create_form()

    def create_form(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container (Centered)
        form_card = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        form_card.place(relx=0.5, rely=0.5, anchor="center", width=500, height=400)

        # Header Title
        tk.Label(form_card, text="INVENTORY MANAGEMENT", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(pady=(40, 0))
        
        self.title_label = tk.Label(form_card, text="Add/Edit Category", font=("Segoe UI", 20, "bold"), 
                                   bg=self.card_color, fg=self.primary_color)
        self.title_label.pack(pady=(0, 30))

        # 2. Input Fields Container
        fields_frame = tk.Frame(form_card, bg=self.card_color)
        fields_frame.pack(padx=60, fill="x")

        tk.Label(fields_frame, text="Category Name", font=("Segoe UI", 10, "bold"), 
                 bg=self.card_color, fg="#424242").pack(anchor="w", pady=(0, 5))
        
        self.category_name_entry = tk.Entry(fields_frame, font=("Segoe UI", 12), bg="#f5f5f5", bd=0, 
                                           highlightthickness=1, highlightbackground="#e0e0e0", 
                                           highlightcolor=self.primary_color)
        self.category_name_entry.pack(fill="x", ipady=8)
        self.category_name_entry.focus_set()

        # 3. ACTION BUTTONS (High-Visibility Modern Structure)
        btn_container = tk.Frame(form_card, bg=self.card_color)
        btn_container.pack(fill="x", padx=60, pady=(40, 0))

        # --- SAVE BUTTON (Primary) ---
        tk.Button(
            btn_container, text="SAVE CATEGORY", command=self.save_category,
            bg=self.primary_color, fg="white", font=("Segoe UI", 11, "bold"),
            bd=0, cursor="hand2", activebackground="#1b5e20", activeforeground="white"
        ).pack(fill="x", ipady=12)

        # --- VIEW AND BACK BUTTONS (Secondary Row) ---
        nav_frame = tk.Frame(btn_container, bg=self.card_color)
        nav_frame.pack(fill="x", pady=15)

        tk.Button(
            nav_frame, text="View Categories", command=self.view_categories,
            bg=self.view_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
            bd=0, cursor="hand2", activebackground="#1565C0", width=18
        ).pack(side="left", ipady=8)

        tk.Button(
            nav_frame, text="Back to Dashboard", command=self.back_callback,
            bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
            bd=0, cursor="hand2", activebackground="#424242", width=18
        ).pack(side="right", ipady=8)

    def load_category(self, category_id):
        self.category_id = category_id
        self.title_label.config(text="Update Category")
        self.cursor.execute("SELECT category_name FROM Categories WHERE category_id = ?", (category_id,))
        category = self.cursor.fetchone()
        if category:
            self.category_name_entry.delete(0, tk.END)
            self.category_name_entry.insert(0, category[0])

    def save_category(self):
        category_name = self.category_name_entry.get().strip()

        if not category_name:
            messagebox.showerror("Error", "Category name cannot be empty.")
            return

        try:
            if self.category_id:  # Update
                self.cursor.execute('''
                    UPDATE Categories SET category_name = ?
                    WHERE category_id = ?
                ''', (category_name, self.category_id))
                messagebox.showinfo("Success", "Category updated successfully")
            else:  # Add New
                self.cursor.execute('''
                    INSERT INTO Categories (category_name)
                    VALUES (?)
                ''', (category_name,))
                messagebox.showinfo("Success", "New category added successfully")
            
            self.conn.commit()
            self.clear_form()
            self.back_callback() # Navigate back after success
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This category name already exists.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save category: {e}")

    def clear_form(self):
        self.category_id = None
        self.category_name_entry.delete(0, tk.END)

    def view_categories(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from view_categories import ViewCategories
        ViewCategories(self.root, self.current_user, self.back_callback)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()