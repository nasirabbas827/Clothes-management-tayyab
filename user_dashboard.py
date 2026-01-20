import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3, os
from PIL import Image, ImageTk

class UserDashboard:
    def __init__(self, root, user, logout_callback):
        self.root = root
        self.user = user
        self.logout_callback = logout_callback

        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Pale Green background
        self.header_color = "#2e7d32"   # Dark Green header
        self.card_color = "#ffffff"     # White for content
        self.sale_btn_color = "#2196F3" # Bright Blue for Sale
        self.search_btn_color = "#4CAF50" # Green for Search
        
        self.root.title("Clothes Management - User Dashboard")
        self.root.geometry("1100x600")
        self.root.configure(bg=self.bg_color)

        # DB Connection
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()

        # Caches for image handling
        self.tk_images = {}  
        self.path_cache = {} 

        self.create_dashboard()

    def create_dashboard(self):
        # 1. Header Section
        header = tk.Frame(self.root, bg=self.header_color, height=70)
        header.pack(fill="x", side="top")
        
        welcome_txt = f"Welcome, {self.user['full_name']} (Sales Staff)"
        tk.Label(header, text=welcome_txt, font=("Segoe UI", 14, "bold"), 
                 bg=self.header_color, fg="white").pack(side="left", padx=30, pady=15)
        
        tk.Button(header, text="Logout", command=self.logout, font=("Segoe UI", 10, "bold"),
                  bg="#d32f2f", fg="white", bd=0, padx=20, cursor="hand2").pack(side="right", padx=30)

        # 2. Main Content Card
        main_card = tk.Frame(self.root, bg=self.card_color, bd=0, highlightthickness=1, highlightbackground="#d1d1d1")
        main_card.place(relx=0.5, rely=0.55, anchor="center", relwidth=0.92, relheight=0.8)

        # 3. TOP ACTION BAR (Search + Sale Button in one row)
        top_bar = tk.Frame(main_card, bg=self.card_color)
        top_bar.pack(fill="x", padx=20, pady=15)

        tk.Label(top_bar, text="Search Inventory:", font=("Segoe UI", 10, "bold"), 
                 bg=self.card_color, fg="#424242").pack(side="left", padx=(0, 5))
        
        self.search_entry = tk.Entry(top_bar, font=("Segoe UI", 11), bg="#f5f5f5", 
                                     bd=0, highlightthickness=1, highlightbackground="#e0e0e0")
        self.search_entry.pack(side="left", padx=5, ipady=5, fill="x", expand=True)
        self.search_entry.focus_set() # Ready to type immediately
        self.search_entry.bind("<Return>", lambda e: self.search_items())

        # Buttons Group
        tk.Button(top_bar, text="Search", command=self.search_items, bg=self.search_btn_color, fg="white",
                  font=("Segoe UI", 10, "bold"), bd=0, width=10, cursor="hand2").pack(side="left", padx=2)
        
        tk.Button(top_bar, text="Refresh", command=lambda: self.load_items(), bg="#757575", fg="white",
                  font=("Segoe UI", 10, "bold"), bd=0, width=10, cursor="hand2").pack(side="left", padx=2)

        # THE PROCEED TO SALE BUTTON (High Visibility)
        tk.Button(top_bar, text="PROCEED TO SALE", command=self.sale_selected_item,
                  bg=self.sale_btn_color, fg="white", font=("Segoe UI", 10, "bold"),
                  bd=0, width=20, cursor="hand2").pack(side="left", padx=(15, 0))

        # 4. Treeview (Table)
        table_frame = tk.Frame(main_card, bg=self.card_color)
        table_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#eeeeee")
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=45)

        # height=10 ensures the table stays compact
        self.tree = ttk.Treeview(table_frame, 
                                 columns=("ID", "Name", "Category", "Season", "Price", "Stock", "Preview"),
                                 show="headings", height=10)
        
        cols = {"ID": 50, "Name": 200, "Category": 120, "Season": 100, "Price": 110, "Stock": 80, "Preview": 80}
        for col, width in cols.items():
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=width)

        self.tree.pack(side="left", fill="both", expand=True)

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Initial data load
        self.load_items()
        
        # Bindings
        self.tree.bind("<ButtonRelease-1>", self.handle_tree_click)

    def load_items(self, search_term=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        self.tk_images.clear()
        self.path_cache.clear()

        query = '''
            SELECT mi.item_id, mi.item_name, ic.category_name, mi.season, mi.unit_price, 
                   mi.stock_quantity, mi.item_image
            FROM ClothItems mi
            JOIN Categories ic ON mi.category_id = ic.category_id
        '''
        if search_term:
            query += " WHERE mi.item_id LIKE ? OR mi.item_name LIKE ?"
            self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        else:
            self.cursor.execute(query)

        for row in self.cursor.fetchall():
            item_id, name, cat, season, price, stock, img_path = row
            price_rs = f"RS {price:,.2f}"
            self.path_cache[item_id] = img_path

            photo = None
            if img_path and os.path.exists(str(img_path)):
                try:
                    img = Image.open(img_path)
                    img = img.resize((40, 40), Image.Resampling.LANCZOS)
                    photo = ImageTk.PhotoImage(img)
                    self.tk_images[item_id] = photo
                except:
                    photo = None

            self.tree.insert("", "end", values=(item_id, name, cat, season, price_rs, stock, "👁 View"), 
                             image=photo if photo else "")

    def handle_tree_click(self, event):
        item = self.tree.selection()
        if not item: return
        
        col = self.tree.identify_column(event.x)
        item_data = self.tree.item(item)["values"]
        item_id = item_data[0]
        
        # Check if user clicked the "Preview" column (#7)
        if col == "#7":
            self.show_image(item_id)

    def show_image(self, item_id):
        image_path = self.path_cache.get(item_id)
        if image_path and os.path.exists(str(image_path)):
            img_window = tk.Toplevel(self.root)
            img_window.title("Product Preview")
            img = Image.open(image_path)
            img.thumbnail((400, 400))
            photo = ImageTk.PhotoImage(img)
            lbl = tk.Label(img_window, image=photo)
            lbl.image = photo
            lbl.pack(padx=20, pady=20)
        else:
            messagebox.showinfo("Info", "No image attached to this product.")

    def sale_selected_item(self):
        item = self.tree.selection()
        if not item:
            messagebox.showwarning("Selection Required", "Please select an item from the table first.")
            return
        
        values = self.tree.item(item)["values"]
        item_id = values[0]
        stock = values[5]
        
        if int(stock) <= 0:
            messagebox.showerror("Out of Stock", "This item has no stock available.")
            return

        for widget in self.root.winfo_children():
            widget.destroy()
        from add_sale import AddSale
        AddSale(self.root, self.user, self.show_dashboard, item_id)

    def search_items(self):
        self.load_items(self.search_entry.get())

    def show_dashboard(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        self.create_dashboard()

    def logout(self):
        if messagebox.askyesno("Logout", "Are you sure you want to exit to login?"):
            self.logout_callback()

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()