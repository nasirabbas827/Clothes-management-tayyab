import tkinter as tk
from tkinter import messagebox, ttk
import sqlite3
from datetime import datetime

class AddPurchase:
    def __init__(self, root, current_user, back_callback):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Your Pale Green background
        self.card_color = "#ffffff"     # White Card
        self.primary_color = "#2e7d32" # Dark Green for Save
        self.view_btn_color = "#1976D2" # Bright Blue for View
        self.back_btn_color = "#616161" # Professional Gray for Back
        
        self.root.title("Clothes - Add Purchase")
        self.root.geometry("1100x600")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        
        self.create_form()

    def create_form(self):
        # Clear existing widgets to reset the view
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container (Centered)
        form_card = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        form_card.place(relx=0.5, rely=0.5, anchor="center", width=520, height=450)

        # Header Title
        tk.Label(form_card, text="STOCK ACQUISITION", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(pady=(35, 0))
        
        self.title_label = tk.Label(form_card, text="Register New Purchase", font=("Segoe UI", 20, "bold"), 
                                   bg=self.card_color, fg=self.primary_color)
        self.title_label.pack(pady=(0, 30))

        # 2. Form Fields Container
        fields_frame = tk.Frame(form_card, bg=self.card_color)
        fields_frame.pack(padx=60, fill="x")

        # Item Dropdown Selection
        tk.Label(fields_frame, text="Select Item", font=("Segoe UI", 10, "bold"), 
                 bg=self.card_color, fg="#424242").pack(anchor="w", pady=(0, 5))
        
        self.item_var = tk.StringVar()
        # Styled Combobox for better visibility than OptionMenu
        self.item_menu = ttk.Combobox(fields_frame, textvariable=self.item_var, font=("Segoe UI", 11), state="readonly")
        self.item_menu.pack(fill="x", ipady=5, pady=(0, 15))

        # Quantity Input
        tk.Label(fields_frame, text="Quantity Purchased", font=("Segoe UI", 10, "bold"), 
                 bg=self.card_color, fg="#424242").pack(anchor="w", pady=(0, 5))
        
        self.quantity_entry = tk.Entry(fields_frame, font=("Segoe UI", 12), bg="#f5f5f5", bd=0, 
                                       highlightthickness=1, highlightbackground="#e0e0e0",
                                       highlightcolor=self.primary_color)
        self.quantity_entry.pack(fill="x", ipady=8)

        self.load_items()

        # 3. ACTION BUTTONS (Modern High-Visibility Style)
        btn_container = tk.Frame(form_card, bg=self.card_color)
        btn_container.pack(fill="x", padx=60, pady=(35, 0))

        # --- SAVE PURCHASE BUTTON (Primary) ---
        tk.Button(
            btn_container, text="CONFIRM & SAVE PURCHASE", command=self.save_purchase,
            bg=self.primary_color, fg="white", font=("Segoe UI", 11, "bold"),
            bd=0, cursor="hand2", activebackground="#1b5e20", activeforeground="white"
        ).pack(fill="x", ipady=12)

        # --- VIEW AND BACK BUTTONS (Secondary Row) ---
        nav_frame = tk.Frame(btn_container, bg=self.card_color)
        nav_frame.pack(fill="x", pady=15)

        tk.Button(
            nav_frame, text="View All Purchases", command=self.view_purchases,
            bg=self.view_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
            bd=0, cursor="hand2", activebackground="#1565C0", width=18
        ).pack(side="left", ipady=8)

        tk.Button(
            nav_frame, text="Back to Dashboard", command=self.back_callback,
            bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
            bd=0, cursor="hand2", activebackground="#424242", width=18
        ).pack(side="right", ipady=8)

    def load_items(self):
        self.cursor.execute("SELECT item_id, item_name, sale_price FROM ClothItems")
        items = self.cursor.fetchall()
        item_names = [item[1] for item in items]
        self.item_dict = {item[1]: (item[0], item[2]) for item in items}
        
        self.item_menu['values'] = item_names
        if item_names:
            self.item_var.set(item_names[0])

    def save_purchase(self):
        item_name = self.item_var.get()
        quantity = self.quantity_entry.get().strip()

        if not all([item_name, quantity]):
            messagebox.showerror("Error", "Please select an item and enter quantity.")
            return

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError("Quantity must be greater than zero.")

            item_id, sale_price = self.item_dict.get(item_name)
            total_cost = quantity * sale_price
            purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Insert purchase record
            self.cursor.execute('''
                INSERT INTO Purchases (item_id, user_id, quantity_purchased, purchase_date, total_cost)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, self.current_user['user_id'], quantity, purchase_date, total_cost))

            # Update stock quantity automatically
            self.cursor.execute('''
                UPDATE ClothItems SET stock_quantity = stock_quantity + ?
                WHERE item_id = ?
            ''', (quantity, item_id))

            self.conn.commit()
            messagebox.showinfo("Success", f"Purchased {quantity} units of {item_name}. Stock updated.")
            self.clear_form()
            self.back_callback() # Return to dashboard
        except ValueError:
            messagebox.showerror("Error", "Invalid quantity. Please enter a whole number.")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save purchase: {e}")

    def clear_form(self):
        self.quantity_entry.delete(0, tk.END)
        self.load_items()

    def view_purchases(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from view_purchase import ViewPurchases
        ViewPurchases(self.root, self.current_user, self.back_callback)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()