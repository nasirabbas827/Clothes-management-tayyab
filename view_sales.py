import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from PIL import Image, ImageTk

class ViewSales:
    def __init__(self, root, current_user, back_callback):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       
        self.card_color = "#ffffff"     
        self.primary_color = "#2e7d32" 
        self.search_btn_color = "#1976D2" 
        self.clear_btn_color = "#FF9800"  
        self.back_btn_color = "#F44336"   
        
        self.root.title("Clothes - View Sales History")
        self.root.geometry("1100x650")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        
        self.tk_images = {}  
        self.path_cache = {} 
        
        self.create_view()

    def create_view(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container
        container = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.85)

        # --- TOP NAVIGATION ROW (Title + Back Button) ---
        top_nav = tk.Frame(container, bg=self.card_color)
        top_nav.pack(fill="x", padx=40, pady=(20, 10))

        # Title on the left
        title_frame = tk.Frame(top_nav, bg=self.card_color)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="SALES HISTORY", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(anchor="w")
        tk.Label(title_frame, text="Transactions Log", font=("Segoe UI", 18, "bold"), 
                 bg=self.card_color, fg=self.primary_color).pack(anchor="w")

        # Back to Dashboard on the right (Always Visible)
        tk.Button(top_nav, text="← BACK TO DASHBOARD", command=self.back_callback,
                  bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=22).pack(side="right", ipady=8)

        # --- 2. SEARCH & CLEAR ROW ---
        search_frame = tk.Frame(container, bg="#f8f9fa", padx=15, pady=10)
        search_frame.pack(pady=10, fill="x", padx=40)

        tk.Label(search_frame, text="Search:", font=("Segoe UI", 10, "bold"), 
                 bg="#f8f9fa", fg="#424242").pack(side="left", padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), bg="white", bd=0, 
                                     highlightthickness=1, highlightbackground="#e0e0e0")
        self.search_entry.pack(side="left", padx=5, ipady=4, expand=True, fill="x")

        tk.Button(search_frame, text="SEARCH", command=self.search_sales,
                  bg=self.search_btn_color, fg="white", font=("Segoe UI", 8, "bold"), 
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=5, ipady=4)
        
        tk.Button(search_frame, text="CLEAR", command=self.clear_search,
                  bg=self.clear_btn_color, fg="white", font=("Segoe UI", 8, "bold"), 
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=5, ipady=4)

        # --- 3. TABLE AREA ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=40)

        table_frame = tk.Frame(container, bg=self.card_color)
        table_frame.pack(padx=40, pady=(0, 20), fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Item Name", "Qty", "Total", "Date", "Image"), 
                                 show="headings")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.heading("ID", text="Sale ID")
        self.tree.heading("Item Name", text="Item Name")
        self.tree.heading("Qty", text="Qty")
        self.tree.heading("Total", text="Total Amount")
        self.tree.heading("Date", text="Sale Date")
        self.tree.heading("Image", text="Image Preview")

        self.tree.column("ID", width=80, anchor="center")
        self.tree.column("Item Name", width=250, anchor="w")
        self.tree.column("Qty", width=80, anchor="center")
        self.tree.column("Total", width=120, anchor="center")
        self.tree.column("Date", width=180, anchor="center")
        self.tree.column("Image", width=100, anchor="center")
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_sales()
        self.tree.bind("<ButtonRelease-1>", self.handle_tree_click)

    def load_sales(self, search_term=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.tk_images.clear()
        self.path_cache.clear()

        query = '''
            SELECT s.sale_id, mi.item_name, s.quantity_sold, s.total_amount, s.sale_date, mi.item_image
            FROM Sales s
            JOIN ClothItems mi ON s.item_id = mi.item_id
        '''
        if search_term:
            query += " WHERE mi.item_name LIKE ? OR s.sale_id LIKE ?"
            self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        else:
            query += " ORDER BY s.sale_date DESC"
            self.cursor.execute(query)

        for sale in self.cursor.fetchall():
            sale_id, item_name, qty, total, sale_date, img_path = sale
            self.path_cache[sale_id] = img_path
            formatted_total = f"RS {total:,.2f}"

            photo = None
            if img_path and os.path.exists(str(img_path)):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((35, 35))
                    photo = ImageTk.PhotoImage(img)
                    self.tk_images[sale_id] = photo
                except: photo = None

            self.tree.insert("", "end", values=(sale_id, item_name, qty, formatted_total, sale_date, "👁 View"), image=photo)

    def search_sales(self):
        self.load_sales(self.search_entry.get().strip())

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_sales()

    def handle_tree_click(self, event):
        item = self.tree.selection()
        if not item: return
        col = self.tree.identify_column(event.x)
        sale_id = self.tree.item(item)["values"][0]
        if col == "#6": self.show_image(sale_id)

    def show_image(self, sale_id):
        image_path = self.path_cache.get(sale_id)
        if image_path and os.path.exists(str(image_path)):
            try:
                img_window = tk.Toplevel(self.root)
                img_window.title(f"Item Preview - ID: {sale_id}")
                img_window.configure(bg="white")
                img = Image.open(image_path)
                img.thumbnail((300, 300))
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(img_window, image=photo, bg="white")
                lbl.image = photo
                lbl.pack(padx=20, pady=20)
            except Exception as e: messagebox.showerror("Error", f"Failed: {e}")
        else: messagebox.showinfo("Info", "No image available")

    def __del__(self):
        if hasattr(self, 'conn'): self.conn.close()