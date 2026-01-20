import tkinter as tk
from tkinter import ttk, messagebox
from tkcalendar import DateEntry
import sqlite3
from datetime import datetime
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
import os
from PIL import Image, ImageTk

class GenerateReports:
    def __init__(self, root, current_user, back_callback):
        self.root = root
        self.current_user = current_user
        self.back_callback = back_callback
        
        # --- THEME COLORS ---
        self.bg_color = "#98FB98"       # Pale Green background
        self.card_color = "#ffffff"     # White Card
        self.primary_color = "#2e7d32"  # Dark Green
        self.accent_blue = "#1976D2"    # Export Blue
        self.back_btn_color = "#F44336"   # Red
        self.gen_btn_color = "#4CAF50"    # Success Green
        
        self.root.title("ThreadFlow | Business Intelligence Reports")
        self.root.geometry("1150x750")
        self.root.configure(bg=self.bg_color)
        
        self.conn = sqlite3.connect('clothes.db')
        self.cursor = self.conn.cursor()
        
        self.reports_folder = "reports"
        if not os.path.exists(self.reports_folder):
            os.makedirs(self.reports_folder)
            
        self.image_cache = {}  
        self.path_cache = {}   
        
        self.create_form()

    def create_form(self):
        for widget in self.root.winfo_children():
            widget.destroy()

        container = tk.Frame(self.root, bg=self.card_color, bd=0, 
                             highlightbackground="#d1d1d1", highlightthickness=1)
        container.place(relx=0.5, rely=0.5, anchor="center", relwidth=0.9, relheight=0.9)

        top_nav = tk.Frame(container, bg=self.card_color)
        top_nav.pack(fill="x", padx=40, pady=(25, 10))

        title_frame = tk.Frame(top_nav, bg=self.card_color)
        title_frame.pack(side="left")
        tk.Label(title_frame, text="ANALYTICS ENGINE", font=("Helvetica", 9, "bold"), 
                 bg=self.card_color, fg="#9e9e9e").pack(anchor="w")
        tk.Label(title_frame, text="Business Reports", font=("Segoe UI", 18, "bold"), 
                 bg=self.card_color, fg=self.primary_color).pack(anchor="w")

        btn_nav = tk.Frame(top_nav, bg=self.card_color)
        btn_nav.pack(side="right", pady=5)

        tk.Button(btn_nav, text="← DASHBOARD", command=self.back_callback,
                 bg=self.back_btn_color, fg="white", font=("Segoe UI", 9, "bold"),
                 bd=0, cursor="hand2", width=15).pack(side="right", padx=5, ipady=8)

        control_panel = tk.Frame(container, bg="#f8f9fa", padx=20, pady=15)
        control_panel.pack(fill="x", padx=40, pady=10)

        type_frame = tk.Frame(control_panel, bg="#f8f9fa")
        type_frame.pack(side="left")
        
        tk.Label(type_frame, text="Report Type:", font=("Segoe UI", 9, "bold"), bg="#f8f9fa").pack(side="left", padx=5)
        self.report_var = tk.StringVar(value="Stock")
        types = ["Stock", "Sales", "Purchases", "Profit"]
        for t in types:
            tk.Radiobutton(type_frame, text=t, variable=self.report_var, value=t,
                           font=("Segoe UI", 9), bg="#f8f9fa", indicatoron=0, 
                           width=10, selectcolor="#e8f5e9", cursor="hand2").pack(side="left", padx=2)

        date_frame = tk.Frame(control_panel, bg="#f8f9fa")
        date_frame.pack(side="left", padx=(30, 0))
        
        tk.Label(date_frame, text="From:", bg="#f8f9fa", font=("Segoe UI", 9)).pack(side="left", padx=2)
        self.start_date_entry = DateEntry(date_frame, width=12, background='darkblue', 
                                          foreground='white', borderwidth=2, date_pattern="yyyy-mm-dd")
        self.start_date_entry.pack(side="left", padx=5)

        tk.Label(date_frame, text="To:", bg="#f8f9fa", font=("Segoe UI", 9)).pack(side="left", padx=2)
        self.end_date_entry = DateEntry(date_frame, width=12, background='darkblue', 
                                        foreground='white', borderwidth=2, date_pattern="yyyy-mm-dd")
        self.end_date_entry.pack(side="left", padx=5)

        actions_frame = tk.Frame(control_panel, bg="#f8f9fa")
        actions_frame.pack(side="right")

        tk.Button(actions_frame, text="GENERATE", command=self.generate_report, 
                  bg=self.gen_btn_color, fg="white", font=("Segoe UI", 9, "bold"), width=12, bd=0).pack(side="left", padx=5, ipady=5)
        
        tk.Button(actions_frame, text="EXPORT PDF", command=self.download_pdf,
                  bg=self.accent_blue, fg="white", font=("Segoe UI", 9, "bold"), width=12, bd=0).pack(side="left", padx=5, ipady=5)

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview.Heading", font=("Segoe UI", 10, "bold"))
        style.configure("Treeview", font=("Segoe UI", 9), rowheight=45)
        
        table_frame = tk.Frame(container, bg=self.card_color)
        table_frame.pack(padx=40, pady=(10, 30), fill="both", expand=True)

        self.tree = ttk.Treeview(table_frame, show="headings")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.tag_configure('total', background='#e8f5e9', font=('Segoe UI', 10, 'bold'))

        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.report_data = []

    def generate_report(self):
        report_type = self.report_var.get()
        start = self.start_date_entry.get_date().strftime("%Y-%m-%d")
        end = self.end_date_entry.get_date().strftime("%Y-%m-%d")

        self.image_cache.clear()
        self.path_cache.clear()
        
        if report_type == "Stock":
            self.generate_stock_report()
        elif report_type == "Sales":
            self.generate_sales_report(start, end)
        elif report_type == "Purchases":
            self.generate_purchases_report(start, end)
        elif report_type == "Profit":
            self.generate_profit_report(start, end)

        self.display_report()

    def generate_stock_report(self):
        self.tree["columns"] = ("ID", "Item Name", "Category", "Quantity", "Price", "Image")
        for col in self.tree["columns"]: 
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.cursor.execute('''
            SELECT mi.item_id, mi.item_name, ic.category_name, mi.stock_quantity, mi.unit_price, mi.item_image
            FROM ClothItems mi JOIN Categories ic ON mi.category_id = ic.category_id
        ''')
        self.report_data = self.cursor.fetchall()

    def generate_sales_report(self, start, end):
        self.tree["columns"] = ("Sale ID", "Item Name", "Qty", "Total", "Date", "Image")
        for col in self.tree["columns"]: 
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.cursor.execute('''
            SELECT s.sale_id, mi.item_name, s.quantity_sold, s.total_amount, s.sale_date, mi.item_image
            FROM Sales s JOIN ClothItems mi ON s.item_id = mi.item_id
            WHERE s.sale_date BETWEEN ? AND ?
        ''', (start, f"{end} 23:59:59"))
        self.report_data = self.cursor.fetchall()

    def generate_purchases_report(self, start, end):
        self.tree["columns"] = ("ID", "Item Name", "Qty", "Cost", "Date", "Image")
        for col in self.tree["columns"]: 
            self.tree.heading(col, text=col)
            self.tree.column(col, width=130, anchor="center")
        self.cursor.execute('''
            SELECT p.purchase_id, mi.item_name, p.quantity_purchased, p.total_cost, p.purchase_date, mi.item_image
            FROM Purchases p JOIN ClothItems mi ON p.item_id = mi.item_id
            WHERE p.purchase_date BETWEEN ? AND ?
        ''', (start, f"{end} 23:59:59"))
        self.report_data = self.cursor.fetchall()

    def generate_profit_report(self, start, end):
        """Calculates profit: (Total Revenue) - (Unit Cost * Qty Sold)"""
        self.tree["columns"] = ("Item Name", "Revenue", "Cost Basis", "Gross Profit")
        for col in self.tree["columns"]: 
            self.tree.heading(col, text=col)
            self.tree.column(col, width=180, anchor="center")

        # SQL Formula: SUM(sale_price * qty) - SUM(unit_price * qty)
        self.cursor.execute('''
            SELECT 
                mi.item_name,
                SUM(s.total_amount) as revenue,
                SUM(s.quantity_sold * mi.unit_price) as cost_basis,
                SUM(s.total_amount - (s.quantity_sold * mi.unit_price)) as profit
            FROM Sales s
            JOIN ClothItems mi ON s.item_id = mi.item_id
            WHERE s.sale_date BETWEEN ? AND ?
            GROUP BY mi.item_id
        ''', (start, f"{end} 23:59:59"))
        
        raw_data = self.cursor.fetchall()
        self.report_data = []
        t_rev, t_cost, t_prof = 0, 0, 0

        for row in raw_data:
            name, rev, cost, prof = row
            self.report_data.append((name, f"RS {rev:,.2f}", f"RS {cost:,.2f}", f"RS {prof:,.2f}"))
            t_rev += rev; t_cost += cost; t_prof += prof

        if self.report_data:
            self.report_data.append(("GRAND TOTAL", f"RS {t_rev:,.2f}", f"RS {t_cost:,.2f}", f"RS {t_prof:,.2f}"))

    def display_report(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        rtype = self.report_var.get()

        for row in self.report_data:
            photo = None
            d_vals = list(row)

            if rtype != "Profit" and d_vals[0] != "GRAND TOTAL":
                item_id = row[0]
                img_path = row[-1]
                self.path_cache[item_id] = img_path
                if img_path and os.path.exists(str(img_path)):
                    try:
                        img = Image.open(img_path).resize((40,40))
                        photo = ImageTk.PhotoImage(img)
                        self.image_cache[item_id] = photo
                    except: photo = None
                d_vals = list(row[:-1]) + ["👁 View"]

            tags = ('total',) if d_vals[0] == "GRAND TOTAL" else ()
            
            if photo:
                self.tree.insert("", "end", values=d_vals, image=photo, tags=tags)
            else:
                self.tree.insert("", "end", values=d_vals, tags=tags)

        self.tree.bind("<ButtonRelease-1>", self.handle_tree_click) if rtype != "Profit" else self.tree.unbind("<ButtonRelease-1>")

    def handle_tree_click(self, event):
        item = self.tree.selection()
        if not item: return
        col = self.tree.identify_column(event.x)
        row_vals = self.tree.item(item)["values"]
        if col == f"#{len(self.tree['columns'])}" and row_vals[0] != "GRAND TOTAL":
            img_path = self.path_cache.get(row_vals[0])
            if img_path and os.path.exists(str(img_path)):
                win = tk.Toplevel(self.root)
                win.title("Preview")
                img = ImageTk.PhotoImage(Image.open(img_path).resize((300,300)))
                lbl = tk.Label(win, image=img); lbl.image = img; lbl.pack(padx=10, pady=10)

    def download_pdf(self):
        if not self.report_data: return messagebox.showerror("Error", "No data to export.")
        rtype = self.report_var.get()
        fname = f"{self.reports_folder}/{rtype.lower()}_report.pdf"
        doc = SimpleDocTemplate(fname, pagesize=letter)
        elements = [Paragraph(f"<b>{rtype} Report</b>", getSampleStyleSheet()['Heading1']), Spacer(1, 12)]
        
        pdf_table_data = [list(self.tree["columns"])] + [list(r) for r in self.report_data]
        if rtype != "Profit":
            for r in pdf_table_data[1:]: 
                if r[0] != "GRAND TOTAL": r[-1] = "Image Record"
        
        table = Table(pdf_table_data)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0,0), (-1,0), colors.darkgreen), 
            ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
            ('GRID', (0,0), (-1,-1), 0.5, colors.grey), 
            ('ALIGN', (0,0), (-1,-1), 'CENTER'),
            ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold')
        ]))
        elements.append(table)
        doc.build(elements)
        messagebox.showinfo("Success", f"Exported to: {fname}")

    def __del__(self):
        if hasattr(self, 'conn'): self.conn.close()