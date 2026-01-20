import tkinter as tk
from tkinter import messagebox, filedialog
from tkinter import ttk
import sqlite3
import os
import shutil
from datetime import datetime

class AddItems:
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
        self.upload_btn_color = "#FF9800" # Orange for Upload
        
        self.root.title("Clothes Management - Add/Edit Item")
        self.root.geometry("1100x700")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect("clothes.db")
        self.cursor = self.conn.cursor()
        self.item_id = None
        self.image_path = None
        self.items_folder = "items"

        if not os.path.exists(self.items_folder):
            os.makedirs(self.items_folder)

        self.create_form()

    def create_form(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container (Larger for Item Details)
        form_card = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        form_card.place(relx=0.5, rely=0.5, anchor="center", width=700, height=620)

        # Header Title
        tk.Label(form_card, text="INVENTORY ITEM SETUP", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(pady=(20, 0))
        
        self.title_label = tk.Label(form_card, text="Add/Edit Product Item", font=("Segoe UI", 20, "bold"), 
                                   bg=self.card_color, fg=self.primary_color)
        self.title_label.pack(pady=(0, 20))

        # 2. Form Fields Grid Layout (Inside Card)
        fields_frame = tk.Frame(form_card, bg=self.card_color)
        fields_frame.pack(padx=40, fill="both", expand=True)

        def create_label(parent, text):
            return tk.Label(parent, text=text, font=("Segoe UI", 9, "bold"), bg=self.card_color, fg="#424242")

        # Column 1
        create_label(fields_frame, "Item Name").grid(row=0, column=0, sticky="w", pady=(10, 0))
        self.item_name_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), bg="#f5f5f5", bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        self.item_name_entry.grid(row=1, column=0, sticky="ew", padx=(0, 10), ipady=5)

        create_label(fields_frame, "Category").grid(row=2, column=0, sticky="w", pady=(10, 0))
        self.category_var = tk.StringVar()
        self.category_menu = ttk.Combobox(fields_frame, textvariable=self.category_var, font=("Segoe UI", 11), state="readonly")
        self.category_menu.grid(row=3, column=0, sticky="ew", padx=(0, 10), ipady=5)

        create_label(fields_frame, "Unit Cost Price").grid(row=4, column=0, sticky="w", pady=(10, 0))
        self.unit_price_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), bg="#f5f5f5", bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        self.unit_price_entry.grid(row=5, column=0, sticky="ew", padx=(0, 10), ipady=5)

        # Column 2
        create_label(fields_frame, "Season").grid(row=0, column=1, sticky="w", pady=(10, 0))
        self.season_var = tk.StringVar(value="Spring")
        self.season_menu = ttk.Combobox(fields_frame, textvariable=self.season_var, font=("Segoe UI", 11), state="readonly")
        self.season_menu['values'] = ('Spring', 'Summer', 'Autumn', 'Winter')
        self.season_menu.grid(row=1, column=1, sticky="ew", ipady=5)

        create_label(fields_frame, "Stock Quantity").grid(row=2, column=1, sticky="w", pady=(10, 0))
        self.stock_quantity_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), bg="#f5f5f5", bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        self.stock_quantity_entry.grid(row=3, column=1, sticky="ew", ipady=5)

        create_label(fields_frame, "Sale Price").grid(row=4, column=1, sticky="w", pady=(10, 0))
        self.sale_price_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), bg="#f5f5f5", bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        self.sale_price_entry.grid(row=5, column=1, sticky="ew", ipady=5)

        # Full Width Description
        create_label(fields_frame, "Item Description").grid(row=6, column=0, columnspan=2, sticky="w", pady=(10, 0))
        self.description_entry = tk.Entry(fields_frame, font=("Segoe UI", 11), bg="#f5f5f5", bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        self.description_entry.grid(row=7, column=0, columnspan=2, sticky="ew", ipady=5)

        # Image Upload Section
        img_frame = tk.Frame(fields_frame, bg=self.card_color)
        img_frame.grid(row=8, column=0, columnspan=2, pady=15, sticky="ew")
        
        tk.Button(img_frame, text="UPLOAD IMAGE", command=self.upload_image, bg=self.upload_btn_color, fg="white", font=("Segoe UI", 9, "bold"), bd=0, cursor="hand2").pack(side="left", padx=5, ipady=5)
        self.image_label = tk.Label(img_frame, text="No image selected", font=("Segoe UI", 9, "italic"), bg=self.card_color, fg="#757575")
        self.image_label.pack(side="left", padx=10)

        fields_frame.columnconfigure(0, weight=1)
        fields_frame.columnconfigure(1, weight=1)

        # 3. ACTION BUTTONS (Modern Tall Style)
        btn_container = tk.Frame(form_card, bg=self.card_color)
        btn_container.pack(fill="x", padx=40, pady=(10, 20))

        # --- SAVE BUTTON ---
        tk.Button(
            btn_container, text="SAVE ITEM TO INVENTORY", command=self.save_item,
            bg=self.primary_color, fg="white", font=("Segoe UI", 11, "bold"),
            bd=0, cursor="hand2", activebackground="#1b5e20"
        ).pack(fill="x", ipady=12)

        # --- VIEW AND BACK BUTTONS ---
        nav_frame = tk.Frame(btn_container, bg=self.card_color)
        nav_frame.pack(fill="x", pady=10)

        tk.Button(nav_frame, text="View All Items", command=self.view_items,
                  bg=self.view_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=22).pack(side="left", ipady=8)

        tk.Button(nav_frame, text="Back to Dashboard", command=self.back_callback,
                  bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=22).pack(side="right", ipady=8)

        self.load_categories()

    def load_categories(self):
        self.cursor.execute("SELECT category_id, category_name FROM Categories")
        categories = self.cursor.fetchall()
        category_names = [cat[1] for cat in categories]
        self.category_dict = {cat[1]: cat[0] for cat in categories}
        self.category_menu["values"] = category_names
        if category_names:
            self.category_var.set(category_names[0])

    def upload_image(self):
        file_path = filedialog.askopenfilename(filetypes=[("Image files", "*.png *.jpg *.jpeg")])
        if file_path:
            filename = f"item_{int(datetime.now().timestamp())}_{os.path.basename(file_path)}"
            dest_path = os.path.join(self.items_folder, filename)
            shutil.copy(file_path, dest_path)
            self.image_path = dest_path
            self.image_label.config(text=f"✓ {filename}")

    def load_item(self, item_id):
        self.item_id = item_id
        self.title_label.config(text="Edit Product Details")
        self.cursor.execute("""SELECT item_name, category_id, description, unit_price, sale_price, 
                               stock_quantity, season, item_image 
                               FROM ClothItems WHERE item_id = ?""", (item_id,))
        item = self.cursor.fetchone()
        if not item: return

        self.item_name_entry.insert(0, item[0])
        self.cursor.execute("SELECT category_name FROM Categories WHERE category_id = ?", (item[1],))
        cat_row = self.cursor.fetchone()
        if cat_row: self.category_var.set(cat_row[0])
        
        self.description_entry.insert(0, item[2] if item[2] else "")
        self.unit_price_entry.insert(0, str(item[3]))
        self.sale_price_entry.insert(0, str(item[4]))
        self.stock_quantity_entry.insert(0, str(item[5]))
        self.season_var.set(item[6])
        self.image_path = item[7]
        self.image_label.config(text=f"✓ {os.path.basename(self.image_path) if self.image_path else 'No image'}")

    def save_item(self):
        data = (self.item_name_entry.get(), self.category_var.get(), self.unit_price_entry.get(), 
                self.sale_price_entry.get(), self.stock_quantity_entry.get(), self.season_var.get())

        if not all(data):
            messagebox.showwarning("Incomplete", "Please fill all required fields.")
            return

        try:
            u_price = float(data[2])
            s_price = float(data[3])
            qty = int(data[4])
            category_id = self.category_dict.get(data[1])

            if self.item_id:
                self.cursor.execute("""UPDATE ClothItems SET item_name=?, category_id=?, description=?, 
                                     unit_price=?, sale_price=?, stock_quantity=?, season=?, item_image=?
                                     WHERE item_id=?""",
                                   (data[0], category_id, self.description_entry.get(), u_price, s_price, qty, data[5], self.image_path, self.item_id))
            else:
                self.cursor.execute("""INSERT INTO ClothItems 
                                     (item_name, category_id, description, unit_price, sale_price, stock_quantity, season, item_image)
                                     VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
                                   (data[0], category_id, self.description_entry.get(), u_price, s_price, qty, data[5], self.image_path))

            self.conn.commit()
            messagebox.showinfo("Success", "Inventory updated.")
            self.back_callback()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save: {e}")

    def view_items(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from view_items import ViewItems
        ViewItems(self.root, self.current_user, self.back_callback)

    def __del__(self):
        if hasattr(self, 'conn'): self.conn.close()