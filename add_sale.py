import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
from datetime import datetime

class AddSale:
    def __init__(self, root, current_user, back_callback, item_id=None):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        self.item_id = item_id

        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Pale Green background
        self.card_color = "#ffffff"     # White Card
        self.primary_color = "#2e7d32"  # Dark Green
        self.accent_blue = "#1976D2"    # Stock Blue
        self.confirm_btn = "#2196F3"    # Blue
        self.back_btn_color = "#F44336" # Red
        self.success_green = "#4CAF50"  # Total Green

        self.root.title("Clothes - New Sale Transaction")
        self.root.geometry("1100x650")
        self.root.configure(bg=self.bg_color)

        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        self.item_dict = {}

        self.create_form()

    def create_form(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container
        container = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor="center", width=600, height=550)

        # --- TOP NAVIGATION ROW (Matching Purchases/Reports) ---
        top_nav = tk.Frame(container, bg=self.card_color)
        top_nav.pack(fill="x", padx=40, pady=(25, 10))

        title_frame = tk.Frame(top_nav, bg=self.card_color)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="TRANSACTION", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(anchor="w")
        tk.Label(title_frame, text="Add New Sale", font=("Segoe UI", 18, "bold"), 
                 bg=self.card_color, fg=self.primary_color).pack(anchor="w")

        tk.Button(top_nav, text="← DASHBOARD", command=self.back_callback,
                  bg=self.back_btn_color, fg="white", font=("Segoe UI", 8, "bold"),
                  bd=0, cursor="hand2", width=15).pack(side="right", pady=5, ipady=5)

        # --- FORM FIELDS ---
        form_inner = tk.Frame(container, bg=self.card_color)
        form_inner.pack(fill="both", expand=True, padx=50, pady=10)

        # Item Dropdown
        tk.Label(form_inner, text="Select Item", font=("Segoe UI", 10, "bold"), 
                 bg=self.card_color, fg="#424242").pack(anchor="w", pady=(10, 0))
        self.item_var = tk.StringVar()
        self.item_menu = ttk.Combobox(form_inner, textvariable=self.item_var, font=("Segoe UI", 11), state="readonly")
        self.item_menu.pack(fill="x", pady=5, ipady=5)

        # Stock Display
        stock_frame = tk.Frame(form_inner, bg="#f8f9fa", pady=8)
        stock_frame.pack(fill="x", pady=10)
        tk.Label(stock_frame, text="Available Stock:", font=("Segoe UI", 9), 
                 bg="#f8f9fa", fg="#616161").pack(side="left", padx=10)
        self.stock_label = tk.Label(stock_frame, text="0", font=("Segoe UI", 10, "bold"), 
                                    bg="#f8f9fa", fg=self.accent_blue)
        self.stock_label.pack(side="left")

        # Quantity Entry
        tk.Label(form_inner, text="Quantity to Sell", font=("Segoe UI", 10, "bold"), 
                 bg=self.card_color, fg="#424242").pack(anchor="w", pady=(10, 0))
        self.quantity_entry = tk.Entry(form_inner, font=("Segoe UI", 12), bd=0, 
                                       highlightthickness=1, highlightbackground="#e0e0e0")
        self.quantity_entry.pack(fill="x", pady=5, ipady=8)
        self.quantity_entry.bind("<KeyRelease>", lambda event: self.calculate_total())

        # Total Payable
        total_frame = tk.Frame(form_inner, bg=self.card_color)
        total_frame.pack(fill="x", pady=(20, 0))
        tk.Label(total_frame, text="TOTAL PAYABLE", font=("Segoe UI", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(side="left")
        self.total_amount_label = tk.Label(total_frame, text="RS 0.00", font=("Segoe UI", 18, "bold"), 
                                           bg=self.card_color, fg=self.success_green)
        self.total_amount_label.pack(side="right")

        # --- HORIZONTAL BUTTON ROW ---
        btn_frame = tk.Frame(container, bg=self.card_color)
        btn_frame.pack(fill="x", padx=50, pady=(20, 40))

        # Grid config for equal width buttons
        btn_frame.columnconfigure(0, weight=1)
        btn_frame.columnconfigure(1, weight=1)

        tk.Button(btn_frame, text="CONFIRM SALE", command=self.save_sale,
                  bg=self.confirm_btn, fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, cursor="hand2").grid(row=0, column=0, padx=(0, 5), sticky="ew", ipady=12)
        
        tk.Button(btn_frame, text="CANCEL", command=self.back_callback,
                  bg="#757575", fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, cursor="hand2").grid(row=0, column=1, padx=(5, 0), sticky="ew", ipady=12)

        self.load_items()
        self.item_menu.bind("<<ComboboxSelected>>", self.update_stock_label)

    def load_items(self):
        try:
            self.cursor.execute("SELECT item_id, item_name, sale_price, stock_quantity FROM ClothItems")
            items = self.cursor.fetchall()
            self.item_dict = {item[1]: (item[0], item[2], item[3]) for item in items}
            self.item_menu['values'] = list(self.item_dict.keys())

            if self.item_id:
                self.cursor.execute("SELECT item_name FROM ClothItems WHERE item_id = ?", (self.item_id,))
                res = self.cursor.fetchone()
                if res:
                    self.item_var.set(res[0])
                    self.update_stock_label()
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not load items: {e}")

    def update_stock_label(self, event=None):
        item_name = self.item_var.get()
        if item_name in self.item_dict:
            stock = self.item_dict[item_name][2]
            self.stock_label.config(text=f"{stock} Units Available")
            self.calculate_total()

    def calculate_total(self):
        item_name = self.item_var.get()
        qty_str = self.quantity_entry.get()
        
        if not qty_str or not item_name:
            self.total_amount_label.config(text="RS 0.00")
            return

        try:
            qty = int(qty_str)
            price = self.item_dict[item_name][1]
            total = qty * price
            self.total_amount_label.config(text=f"RS {total:,.2f}")
        except ValueError:
            self.total_amount_label.config(text="Invalid Qty")

    def save_sale(self):
        item_name = self.item_var.get()
        qty_str = self.quantity_entry.get()

        if not item_name or not qty_str:
            messagebox.showerror("Error", "Please select an item and enter quantity")
            return

        try:
            qty = int(qty_str)
            item_id, unit_price, current_stock = self.item_dict[item_name]

            if qty <= 0:
                messagebox.showerror("Error", "Quantity must be greater than 0")
                return
            if qty > current_stock:
                messagebox.showerror("Error", f"Insufficient Stock! Only {current_stock} left.")
                return

            total_amount = qty * unit_price
            sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            self.cursor.execute('''
                INSERT INTO Sales (item_id, user_id, quantity_sold, sale_date, total_amount)
                VALUES (?, ?, ?, ?, ?)
            ''', (item_id, self.current_user['user_id'], qty, sale_date, total_amount))

            self.cursor.execute('''
                UPDATE ClothItems SET stock_quantity = stock_quantity - ?
                WHERE item_id = ?
            ''', (qty, item_id))

            self.conn.commit()
            messagebox.showinfo("Success", f"Transaction Finalized!\nTotal: RS {total_amount:,.2f}")
            self.back_callback()

        except ValueError:
            messagebox.showerror("Error", "Quantity must be a whole number")
        except Exception as e:
            messagebox.showerror("Error", f"Transaction failed: {e}")

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()