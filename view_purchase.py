import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from PIL import Image, ImageTk

class ViewPurchases:
    def __init__(self, root, current_user, back_callback):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Pale Green background
        self.card_color = "#ffffff"     # White Card
        self.primary_color = "#2e7d32"  # Dark Green
        self.search_btn_color = "#1976D2" # Blue
        self.clear_btn_color = "#FF9800"  # Orange
        self.back_btn_color = "#F44336"   # Red
        self.add_btn_color = "#4CAF50"    # Success Green
        
        self.root.title("Clothes - Purchase Management")
        self.root.geometry("1150x700")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        
        # Caches for image handling
        self.image_cache = {}  
        self.path_cache = {}   
        
        self.create_view()

    def create_view(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container
        container = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

        # --- TOP NAVIGATION ROW (Fixed Visibility) ---
        top_nav = tk.Frame(container, bg=self.card_color)
        top_nav.pack(fill="x", padx=40, pady=(25, 15))

        # Title Section
        title_frame = tk.Frame(top_nav, bg=self.card_color)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="STOCK INFLOW", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(anchor="w")
        tk.Label(title_frame, text="Purchase History", font=("Segoe UI", 18, "bold"), 
                 bg=self.card_color, fg=self.primary_color).pack(anchor="w")

        # Action Buttons on Right
        btn_nav = tk.Frame(top_nav, bg=self.card_color)
        btn_nav.pack(side="right", pady=5)

        tk.Button(btn_nav, text="+ ADD PURCHASE", command=self.add_purchase,
                  bg=self.add_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=18).pack(side="left", padx=5, ipady=8)

        tk.Button(btn_nav, text="← DASHBOARD", command=self.back_callback,
                  bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=18).pack(side="left", padx=5, ipady=8)

        # --- 2. SEARCH BAR ---
        search_frame = tk.Frame(container, bg="#f8f9fa", padx=15, pady=10)
        search_frame.pack(pady=10, fill="x", padx=40)

        tk.Label(search_frame, text="Filter Purchases:", font=("Segoe UI", 10, "bold"), 
                 bg="#f8f9fa", fg="#424242").pack(side="left", padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), bg="white", bd=0, 
                                     highlightthickness=1, highlightbackground="#e0e0e0")
        self.search_entry.pack(side="left", padx=5, ipady=5, expand=True, fill="x")

        tk.Button(search_frame, text="SEARCH", command=self.search_purchases,
                  bg=self.search_btn_color, fg="white", font=("Segoe UI", 8, "bold"), 
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=5, ipady=5)
        
        tk.Button(search_frame, text="CLEAR", command=self.clear_search,
                  bg=self.clear_btn_color, fg="white", font=("Segoe UI", 8, "bold"), 
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=5, ipady=5)

        # --- 3. PURCHASE TABLE ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=45)

        table_frame = tk.Frame(container, bg=self.card_color)
        table_frame.pack(padx=40, pady=(0, 20), fill="both", expand=True)

        cols = ("ID", "Item Name", "Quantity", "Total Cost", "Date", "Image", "Actions")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=120)

        self.tree.column("Item Name", width=200, anchor="w")
        self.tree.column("ID", width=70)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_purchases()
        self.tree.bind("<ButtonRelease-1>", self.handle_tree_click)

    def load_purchases(self, search_term=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.image_cache.clear()
        self.path_cache.clear()

        query = '''
            SELECT p.purchase_id, mi.item_name, p.quantity_purchased, p.total_cost, p.purchase_date, mi.item_image
            FROM Purchases p
            JOIN ClothItems mi ON p.item_id = mi.item_id
        '''
        if search_term:
            query += " WHERE p.purchase_id LIKE ? OR mi.item_name LIKE ?"
            self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        else:
            self.cursor.execute(query + " ORDER BY p.purchase_date DESC")

        for purchase in self.cursor.fetchall():
            p_id, item_name, qty, cost, p_date, img_path = purchase
            self.path_cache[p_id] = img_path
            
            photo = None
            if img_path and os.path.exists(str(img_path)):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((35, 35))
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[p_id] = photo
                except: photo = None

            self.tree.insert("", "end", 
                             values=(p_id, item_name, qty, f"RS {cost:,.2f}", p_date, "👁 View", "🗑 Delete"),
                             image=photo)

    def search_purchases(self):
        self.load_purchases(self.search_entry.get().strip())

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_purchases()

    def handle_tree_click(self, event):
        item = self.tree.selection()
        if not item: return
        col = self.tree.identify_column(event.x)
        p_id = self.tree.item(item)["values"][0]
        
        if col == "#7": self.delete_purchase(p_id)
        elif col == "#6": self.show_image(p_id)

    def show_image(self, purchase_id):
        image_path = self.path_cache.get(purchase_id)
        if image_path and os.path.exists(str(image_path)):
            try:
                img_window = tk.Toplevel(self.root)
                img_window.title(f"Purchase ID: {purchase_id}")
                img_window.configure(bg="white")
                img = Image.open(image_path)
                img.thumbnail((350, 350))
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(img_window, image=photo, bg="white")
                lbl.image = photo 
                lbl.pack(padx=20, pady=20)
            except Exception as e: messagebox.showerror("Error", f"Failed: {e}")
        else: messagebox.showinfo("Info", "No image found for this record.")

    def delete_purchase(self, purchase_id):
        if not messagebox.askyesno("Confirm", "Delete this record? This will reduce stock quantity."):
            return
        try:
            self.cursor.execute("SELECT item_id, quantity_purchased FROM Purchases WHERE purchase_id = ?", (purchase_id,))
            res = self.cursor.fetchone()
            if res:
                item_id, qty = res
                self.cursor.execute("UPDATE ClothItems SET stock_quantity = stock_quantity - ? WHERE item_id = ?", (qty, item_id))
                self.cursor.execute("DELETE FROM Purchases WHERE purchase_id = ?", (purchase_id,))
                self.conn.commit()
                messagebox.showinfo("Success", "Record deleted.")
                self.load_purchases()
        except Exception as e: messagebox.showerror("Error", f"Failed: {e}")

    def add_purchase(self):
        for widget in self.root.winfo_children(): widget.destroy()
        from add_purchase import AddPurchase
        AddPurchase(self.root, self.current_user, self.back_callback)

    def __del__(self):
        if hasattr(self, 'conn'): self.conn.close()