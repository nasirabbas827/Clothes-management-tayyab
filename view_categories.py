import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

class ViewCategories:
    def __init__(self, root, current_user, back_callback):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Pale Green background
        self.card_color = "#ffffff"     # White Card
        self.primary_color = "#2e7d32"  # Dark Green
        self.search_btn_color = "#1976D2" # Blue
        self.clear_btn_color = "#757575"  # Gray
        self.back_btn_color = "#F44336"   # Red
        self.add_btn_color = "#4CAF50"    # Success Green
        self.delete_btn_color = "#FF9800" # Orange
        
        self.root.title("Clothes - Category Management")
        self.root.geometry("1100x650")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        self.create_view()

    def create_view(self):
        # Clear existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        # 1. Main Card Container
        container = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.85, relheight=0.85)

        # --- TOP NAVIGATION ROW (Title + Action Buttons) ---
        top_nav = tk.Frame(container, bg=self.card_color)
        top_nav.pack(fill="x", padx=40, pady=(25, 15))

        # Title Section
        title_frame = tk.Frame(top_nav, bg=self.card_color)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="CLASSIFICATION", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(anchor="w")
        tk.Label(title_frame, text="Product Categories", font=("Segoe UI", 18, "bold"), 
                 bg=self.card_color, fg=self.primary_color).pack(anchor="w")

        # Buttons on Right (Pinned for Visibility)
        btn_nav = tk.Frame(top_nav, bg=self.card_color)
        btn_nav.pack(side="right", pady=5)

        tk.Button(btn_nav, text="+ ADD CATEGORY", command=self.add_category,
                  bg=self.add_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=16).pack(side="left", padx=5, ipady=8)

        tk.Button(btn_nav, text="← DASHBOARD", command=self.back_callback,
                  bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2", width=16).pack(side="left", padx=5, ipady=8)

        # --- 2. SEARCH BAR ---
        search_frame = tk.Frame(container, bg="#f8f9fa", padx=15, pady=10)
        search_frame.pack(pady=10, fill="x", padx=40)

        tk.Label(search_frame, text="Find Category:", font=("Segoe UI", 10, "bold"), 
                 bg="#f8f9fa", fg="#424242").pack(side="left", padx=5)
        
        self.search_entry = tk.Entry(search_frame, font=("Segoe UI", 11), bg="white", bd=0, 
                                     highlightthickness=1, highlightbackground="#e0e0e0")
        self.search_entry.pack(side="left", padx=5, ipady=5, expand=True, fill="x")

        tk.Button(search_frame, text="SEARCH", command=self.search_categories,
                  bg=self.search_btn_color, fg="white", font=("Segoe UI", 8, "bold"), 
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=5, ipady=5)
        
        tk.Button(search_frame, text="CLEAR", command=self.clear_search,
                  bg=self.clear_btn_color, fg="white", font=("Segoe UI", 8, "bold"), 
                  width=10, bd=0, cursor="hand2").pack(side="left", padx=5, ipady=5)

        # --- 3. TABLE AREA ---
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"))
        style.configure("Treeview", font=("Segoe UI", 10), rowheight=35)

        table_frame = tk.Frame(container, bg=self.card_color)
        table_frame.pack(padx=40, pady=(10, 20), fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, columns=("ID", "Name"), show="headings")
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        
        self.tree.heading("ID", text="Category ID")
        self.tree.heading("Name", text="Category Name")

        self.tree.column("ID", width=150, anchor="center")
        self.tree.column("Name", width=400, anchor="w")
        
        self.tree.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # --- 4. DELETE BUTTON (Bottom) ---
        tk.Button(container, text="DELETE SELECTED CATEGORY", command=self.handle_delete,
                  bg=self.delete_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                  bd=0, cursor="hand2").pack(pady=(0, 25), ipady=10, fill="x", padx=40)

        self.load_categories()
        self.tree.bind("<Double-1>", self.edit_category)

    def load_categories(self, search_term=""):
        for item in self.tree.get_children():
            self.tree.delete(item)
        
        query = "SELECT category_id, category_name FROM Categories"
        if search_term:
            query += " WHERE category_id LIKE ? OR category_name LIKE ?"
            self.cursor.execute(query, (f"%{search_term}%", f"%{search_term}%"))
        else:
            self.cursor.execute(query)
            
        for category in self.cursor.fetchall():
            self.tree.insert("", "end", values=category)

    def search_categories(self):
        self.load_categories(self.search_entry.get().strip())

    def clear_search(self):
        self.search_entry.delete(0, tk.END)
        self.load_categories()

    def handle_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Required", "Please select a category to delete.")
            return
        
        category_data = self.tree.item(selected_item)["values"]
        category_id = category_data[0]
        category_name = category_data[1]

        confirm = messagebox.askyesno("Confirm Delete", f"Delete '{category_name}'? \nThis action cannot be undone.")
        if confirm:
            self.delete_category(category_id)

    def delete_category(self, category_id):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM ClothItems WHERE category_id = ?", (category_id,))
            if self.cursor.fetchone()[0] > 0:
                messagebox.showerror("Error", "Conflict: Category contains active items and cannot be deleted.")
                return

            self.cursor.execute("DELETE FROM Categories WHERE category_id = ?", (category_id,))
            self.conn.commit()
            messagebox.showinfo("Success", "Category removed.")
            self.load_categories()
        except Exception as e:
            messagebox.showerror("Error", f"Operation failed: {e}")

    def edit_category(self, event):
        item = self.tree.selection()
        if not item: return
        category_id = self.tree.item(item)["values"][0]
        for widget in self.root.winfo_children():
            widget.destroy()
        from add_categories import AddCategories
        page = AddCategories(self.root, self.current_user, self.back_callback)
        page.load_category(category_id)

    def add_category(self):
        for widget in self.root.winfo_children():
            widget.destroy()
        from add_categories import AddCategories
        AddCategories(self.root, self.current_user, self.back_callback)

    def __del__(self):
        if hasattr(self, 'conn'):
            self.conn.close()