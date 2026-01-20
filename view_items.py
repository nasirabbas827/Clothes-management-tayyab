import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import os
from PIL import Image, ImageTk

class ViewItems:
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
        
        self.root.title("Clothes - Inventory Management")
        self.root.geometry("1150x700")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        
        # Caches for image handling
        self.image_cache = {}  
        self.path_cache = {}   
        
        self.create_view()

    def create_view(self):
        # Clear root
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container
        container = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.95, relheight=0.9)

        # --- TOP NAVIGATION ROW ---
        top_nav = tk.Frame(container, bg=self.card_color)
        top_nav.pack(fill="x", padx=30, pady=(20, 10))

        # Title Section
        title_frame = tk.Frame(top_nav, bg=self.card_color)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="PRODUCT INVENTORY", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(anchor="w")
        tk.Label(title_frame, text="Manage Clothing Items", font=("Segoe UI", 18, "bold"), 
                 bg=self.card_color, fg=self.primary_color).pack(anchor="w")

        # Action Buttons on Right (Always Visible)
        btn_nav = tk.Frame(top_nav, bg=self.card_color)
        btn_nav.pack(side="right", pady=5)

        tk.Button(btn_nav, text="+ ADD NEW ITEM", command=self.add_item,
                  bg=self.add_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=18).pack(side="left", padx=5, ipady=7)

        tk.Button(btn_nav, text="← DASHBOARD", command=self.back_callback,
                  bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=18).pack(side="left", padx=5, ipady=7)

        # --- 2. SEARCH & FILTER BAR ---
        search_frame = tk.Frame(container, bg="#f8f9fa", padx=15, pady=10)
        search_frame.pack(pady=10, fill="x", padx=30)

        tk.Label(search_frame, text="Quick Search:", font=("Segoe UI", 10, "bold"), 
                 bg="#f8f9fa", fg="#424242").pack(side="left", padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), bg="white", bd=0, 
                                     highlightthickness=1, highlightbackground="#e0e0e0")
        self.search_entry.pack(side="left", padx=5, ipady=5, expand=True, fill="x")

        tk.Button(search_frame, text="SEARCH", command=self.search_items,
                  bg=self.search_btn_color, fg="white", font=("Segoe UI", 8, "bold"), 
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=5, ipady=5)
        
        tk.Button(search_frame, text="CLEAR", command=self.clear_search,
                  bg=self.clear_btn_color, fg="white", font=("Segoe UI", 8, "bold"), 
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=5, ipady=5)

        # --- 3. INVENTORY TABLE ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=50)

        table_frame = tk.Frame(container, bg=self.card_color)
        table_frame.pack(padx=30, pady=(0, 20), fill="both", expand=True)

        cols = ("ID", "Name", "Category", "Unit Price", "Sale Price", "Stock", "Season", "Image", "Actions")
        self.tree = ttk.Treeview(table_frame, columns=cols, show="headings")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        for col in cols:
            self.tree.heading(col, text=col)
            self.tree.column(col, anchor="center", width=100)
        
        self.tree.column("ID", width=50)
        self.tree.column("Name", width=180, anchor="w")
        self.tree.column("Actions", width=110)
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.load_items()
        self.tree.bind("<ButtonRelease-1>", self.handle_tree_click)

    def load_items(self, search_term=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        self.image_cache.clear()
        self.path_cache.clear()

        query = '''
            SELECT mi.item_id, mi.item_name, ic.category_name, mi.unit_price, mi.sale_price, 
                   mi.stock_quantity, mi.season, mi.item_image
            FROM ClothItems mi
            JOIN Categories ic ON mi.category_id = ic.category_id
        '''
        if search_term:
            query += " WHERE mi.item_id LIKE ? OR mi.item_name LIKE ?"
            self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        else:
            self.cursor.execute(query)

        for row in self.cursor.fetchall():
            item_id, name, cat, u_price, s_price, stock, season, img_path = row
            self.path_cache[item_id] = img_path
            
            photo = None
            if img_path and os.path.exists(img_path):
                try:
                    img = Image.open(img_path)
                    img.thumbnail((45, 45)) 
                    photo = ImageTk.PhotoImage(img)
                    self.image_cache[item_id] = photo 
                except: photo = None

            self.tree.insert("", "end", 
                values=(item_id, name, cat, f"RS {u_price}", f"RS {s_price}", stock, season, "👁 View", "⚙ Options"),
                image=photo
            )

    def search_items(self):
        self.load_items(self.search_entry.get().strip())

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_items()

    def handle_tree_click(self, event):
        item = self.tree.selection()
        if not item: return
        column = self.tree.identify_column(event.x)
        item_id = self.tree.item(item)["values"][0]
        
        if column == "#9": self.show_action_menu(item_id)
        elif column == "#8": self.show_image(item_id)

    def show_image(self, item_id):
        image_path = self.path_cache.get(item_id)
        if image_path and os.path.exists(image_path):
            try:
                img_window = tk.Toplevel(self.root)
                img_window.title(f"Item Preview: {item_id}")
                img_window.configure(bg="white")
                img = Image.open(image_path)
                img.thumbnail((400, 400))
                photo = ImageTk.PhotoImage(img)
                lbl = tk.Label(img_window, image=photo, bg="white")
                lbl.image = photo 
                lbl.pack(padx=20, pady=20)
            except Exception as e: messagebox.showerror("Error", f"Image Load Error: {e}")
        else: messagebox.showinfo("Info", "No image found.")

    def show_action_menu(self, item_id):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label="Edit Item", command=lambda: self.edit_item(item_id))
        menu.add_separator()
        menu.add_command(label="Delete Item", command=lambda: self.delete_item(item_id), foreground="red")
        try:
            menu.tk_popup(self.root.winfo_pointerx(), self.root.winfo_pointery())
        finally:
            menu.grab_release()

    def edit_item(self, item_id):
        for widget in self.root.winfo_children(): widget.destroy()
        from add_items import AddItems
        add_page = AddItems(self.root, self.current_user, self.back_callback)
        add_page.load_item(item_id)

    def delete_item(self, item_id):
        if not messagebox.askyesno("Confirm Delete", "Permanently delete this item?"): return
        try:
            self.cursor.execute("SELECT COUNT(*) FROM Sales WHERE item_id = ?", (item_id,))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showerror("Conflict", "Cannot delete item linked to existing sales.")
                return
            self.cursor.execute("DELETE FROM ClothItems WHERE item_id = ?", (item_id,))
            self.conn.commit()
            self.load_items()
        except Exception as e: messagebox.showerror("Error", f"Delete failed: {e}")

    def add_item(self):
        for widget in self.root.winfo_children(): widget.destroy()
        from add_items import AddItems
        AddItems(self.root, self.current_user, self.back_callback)

    def __del__(self):
        if hasattr(self, 'conn'): self.conn.close()