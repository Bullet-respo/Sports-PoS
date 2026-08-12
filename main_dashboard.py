import sqlite3
import customtkinter as ctk
from tkinter import ttk, messagebox

import subprocess
import hashlib

import os
from reportlab.lib.pagesizes import A5
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

# Matplotlib integration for drawing your visual weekly report chart
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

def get_hardware_id():
    """Fetches the unique motherboard UUID of the current machine."""
    try:
        # Queries Windows Management Instrumentation for the unique machine UUID
        cmd = "wmic csproduct get UUID"
        uuid = subprocess.check_output(cmd, shell=True).decode().split('\n')[1].strip()
        
        # Hash it with SHA-256 for a clean, short HWID string
        hwid_hash = hashlib.sha256(uuid.encode()).hexdigest().upper()
        return f"{hwid_hash[:4]}-{hwid_hash[4:8]}-{hwid_hash[8:12]}"
    except Exception:
        # Fallback HWID if WMIC is restricted
        return "GENERIC-CLIENT-HWID-001"
        
def generate_product_key(hwid, secret_salt="SportsShop"):
    """Generates a valid product key tied specifically to a target HWID."""
    raw_str = f"{hwid}:{secret_salt}"
    key_hash = hashlib.sha256(raw_str.encode()).hexdigest().upper()
    return f"SS-{key_hash[:4]}-{key_hash[4:8]}-{key_hash[8:12]}"

class DurraniSportsApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        if not self.check_license_activation():
            self.after(100, self.prompt_activation_window)

        self.title("Durrani Sports Nowshera - Enterprise POS")
        self.geometry("1280x720")
        # self.resizable(False, False)

        # State variable for the earnings privacy eye feature
        self.earnings_hidden = True

        # --- MAIN LAYOUT SPLITTER ---
        # Persistent Sidebar Frame (Left)
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0, fg_color="#1a1c23")
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False)

        # Dynamic Content Window Frame (Right)
        self.container_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="#101116")
        self.container_frame.pack(side="right", fill="both", expand=True)
        # self.admin_security_pin = "1234"
        dev_password = "Admin"  # <-- Hardcoded developer console password for restricted access

        # Dictionary to hold independent structural page view objects
        self.pages = {}

        # Initialize the interface elements
        self.setup_sidebar()
        self.setup_pages()

        # Default to showing the primary overview dashboard on launch
        self.show_page("dashboard")
        self.refresh_dashboard_metrics()
        self.protocol("WM_DELETE_WINDOW", self.safely_terminate_application)

    # ==========================================
    # PERSISTENT LEFT SIDEBAR NAVIGATION MENU
    # ==========================================
    def setup_sidebar(self):
        # 1. Square Logo Display Placeholder Space (1:1 Ratio)
        self.logo_space = ctk.CTkLabel(self.sidebar_frame, text="DURRANI\nSPORTS", font=ctk.CTkFont(size=30, weight="bold"),
                                       width=200, height=120, fg_color="#111217", corner_radius=8)
        self.logo_space.pack(pady=25, padx=20)

        # 2. Navigational Buttons Stack
        nav_items = [
            ("🏠  Main Dashboard", "dashboard"),
            ("📦  Inventory Management", "inventory"),
            ("🖨️ Cashier Billing Pad", "billing"),
            ("📊  Sales History Log", "sales"),
            ("↩  Returns Archive Log", "returns"),
            ("🔒  Hidden Admin Panel", "admin")
            ]

        for text, page_id in nav_items:
            # Color configuration overrides for specific restricted administrative panels
            btn_color = "#2c3e50" if page_id == "admin" else "transparent"
            hover_c = "#34495e" if page_id == "admin" else "#1f538d"
            
            btn = ctk.CTkButton(self.sidebar_frame, text=text, anchor="w", height=40,
                                font=ctk.CTkFont(size=13, weight="bold"),
                                fg_color=btn_color, hover_color=hover_c,
                                command=lambda p=page_id: self.show_page(p))
            btn.pack(fill="x", padx=15, pady=6)
            btn._text_label.configure(padx=10)

        self.btn_dev_console = ctk.CTkButton(self.sidebar_frame, text="🛠️ Developer Console", anchor="w", height=40,
                                             font=ctk.CTkFont(size=13, weight="bold"),
                                             fg_color="#7f8c8d", hover_color="#95a5a6", # Balanced silver-gray tone
                                             command=lambda: self.show_page("developer"))
        # Using side="bottom" locks it to the very baseline beneath all items
        self.btn_dev_console.pack(side="bottom", fill="x", padx=15, pady=(0, 25))
        self.btn_dev_console._text_label.configure(padx=10)

    # ==========================================
    # DYNAMIC SCREEN VIEWS MANAGER PANEL ROUTINES
    # ==========================================
    def setup_pages(self):
        """Pre-loads all operational frames inside the right-hand layout memory container."""
        page_ids = ["dashboard", "inventory", "billing", "sales", "returns", "admin", "developer"]
        
        for p_id in page_ids:
            frame = ctk.CTkFrame(self.container_frame, fg_color="transparent")
            self.pages[p_id] = frame
            
            # Route individual builders to paint specific workspaces inside their allocated frames
            if p_id == "dashboard":
                self.build_dashboard_view(frame)
            elif p_id == "inventory":
                self.build_inventory_view(frame)
            elif p_id == "billing":
                self.build_billing_view(frame)
            elif p_id == "sales":
                self.build_sales_view(frame)
            elif p_id == "returns":
                self.build_returns_view(frame)
            elif p_id == "admin":
                self.build_admin_view(frame)
            elif p_id == "developer":
                self.build_developer_view(frame)
            else:
                # Pre-build label placeholders for sub-workspaces
                ctk.CTkLabel(frame, text=f"🚧 {p_id.upper()} WORKSPACE UNDER CONSTRUCTION", 
                             font=("Arial", 18, "bold")).pack(pady=100)

    def show_page(self, page_id):
        """Brings the chosen panel frame to the front layer smoothly."""
        if page_id == "admin":
            # Security PIN Gate check before loading cost elements
            if not self.verify_admin_access():
                return

        elif page_id == "developer":
            dev_pass = ctk.CTkInputDialog(text="Enter Developer Security Password:", title="Restricted Console").get_input()
            if dev_pass != "Admin":
                messagebox.showerror("Access Denied", "Incorrect Developer Password!")
                return

        # Hide all loaded page nodes frames safely
        for frame in self.pages.values():
            frame.pack_forget()
            
        # Unpack and map the designated view structure frame directly onto the layout canvas
        self.pages[page_id].pack(fill="both", expand=True, padx=25, pady=25)

    def verify_admin_access(self):
        """Fetches the current active master PIN from the database to verify access."""
        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT config_value FROM system_config WHERE config_key = 'admin_pin'")
        current_db_pin = cursor.fetchone()[0]
        conn.close()

        pin = ctk.CTkInputDialog(text="Enter Administrative Protection Key PIN:", title="Access Locked").get_input()
        if pin == current_db_pin:
            return True
        else:
            messagebox.showerror("Access Denied", "Incorrect Security PIN entered!")
            return False
        
    def admin_change_pin_dialog(self):
        """Saves new security PIN structures to the database and logs the audit event trail."""
        from datetime import datetime
        
        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT config_value FROM system_config WHERE config_key = 'admin_pin'")
        current_db_pin = cursor.fetchone()[0]

        current_verify = ctk.CTkInputDialog(text="Confirm your CURRENT Security PIN first:", title="PIN Security Check").get_input()
        if current_verify != current_db_pin:
            messagebox.showerror("Security Failure", "Current active PIN identification mismatch!")
            conn.close()
            return

        new_pin = ctk.CTkInputDialog(text="Type your NEW Administrative PIN Code:", title="Update Vault Key").get_input()
        if not new_pin or new_pin.strip() == "":
            messagebox.showwarning("Invalid Entry", "PIN structure cannot be left blank.")
            conn.close()
            return
            
        confirm_new = ctk.CTkInputDialog(text="Re-type your NEW PIN Code to confirm:", title="Confirm Vault Key").get_input()
        if new_pin.strip() == confirm_new.strip():
            target_pin = new_pin.strip()
            
            # Update permanent configuration row
            cursor.execute("UPDATE system_config SET config_value = ? WHERE config_key = 'admin_pin'", (target_pin,))
            
            # Log audit trail event with masked strings for security compliance
            today_str = datetime.now().strftime("%d-%m-%Y %H:%M:%S")
            masked_old = f"**{current_db_pin[-2:]}" if len(current_db_pin) >= 2 else "***"
            masked_new = f"**{target_pin[-2:]}" if len(target_pin) >= 2 else "***"
            
            cursor.execute("INSERT INTO pin_change_logs (change_date, old_pin_masked, new_pin_masked) VALUES (?, ?, ?)",
                           (today_str, masked_old, masked_new))
            
            conn.commit()
            messagebox.showinfo("PIN Updated", "Security authorization code successfully saved in persistent database storage!")
        else:
            messagebox.showerror("Error", "Confirmation PIN does not match! Change canceled.")
            
        conn.close()
    # ==========================================
    # CORE INTERFACE: MAIN OVERVIEW DASHBOARD PANEL
    # ==========================================
    def build_dashboard_view(self, parent_frame):
        # 1. Shop Header Brand Identity String Banner placement
        self.header_lbl = ctk.CTkLabel(parent_frame, text="Durrani Sports Nowshera", font=ctk.CTkFont(size=28, weight="bold"))
        self.header_lbl.pack(side="top", fill="x", pady=(10, 20))

        # 2. KPI Summary Cards Horizontal Container Bar Layout frame row
        self.kpi_row = ctk.CTkFrame(parent_frame, fg_color="transparent")
        self.kpi_row.pack(fill="x", pady=5)

        # --- CARD A: TODAY'S SALES QUANTITY ---
        self.card_sales = ctk.CTkFrame(self.kpi_row, width=280, height=130, fg_color="#1a1c23", corner_radius=12)
        self.card_sales.pack(side="left", padx=(0, 20))
        self.card_sales.pack_propagate(False)

        ctk.CTkLabel(self.card_sales, text="Today's Sales Count", font=("Arial", 13), text_color="#a0a5b5").pack(anchor="w", padx=20, pady=(15, 2))
        # Hardcoded dynamic baseline metrics trackers placeholders
        self.lbl_sales_metric = ctk.CTkLabel(self.card_sales, text="3", font=("Arial", 42, "bold"))
        self.lbl_sales_metric.pack(anchor="w", padx=20)

        # --- CARD B: DETAILED EARNINGS & EXPENSE BALANCER ---
        self.card_earnings = ctk.CTkFrame(self.kpi_row, width=440, height=130, fg_color="#1a1c23", corner_radius=12)
        self.card_earnings.pack(side="left", padx=20)
        self.card_earnings.pack_propagate(False)

        self.earning_title_frame = ctk.CTkFrame(self.card_earnings, fg_color="transparent")
        self.earning_title_frame.pack(fill="x", padx=15, pady=(10, 2))

        ctk.CTkLabel(self.earning_title_frame, text="Daily Cash Balancer Log Desk", font=("Arial", 12, "bold"), text_color="#a0a5b5").pack(side="left")
        
        self.btn_privacy = ctk.CTkButton(self.earning_title_frame, text="👁", width=25, height=20, fg_color="transparent", hover_color="#2b2d3a", command=self.toggle_earnings_visibility)
        self.btn_privacy.pack(side="right")

        # Inner Sub-metrics Content Grid Block Frame layout
        self.metrics_grid = ctk.CTkFrame(self.card_earnings, fg_color="transparent")
        self.metrics_grid.pack(fill="both", expand=True, padx=15, pady=2)

        # 1. Gross Revenue Row
        ctk.CTkLabel(self.metrics_grid, text="Total Cash Collected (Gross):", font=("Arial", 11), text_color="#a0a5b5").grid(row=0, column=0, sticky="w", pady=1)
        self.lbl_gross_metric = ctk.CTkLabel(self.metrics_grid, text="••••• PKR", font=("Arial", 11, "bold"), text_color="white")
        self.lbl_gross_metric.grid(row=0, column=1, sticky="e", padx=10)

        # 2. Payout Expenses Row + Quick Action Addition Button
        self.exp_lbl_frame = ctk.CTkFrame(self.metrics_grid, fg_color="transparent")
        self.exp_lbl_frame.grid(row=1, column=0, sticky="w", pady=1)
        ctk.CTkLabel(self.exp_lbl_frame, text="Today's Shop Expenses:", font=("Arial", 11), text_color="#a0a5b5").pack(side="left")
        
        self.btn_add_expense = ctk.CTkButton(self.exp_lbl_frame, text="➕ Log Expense", width=75, height=16, font=("Arial", 9), fg_color="#e67e22", hover_color="#d35400", command=self.dashboard_log_expense_dialog)
        self.btn_add_expense.pack(side="left", padx=8)

        self.lbl_expense_metric = ctk.CTkLabel(self.metrics_grid, text="0 PKR", font=("Arial", 11, "bold"), text_color="#e74c3c")
        self.lbl_expense_metric.grid(row=1, column=1, sticky="e", padx=10)

        # 3. True Net Profits Row (Revenue minus buying price cost minus active expenses)
        ctk.CTkLabel(self.metrics_grid, text="Net Shop Profit Margin:", font=("Arial", 12, "bold"), text_color="#2ecc71").grid(row=2, column=0, sticky="w", pady=(4, 0))
        self.lbl_earnings_metric = ctk.CTkLabel(self.metrics_grid, text="••••• PKR", font=("Arial", 14, "bold"), text_color="#2ecc71")
        self.lbl_earnings_metric.grid(row=2, column=1, sticky="e", padx=10, pady=(4, 0))

        # --- NEW CARD C: DYNAMIC LOW STOCK WARNING DESK ---
        self.card_stock_warning = ctk.CTkFrame(self.kpi_row, width=280, height=130, fg_color="#1a1c23", corner_radius=12)
        self.card_stock_warning.pack(side="left", padx=(20, 0))
        self.card_stock_warning.pack_propagate(False)

        ctk.CTkLabel(self.card_stock_warning, text="Low Stock Items Warning", font=("Arial", 13), text_color="#e74c3c").pack(anchor="w", padx=20, pady=(15, 2))
        self.lbl_stock_warning_metric = ctk.CTkLabel(self.card_stock_warning, text="0", font=("Arial", 42, "bold"), text_color="#e74c3c")
        self.lbl_stock_warning_metric.pack(anchor="w", padx=20)
        
        # 3. Analytics Chart Section Container Placement Row Block
        ctk.CTkLabel(parent_frame, text="Weekly Sales Report", font=ctk.CTkFont(size=16, weight="bold")).pack(anchor="w", pady=(35, 10))
        
        self.chart_frame = ctk.CTkFrame(parent_frame, fg_color="#1a1c23", corner_radius=12)
        self.chart_frame.pack(fill="both", expand=True, pady=(0, 10))

        self.render_weekly_matplotlib_chart()

    def toggle_earnings_visibility(self):
        """Calculates real-time cash ledger metrics and shifts masked visibility variables for ALL rows."""
        if self.earnings_hidden:
            from datetime import datetime
            today_date = datetime.now().strftime("%d-%m-%Y")

            conn = sqlite3.connect("durrani_sports.db")
            cursor = conn.cursor()
            
            try:
                # 1. Total Cash Collected Gross Revenue today
                cursor.execute("SELECT TOTAL(amount_collected) FROM sales WHERE date_time LIKE ?", (f"{today_date}%",))
                today_sales_revenue = int(cursor.fetchone()[0])

                # 2. Extract item buying costs to compute product margin
                cursor.execute("""
                    SELECT TOTAL(sales_items.quantity * products.cost_price)
                    FROM sales_items 
                    JOIN products ON sales_items.product_id = products.id
                    JOIN sales ON sales_items.invoice_id = sales.invoice_id
                    WHERE sales.date_time LIKE ?
                """, (f"{today_date}%",))
                today_sales_cost = int(cursor.fetchone()[0])

                # 3. Sum up daily expenses logged inside your expenses data bank
                cursor.execute("SELECT TOTAL(amount) FROM daily_expenses WHERE date = ?", (today_date,))
                today_expenses_total = int(cursor.fetchone()[0])

                # 4. Subtract direct refund payouts
                cursor.execute("SELECT TOTAL(refund_amount) FROM returns WHERE date_time LIKE ?", (f"{today_date}%",))
                today_refunds = int(cursor.fetchone()[0])

                # Core Calculations
                gross_collected = today_sales_revenue
                net_profit_margin = int((today_sales_revenue - today_sales_cost) - today_expenses_total - today_refunds)
                                
                # REVEAL REAL NUMBERS
                self.lbl_gross_metric.configure(text=f"{gross_collected:,} PKR")
                self.lbl_expense_metric.configure(text=f"{today_expenses_total:,} PKR")
                self.lbl_earnings_metric.configure(text=f"{net_profit_margin:,} PKR") # <-- FIXED NOW
                
            except Exception as e:
                print(f"Error in detailed dashboard balancing: {e}")
            finally:
                conn.close()

            self.btn_privacy.configure(text="🔒")
            self.earnings_hidden = False
        else:
            # HIDE ALL NUMBERS BEHIND MASKS CLEANLY
            self.lbl_gross_metric.configure(text="***** PKR")
            self.lbl_expense_metric.configure(text="***** PKR") # <-- FIXED NOW
            self.lbl_earnings_metric.configure(text="***** PKR")
            self.btn_privacy.configure(text="👁")
            self.earnings_hidden = True

    def dashboard_log_expense_dialog(self):
        """Spawns an administrative input wizard routine to log immediate operational costs."""
        from datetime import datetime
        
        exp_amount_input = ctk.CTkInputDialog(text="Enter Expense Amount Paid Out (PKR):", title="Log Expense Payout").get_input()
        if not exp_amount_input or exp_amount_input.strip() == "": return
        
        try:
            amt = int(exp_amount_input.strip())
            if amt <= 0: raise ValueError
            
            exp_desc_input = ctk.CTkInputDialog(text="Enter Expense Note / Description:\n(e.g., Water bill, Lunch, Repair cost)", title="Expense Description").get_input()
            desc = exp_desc_input.strip() if exp_desc_input and exp_desc_input.strip() != "" else "General Expense"
            
            today_date = datetime.now().strftime("%d-%m-%Y")
            
            # Save expense to database ledger
            conn = sqlite3.connect("durrani_sports.db")
            cursor = conn.cursor()
            cursor.execute("INSERT INTO daily_expenses (date, description, amount) VALUES (?, ?, ?)", (today_date, desc, amt))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Expense Logged", f"Logged Payout: {amt} PKR for '{desc}' successfully recorded.")
            
            # Hot-refresh dashboard metrics immediately
            self.refresh_dashboard_metrics()
            
        except ValueError:
            messagebox.showerror("Error", "Please input an integer number for pricing expenses values.")

    def render_weekly_matplotlib_chart(self):
        """Queries the database to calculate total physical items sold over the last 7 days and renders the trend."""
        # 1. Wipe out any existing old chart widgets inside the frame to prevent layout layering bugs
        for widget in self.chart_frame.winfo_children():
            widget.destroy()

        import datetime
        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()

        dates_list = []
        items_sold_count = []

        try:
            # Generate past 7 days dates relative to today
            now = datetime.datetime.now()
            for i in range(6, -1, -1):
                day = now - datetime.timedelta(days=i)
                date_str_db = day.strftime("%d-%m-%Y") # Matches your database format
                display_label = day.strftime("%d-%b")  # e.g., "03-Jul"
                
                # Query total sum of quantities sold on this specific day
                cursor.execute("""
                    SELECT TOTAL(sales_items.quantity) 
                    FROM sales_items
                    JOIN sales ON sales_items.invoice_id = sales.invoice_id
                    WHERE sales.date_time LIKE ?
                """, (f"{date_str_db}%",))
                
                total_items = int(cursor.fetchone()[0])
                
                dates_list.append(display_label)
                items_sold_count.append(total_items)
                
        except Exception as e:
            print(f"Chart data aggregation error: {e}")
            dates_list = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
            items_sold_count = [0, 0, 0, 0, 0, 0, 0]
        finally:
            conn.close()

        # 2. Build the Matplotlib Frame Canvas
        fig, ax = plt.subplots(figsize=(6, 2.3), facecolor='#1a1c23')
        ax.set_facecolor('#1a1c23')

        # Draw the dynamic trend line
        ax.plot(dates_list, items_sold_count, color='#1f538d', marker='o', linewidth=2.5, markersize=6)

        # Apply dark theme styling parameters
        ax.tick_params(colors='white', labelsize=9)
        ax.grid(True, color='#2c2e3b', linestyle='--', linewidth=0.5)
        
        # Enforce integers on Y-axis since we are counting individual sports items
        from matplotlib.ticker import MaxNLocator
        ax.yaxis.set_major_locator(MaxNLocator(integer=True))

        for spine in ax.spines.values():
            spine.set_visible(False)

        # Mount canvas onto the custom frame
        canvas = FigureCanvasTkAgg(fig, master=self.chart_frame)
        canvas_widget = canvas.get_tk_widget()
        canvas_widget.pack(fill="both", expand=True, padx=15, pady=15)
        canvas.draw()

    def refresh_dashboard_metrics(self):
        """Recalculates active sales quantities and updates dashboard metric cards instantly."""
        import datetime
        today_date = datetime.datetime.now().strftime("%d-%m-%Y")

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        
        try:

            # Paste this inside the try block of refresh_dashboard_metrics(self):
            cursor.execute("SELECT COUNT(*) FROM products WHERE stock_qty <= 3")
            low_stock_count = cursor.fetchone()[0]
            self.lbl_stock_warning_metric.configure(text=str(low_stock_count))

            # 1. Update Today's Sales Count Card (Unique Invoices processed today)
            cursor.execute("SELECT COUNT(*) FROM sales WHERE date_time LIKE ?", (f"{today_date}%",))
            today_invoice_count = cursor.fetchone()[0]
            self.lbl_sales_metric.configure(text=str(today_invoice_count))
            
            # 2. Re-render the Weekly Items Sold Trend Chart Canvas
            self.render_weekly_matplotlib_chart()
            
            # 3. Handle Earnings Card state safely
            if not self.earnings_hidden:
                # If privacy eye is currently UNLOCKED, recalculate and show numbers immediately
                self.earnings_hidden = True 
                self.toggle_earnings_visibility() # Toggles to False and updates layout
            else:
                # If locked, keep the bullet mask intact
                self.lbl_earnings_metric.configure(text="••••• PKR")
                
        except Exception as e:
            print(f"Metrics synchronization error: {e}")
        finally:
            conn.close()

    # ==========================================
    # CORE INTERFACE: INVENTORY MANAGEMENT PAGE
    # ==========================================
    def build_inventory_view(self, parent_frame):
        # --- LEFT PANEL: Input Controls Form ---
        self.inv_left_frame = ctk.CTkFrame(parent_frame, width=340, corner_radius=10, fg_color="#1a1c23")
        self.inv_left_frame.pack(side="left", fill="y", padx=(0, 15), pady=10)
        self.inv_left_frame.pack_propagate(False)

        ctk.CTkLabel(self.inv_left_frame, text="Stock Operations Form", font=("Arial", 15, "bold")).pack(pady=(12, 8))
        # Track selected product row ID
        self.inv_selected_id = None

        # Input Forms stack
        ctk.CTkLabel(self.inv_left_frame, text="Product Name:").pack(anchor="w", padx=25, pady=(2, 0))
        self.ent_inv_name = ctk.CTkEntry(self.inv_left_frame, width=280, placeholder_text="e.g., Malik Premium Bat", height=28)
        self.ent_inv_name.pack(padx=25, pady=2)

        ctk.CTkLabel(self.inv_left_frame, text="Category:").pack(anchor="w", padx=25, pady=(2, 0))
        self.ent_inv_cat = ctk.CTkEntry(self.inv_left_frame, width=280, placeholder_text="e.g., Cricket", height=28)
        self.ent_inv_cat.pack(padx=25, pady=2)

        ctk.CTkLabel(self.inv_left_frame, text="Wholesale Cost Price (PKR):").pack(anchor="w", padx=25, pady=(2, 0))
        self.ent_inv_cost = ctk.CTkEntry(self.inv_left_frame, width=280, placeholder_text="e.g., 2000", height=28)
        self.ent_inv_cost.pack(padx=25, pady=2)

        ctk.CTkLabel(self.inv_left_frame, text="Retail Sale Price (PKR):").pack(anchor="w", padx=25, pady=(2, 0))
        self.ent_inv_retail = ctk.CTkEntry(self.inv_left_frame, width=280, placeholder_text="e.g., 3000", height=28)
        self.ent_inv_retail.pack(padx=25, pady=2)

        ctk.CTkLabel(self.inv_left_frame, text="Initial Stock Quantity:").pack(anchor="w", padx=25, pady=(2, 0))
        self.ent_inv_stock = ctk.CTkEntry(self.inv_left_frame, width=280, placeholder_text="e.g., 15", height=28)
        self.ent_inv_stock.pack(padx=25, pady=2)

        # Action Buttons
        self.btn_inv_add = ctk.CTkButton(self.inv_left_frame, text="ADD ITEM", fg_color="green", hover_color="#006400", command=self.inv_add_item)
        self.btn_inv_add.pack(fill="x", padx=25, pady=(12, 3))
        self.btn_inv_update = ctk.CTkButton(self.inv_left_frame, text="UPDATE SELECTED", command=self.inv_update_item)
        self.btn_inv_update.pack(fill="x", padx=25, pady=3)

        self.btn_inv_delete = ctk.CTkButton(self.inv_left_frame, text="DELETE SELECTED", fg_color="red", hover_color="#8B0000", command=self.inv_delete_item)
        self.btn_inv_delete.pack(fill="x", padx=25, pady=3)

        self.btn_inv_clear = ctk.CTkButton(self.inv_left_frame, text="Clear Form", fg_color="gray", command=self.inv_clear_form)
        self.btn_inv_clear.pack(fill="x", padx=25, pady=3)

        self.btn_inv_excel = ctk.CTkButton(self.inv_left_frame, text="📥 Bulk Import Excel", fg_color="#8e44ad", hover_color="#732d91", command=self.inv_import_excel)
        self.btn_inv_excel.pack(fill="x", padx=25, pady=3)


        # --- RIGHT PANEL: Spreadsheet Data Grid View ---
        self.inv_right_frame = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="#1a1c23")
        self.inv_right_frame.pack(side="right", fill="both", expand=True, pady=10)

        self.inv_search_var = ctk.StringVar()
        self.inv_search_var.trace_add("write", self.inv_load_data)
        self.ent_inv_search = ctk.CTkEntry(self.inv_right_frame, placeholder_text="🔍 Live search current stock by description or type...", textvariable=self.inv_search_var)
        self.ent_inv_search.pack(fill="x", padx=20, pady=15)

        # Table configuration mapping standard styling rules
        style = ttk.Style()
        style.configure("Treeview", background="#2a2d2e", foreground="white", rowheight=30, fieldbackground="#2a2d2e", borderwidth=0, font=("Arial", 12))
        style.configure("Treeview.Heading", background="#1f538d", foreground="black", font=("Arial", 12, "bold"))

        # NOTE: Cost price is HIDDEN from this table view layout for cashier front safety counter rules
        self.inv_table = ttk.Treeview(self.inv_right_frame, columns=("id", "name", "cat", "retail", "stock"), show="headings")
        self.inv_table.heading("id", text="ID")
        self.inv_table.heading("name", text="Product Description")
        self.inv_table.heading("cat", text="Category")
        self.inv_table.heading("retail", text="Retail Price (PKR)")
        self.inv_table.heading("stock", text="In-Stock Qty")
        
        self.inv_table.column("id", width=50, anchor="center")
        self.inv_table.column("retail", width=120, anchor="center")
        self.inv_table.column("stock", width=100, anchor="center")
        self.inv_table.pack(fill="both", expand=True, padx=20, pady=(0, 20))
        self.inv_table.bind("<<TreeviewSelect>>", self.inv_on_row_select)

        # Critical stock level color configurations
        self.inv_table.tag_configure("critical_stock", background="#7A1C1C", foreground="white")
        self.inv_table.tag_configure("warning_stock", background="#8A731A", foreground="white")

        self.inv_load_data()

    # ==========================================
    # DATABASE BACKEND ACTIONS FOR INVENTORY
    # ==========================================
    def inv_load_data(self, *args):
        """Fetches items dynamically from SQLite database and populates the table."""
        for item in self.inv_table.get_children():
            self.inv_table.delete(item)

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        search_term = f"%{self.inv_search_var.get()}%"
        
        # Pulls specific columns, keeping cost_price safe from standard view
        cursor.execute("SELECT id, product_name, category, retail_price, stock_qty FROM products WHERE product_name LIKE ? OR category LIKE ?", (search_term, search_term))
        rows = cursor.fetchall()
        
        for row in rows:
            qty = row[4]
            if qty <= 1:
                self.inv_table.insert("", "end", values=row, tags=("critical_stock",))
            elif qty <= 3:
                self.inv_table.insert("", "end", values=row, tags=("warning_stock",))
            else:
                self.inv_table.insert("", "end", values=row)
        conn.close()

    def inv_add_item(self):
        """Adds a fresh item row, or automatically sums quantities if name matching exists."""
        if not self.ent_inv_name.get() or not self.ent_inv_cost.get() or not self.ent_inv_retail.get() or not self.ent_inv_stock.get():
            messagebox.showwarning("Input Missing", "Please fill up all required item specifications form parameters!")
            return

        name = self.ent_inv_name.get().strip()
        cat = self.ent_inv_cat.get().strip()
        cost = int(self.ent_inv_cost.get())
        retail = int(self.ent_inv_retail.get())
        qty = int(self.ent_inv_stock.get())

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()

        # Check for duplication name records
        cursor.execute("SELECT id, stock_qty FROM products WHERE LOWER(product_name) = LOWER(?)", (name,))
        existing = cursor.fetchone()

        if existing:
            new_qty = existing[1] + qty
            cursor.execute("UPDATE products SET stock_qty=?, cost_price=?, retail_price=?, category=? WHERE id=?", (new_qty, cost, retail, cat, existing[0]))
            messagebox.showinfo("Stock Merged", f"'{name}' matched an existing record. Stock updated to {new_qty} total items.")
        else:
            cursor.execute("INSERT INTO products (product_name, category, cost_price, retail_price, stock_qty) VALUES (?, ?, ?, ?, ?)", (name, cat, cost, retail, qty))
            messagebox.showinfo("Success", f"'{name}' successfully added to the database.")

        conn.commit()
        conn.close()
        self.inv_load_data()
        self.inv_clear_form()

    def inv_on_row_select(self, event):
        """Autofills the entry boxes when an item in the data grid is highlighted."""
        selected = self.inv_table.selection()
        if not selected:
            return

        row_vals = self.inv_table.item(selected[0])['values']
        self.inv_selected_id = row_vals[0]

        # Fetch the complete product entry (including hidden cost price) from database
        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        cursor.execute("SELECT cost_price FROM products WHERE id = ?", (self.inv_selected_id,))
        cost_price_record = cursor.fetchone()[0]
        conn.close()

        self.inv_clear_form(keep_id=True)
        self.ent_inv_name.insert(0, row_vals[1])
        self.ent_inv_cat.insert(0, row_vals[2])
        self.ent_inv_cost.insert(0, str(cost_price_record))
        self.ent_inv_retail.insert(0, row_vals[3])
        self.ent_inv_stock.insert(0, row_vals[4])

    def inv_update_item(self):
        """Overwrites parameters for a specific item entry ID."""
        if not self.inv_selected_id:
            messagebox.showwarning("Selection Missing", "Please select an item line from the table list first.")
            return

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE products SET product_name=?, category=?, cost_price=?, retail_price=?, stock_qty=? WHERE id=?",
            (self.ent_inv_name.get(), self.ent_inv_cat.get(), int(self.ent_inv_cost.get()), int(self.ent_inv_retail.get()), int(self.ent_inv_stock.get()), self.inv_selected_id)
        )
        conn.commit()
        conn.close()
        self.inv_load_data()
        self.inv_clear_form()
        messagebox.showinfo("Success", "Product attributes updated safely.")

    def inv_delete_item(self):
        """Deletes a product row completely from the database logs."""
        if not self.inv_selected_id:
            return

        if messagebox.askyesno("Confirm Purge", "Are you entirely certain you want to remove this item entry permanently?"):
            conn = sqlite3.connect("durrani_sports.db")
            cursor = conn.cursor()
            cursor.execute("DELETE FROM products WHERE id=?", (self.inv_selected_id,))
            conn.commit()
            conn.close()
            self.inv_load_data()
            self.inv_clear_form()

    def inv_clear_form(self, keep_id=False):
        if not keep_id:
            self.inv_selected_id = None
        self.ent_inv_name.delete(0, 'end')
        self.ent_inv_cat.delete(0, 'end')
        self.ent_inv_cost.delete(0, 'end')
        self.ent_inv_retail.delete(0, 'end')
        self.ent_inv_stock.delete(0, 'end')

    def inv_import_excel(self):
        """Allows the administrator to pick an Excel sheet and parse its items into the database."""
        from tkinter import filedialog
        import pandas as pd

        file_path = filedialog.askopenfilename(filetypes=[("Excel Files", "*.xlsx *.xls"), ("CSV Files", "*.csv")])
        if not file_path:
            return

        try:
            # Read file using pandas
            if file_path.endswith('.csv'):
                df = pd.read_csv(file_path)
            else:
                df = pd.read_excel(file_path)

            # Standardize column header strings to prevent spelling bugs
            df.columns = [str(c).strip().lower().replace(" ", "_") for c in df.columns]

            # Validate structural pillars are present
            required = ["product_name", "category", "cost_price", "retail_price", "stock_qty"]
            if not all(col in df.columns for col in required):
                messagebox.showerror("Schema Error", f"Excel must contain these exact headers:\n{required}")
                return

            conn = sqlite3.connect("durrani_sports.db")
            cursor = conn.cursor()
            
            imported_count = 0
            for _, row in df.iterrows():
                name = str(row['product_name']).strip()
                cat = str(row['category']).strip()
                cost = int(row['cost_price'])
                retail = int(row['retail_price'])
                qty = int(row['stock_qty'])

                # Merge quantities gracefully if the exact item exists
                cursor.execute("SELECT id, stock_qty FROM products WHERE LOWER(product_name) = LOWER(?)", (name,))
                existing = cursor.fetchone()

                if existing:
                    cursor.execute("UPDATE products SET stock_qty = stock_qty + ? WHERE id = ?", (qty, existing[0]))
                else:
                    cursor.execute("INSERT INTO products (product_name, category, cost_price, retail_price, stock_qty) VALUES (?, ?, ?, ?, ?)", (name, cat, cost, retail, qty))
                imported_count += 1

            conn.commit()
            conn.close()
            
            messagebox.showinfo("Import Success", f"Successfully processed {imported_count} product lines from Excel spreadsheet!")
            self.inv_load_data() # Update inventory screen layout view rows
            self.refresh_dashboard_metrics() # Refresh metrics cards quantities

        except Exception as e:
            messagebox.showerror("Import Failed", f"Could not parse spreadsheet metrics cleanly:\n{e}")

    # ==========================================
    # CORE INTERFACE: CASHIER BILLING PAD PAGE
    # ==========================================
    def build_billing_view(self, parent_frame):
        self.invoice_items = []

        # === LEFT COLUMN: QUICK STOCK SEARCH ===
        self.bill_left_frame = ctk.CTkFrame(parent_frame, width=420, corner_radius=10, fg_color="#1a1c23")
        self.bill_left_frame.pack(side="left", fill="y", padx=(0, 15), pady=10)
        self.bill_left_frame.pack_propagate(False)

        ctk.CTkLabel(self.bill_left_frame, text="🔍 Quick Stock Catalog", font=("Arial", 16, "bold")).pack(pady=15)
        
        self.bill_search_var = ctk.StringVar()
        self.bill_search_var.trace_add("write", self.bill_search_dropdown)
        
        # FIX 1: Linked and packed the correct widget variable name
        self.ent_bill_search = ctk.CTkEntry(self.bill_left_frame, placeholder_text="Type item name to search...", height=35, textvariable=self.bill_search_var)
        self.ent_bill_search.pack(fill="x", padx=15, pady=5)

        # FIX 2: Constrained height to exactly 20 rows without vertical inflation flags
        self.bill_drop_grid = ttk.Treeview(self.bill_left_frame, columns=("id", "name", "price", "stock"), show="headings", height=20)
        self.bill_drop_grid.heading("id", text="ID")
        self.bill_drop_grid.heading("name", text="Product Description")
        self.bill_drop_grid.heading("price", text="Price")
        self.bill_drop_grid.heading("stock", text="Stock")
        self.bill_drop_grid.column("id", width=40, anchor="center")
        self.bill_drop_grid.column("price", width=70, anchor="center")
        self.bill_drop_grid.column("stock", width=60, anchor="center")
        self.bill_drop_grid.pack(fill="x", padx=15, pady=15)
        self.bill_drop_grid.bind("<<TreeviewSelect>>", self.bill_select_product)


        # === RIGHT COLUMN: DIGITAL INVOICE PAD ===
        self.bill_right_frame = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="#1e222b")
        self.bill_right_frame.pack(side="right", fill="both", expand=True, pady=10)

        ctk.CTkLabel(self.bill_right_frame, text="📄 Current Customer Invoice", font=("Arial", 16, "bold")).pack(pady=(15, 5))

        # Customer Metadata Inputs
        self.cust_meta_frame = ctk.CTkFrame(self.bill_right_frame, fg_color="transparent")
        self.cust_meta_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(self.cust_meta_frame, text="Customer:").pack(side="left", padx=(0, 5))
        self.ent_cust_name = ctk.CTkEntry(self.cust_meta_frame, placeholder_text="Customer Name", width=180, height=30)
        self.ent_cust_name.pack(side="left", padx=(0, 15))

        ctk.CTkLabel(self.cust_meta_frame, text="Phone:").pack(side="left", padx=(0, 5))
        self.ent_cust_phone = ctk.CTkEntry(self.cust_meta_frame, placeholder_text="03xx-xxxxxxx", width=150, height=30)
        self.ent_cust_phone.pack(side="left")

        # FIX 3: Fixed vertical boundary allocation size limit to 8 rows
        self.bill_table = ttk.Treeview(self.bill_right_frame, columns=("name", "price", "qty", "total"), show="headings", height=10)
        self.bill_table.heading("name", text="Item Description")
        self.bill_table.heading("price", text="Unit Price")
        self.bill_table.heading("qty", text="Qty")
        self.bill_table.heading("total", text="Total (PKR)")
        self.bill_table.column("price", width=100, anchor="center")
        self.bill_table.column("qty", width=60, anchor="center")
        self.bill_table.column("total", width=110, anchor="center")
        self.bill_table.pack(fill="x", padx=15, pady=10)

        # Line modifiers utilities row
        self.bill_utils_frame = ctk.CTkFrame(self.bill_right_frame, fg_color="transparent")
        self.bill_utils_frame.pack(fill="x", padx=15, pady=5)

        ctk.CTkButton(self.bill_utils_frame, text="▲ Qty Up", width=100, fg_color="#1f538d", command=lambda: self.bill_adjust_qty(1)).pack(side="left", padx=5)
        ctk.CTkButton(self.bill_utils_frame, text="▼ Qty Down", width=100, fg_color="gray", command=lambda: self.bill_adjust_qty(-1)).pack(side="left", padx=5)
        ctk.CTkButton(self.bill_utils_frame, text="🗑️ Remove Row", width=120, fg_color="#7A1C1C", hover_color="#5A1515", command=self.bill_remove_row).pack(side="left", padx=15)

        # === SUMMARY FOOTER BLOCK ===
        self.summary_footer = ctk.CTkFrame(self.bill_right_frame, height=140, corner_radius=8, fg_color="#14171c")
        self.summary_footer.pack(fill="x", padx=15, pady=(10, 15))
        self.summary_footer.pack_propagate(False) # Forces the frame to honor our height setting

        # Left Column inside Footer: Pricing Calculations & Inputs
        self.calc_pane = ctk.CTkFrame(self.summary_footer, fg_color="transparent")
        self.calc_pane.pack(side="left", padx=20, pady=10)

        self.lbl_bill_subtotal = ctk.CTkLabel(self.calc_pane, text="Subtotal: 0 PKR", font=("Arial", 14, "bold"))
        self.lbl_bill_subtotal.pack(anchor="w", pady=2)

        self.disc_row = ctk.CTkFrame(self.calc_pane, fg_color="transparent")
        self.disc_row.pack(anchor="w", pady=5)
        ctk.CTkLabel(self.disc_row, text="Discount Given: ").pack(side="left")
        self.ent_bill_discount = ctk.CTkEntry(self.disc_row, placeholder_text="0 (e.g. 500 or 10%)", width=150, height=28)
        self.ent_bill_discount.pack(side="left", padx=5)
        self.ent_bill_discount.bind("<KeyRelease>", lambda e: self.bill_update_totals())

        # Right Column inside Footer: Separation frame for Grand Total and the Print Button
        self.action_pane = ctk.CTkFrame(self.summary_footer, fg_color="transparent")
        self.action_pane.pack(side="right", padx=20, pady=10)

        self.lbl_bill_grand_total = ctk.CTkLabel(self.action_pane, text="TOTAL: 0 PKR", text_color="#2ecc71", font=("Arial", 22, "bold"))
        self.lbl_bill_grand_total.pack(side="top", anchor="e", pady=(5, 10))

        self.btn_bill_print = ctk.CTkButton(self.action_pane, text="🖨️ PRINT INVOICE", font=("Arial", 14, "bold"), 
                                            fg_color="green", hover_color="#006400", width=180, height=40, 
                                            command=self.bill_process_checkout)
        self.btn_bill_print.pack(side="top", anchor="e")
        
        self.bill_search_dropdown()

    # ==========================================
    # CASHIER OPERATIONS BACKEND FUNCTIONS
    # ==========================================

    def bill_search_dropdown(self, *args):
        """Live filters stock database entries whenever text is typed into the search box."""
        for item in self.bill_drop_grid.get_children():
            self.bill_drop_grid.delete(item)
            
        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        
        # Adding *args handles the tracking parameters safely
        term = f"%{self.bill_search_var.get().strip().lower()}%"
        cursor.execute("SELECT id, product_name, retail_price, stock_qty FROM products WHERE LOWER(product_name) LIKE ?", (term,))
        
        for row in cursor.fetchall():
            self.bill_drop_grid.insert("", "end", values=row)
        conn.close()

    def bill_select_product(self, event):
        selected = self.bill_drop_grid.selection()
        if not selected: return
        p_id, p_name, p_price, p_stock = self.bill_drop_grid.item(selected[0])['values']
        
        if p_stock <= 0:
            messagebox.showwarning("Out of Stock", "This sports item has no stock left!")
            return

        for item in self.invoice_items:
            if item['id'] == p_id:
                if item['qty'] < p_stock:
                    item['qty'] += 1
                self.bill_refresh_pad_view()
                return

        self.invoice_items.append({"id": p_id, "name": p_name, "price": int(p_price), "qty": 1, "max_stock": p_stock})
        self.bill_refresh_pad_view()

    def bill_refresh_pad_view(self):
        for item in self.bill_table.get_children():
            self.bill_table.delete(item)
        for idx, item in enumerate(self.invoice_items):
            line_total = item['price'] * item['qty']
            self.bill_table.insert("", "end", iid=idx, values=(item['name'], item['price'], item['qty'], line_total))
        self.bill_update_totals()

    def bill_adjust_qty(self, delta):
        selected = self.bill_table.selection()
        if not selected: return
        idx = int(selected[0])
        item = self.invoice_items[idx]
        
        if delta > 0 and item['qty'] >= item['max_stock']:
            messagebox.showwarning("Stock Limit", "Cannot sell more units than stored in active inventory!")
            return
            
        item['qty'] += delta
        if item['qty'] <= 0:
            del self.invoice_items[idx]
        self.bill_refresh_pad_view()

    def bill_remove_row(self):
        selected = self.bill_table.selection()
        if not selected: return
        idx = int(selected[0])
        del self.invoice_items[idx]
        self.bill_refresh_pad_view()

    def bill_update_totals(self):
        subtotal = sum(item['price'] * item['qty'] for item in self.invoice_items)
        disc_text = self.ent_bill_discount.get().strip()
        discount = 0.0

        if disc_text:
            try:
                if "%" in disc_text:
                    pct = float(disc_text.replace("%", ""))
                    discount = subtotal * (pct / 100.0)
                else:
                    discount = float(disc_text)
            except ValueError:
                discount = 0.0

        discount = min(max(discount, 0.0), subtotal)
        self.bill_grand_total = int(subtotal - discount)
        self.bill_discount_amount = int(discount)
        self.bill_subtotal_amount = int(subtotal)

        self.lbl_bill_subtotal.configure(text=f"Subtotal: {subtotal:,} PKR")
        self.lbl_bill_grand_total.configure(text=f"TOTAL: {self.bill_grand_total:,} PKR")

    def bill_process_checkout(self):
        """Compiles ReportLab layout parameters, saves the A5 PDF file, and inserts relational database entries."""
        if not self.invoice_items:
            messagebox.showwarning("Empty Invoice", "Please add items to the invoice pad before checking out!")
            return

        from datetime import datetime
        now = datetime.now()
        date_str = now.strftime("%d-%m-%Y")
        time_str = now.strftime("%I:%M %p")
        invoice_number = f"INV-{now.strftime('%Y%m%d%H%M%S')}"

        c_name = self.ent_cust_name.get().strip() if self.ent_cust_name.get().strip() else "Walk-in Client"
        c_phone = self.ent_cust_phone.get().strip() if self.ent_cust_phone.get().strip() else "N/A"

        # Unique file destination configuration
        pdf_filename = f"{invoice_number}.pdf"

        # --- REPORTLAB A5 PDF GENERATION MODULE ---
        try:
            # 1. Setup Document Core Template Boundaries
            doc = SimpleDocTemplate(pdf_filename, pagesize=A5, rightMargin=20, leftMargin=20, topMargin=15, bottomMargin=15)
            story = []
            styles = getSampleStyleSheet()

            # Dynamic Typography Configuration Styles
            title_style = ParagraphStyle('ShopTitle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=16, alignment=1, textColor=colors.HexColor("#1f538d"))
            prop_style = ParagraphStyle('PropTitle', fontName='Helvetica-Oblique', fontSize=9, alignment=1, textColor=colors.HexColor("#555555"))
            meta_style = ParagraphStyle('MetaText', fontName='Helvetica', fontSize=9, leading=12)

            # Build Header Identity Blocks
            if os.path.exists("logo.png"):
                story.append(Image("logo.png", width=50, height=50))
                story.append(Spacer(1, 5))
        
            story.append(Paragraph("Durrani Sports Nowshera", title_style))
            story.append(Paragraph("Prop. Haris Durrani 0333-5799214", prop_style))
            story.append(Spacer(1, 10))

            # Metadata Table Segment Block
            meta_data = [
                [Paragraph(f"<b>Date:</b> {date_str}", meta_style), Paragraph(f"<b>Name:</b> {c_name}", meta_style)],
                [Paragraph(f"<b>Time:</b> {time_str}", meta_style), Paragraph(f"<b>Phone:</b> {c_phone}", meta_style)],
                [Paragraph(f"<b>Invoice #:</b> {invoice_number}", meta_style), Paragraph("", meta_style)]
            ]
            meta_table = Table(meta_data, colWidths=[190, 190])
            meta_table.setStyle(TableStyle([('VALIGN', (0,0), (-1,-1), 'TOP')]))
            story.append(meta_table)
            story.append(Spacer(1, 12))

            # Item Grid Rows Matrix Construction
            table_content = [["Item Description", "Unit Price", "Qty", "Total"]]
            for item in self.invoice_items:
                line_tot = item['price'] * item['qty']
                table_content.append([item['name'], f"{item['price']:,}", str(item['qty']), f"{line_tot:,}"])

            # Render Table Matrix Columns Constraints Layout
            item_table = Table(table_content, colWidths=[180, 65, 45, 90])
            item_table.setStyle(TableStyle([
                ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1f538d")),
                ('TEXTCOLOR', (0,0), (-1,0), colors.white),
                ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
                ('FONTSIZE', (0,0), (-1,0), 10),
                ('BOTTOMPADDING', (0,0), (-1,0), 5),
                ('ALIGN', (1,0), (-1,-1), 'CENTER'),
                ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
                ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
                ('FONTSIZE', (0,1), (-1,-1), 9),
                ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#f9f9f9")]),
            ]))
            story.append(item_table)
            story.append(Spacer(1, 12))

            # Financial Summary Block Section
            summary_content = [
                ["", "Subtotal:", f"{self.bill_subtotal_amount:,} PKR"],
                ["", "Discount Given:", f"-{self.bill_discount_amount:,} PKR"],
                ["", "GRAND TOTAL:", f"{self.bill_grand_total:,} PKR"]
            ]
            summary_table = Table(summary_content, colWidths=[150, 100, 130])
            summary_table.setStyle(TableStyle([
                ('ALIGN', (1,0), (-1,-1), 'RIGHT'),
                ('FONTNAME', (1,0), (1,-1), 'Helvetica-Bold'),
                ('FONTNAME', (1,2), (2,2), 'Helvetica-Bold'),
                ('FONTSIZE', (1,2), (2,2), 11),
                ('TEXTCOLOR', (1,2), (2,2), colors.HexColor("#27ae60")),
            ]))
            story.append(summary_table)

            # Compiles ReportLab data streams and flushes physical PDF out onto memory track
            doc.build(story)

        except Exception as pdf_error:
            messagebox.showerror("Layout Engine Error", f"ReportLab failed to generate PDF file: {pdf_error}")
            return

        # --- DATABASE CONTROLLER LOGS WRITER ---
        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        try:
            # 1. Log structural Invoice details inside master sales table
            cursor.execute(
                "INSERT INTO sales (invoice_id, customer_name, ph_number, date_time, subtotal, discount_amount, amount_collected) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (invoice_number, c_name, c_phone, f"{date_str} {time_str}", self.bill_subtotal_amount, self.bill_discount_amount, self.bill_grand_total)
            )

            # 2. Append item lines row-by-row into structural content tables & subtract available warehouse metrics
            for item in self.invoice_items:
                cursor.execute("INSERT INTO sales_items (invoice_id, product_id, product_name, quantity, sold_price) VALUES (?, ?, ?, ?, ?)",
                               (invoice_number, item['id'], item['name'], item['qty'], item['price']))
                cursor.execute("UPDATE products SET stock_qty = stock_qty - ? WHERE id = ?", (item['qty'], item['id']))

            conn.commit()
            messagebox.showinfo("Success", f"Transaction finalized!\n\nInvoice File Written: {pdf_filename}\nStock quantities updated.")

            self.refresh_dashboard_metrics()
            self.inv_load_data()

            # Form layout fields clear operations routine
            self.invoice_items.clear()
            self.bill_refresh_pad_view()
            self.ent_cust_name.delete(0, 'end')
            self.ent_cust_phone.delete(0, 'end')
            self.ent_bill_discount.delete(0, 'end')
            self.bill_search_dropdown()
            self.sales_load_history() # Dynamically refreshes sales history table grid behind the scenes

        except Exception as db_error:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed checkout entry write action: {db_error}")
        finally:
            conn.close()

    # ==========================================
    # CORE INTERFACE: SALES HISTORY LOG PAGE
    # ==========================================
    def build_sales_view(self, parent_frame):
        self.sales_main_frame = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="#1a1c23")
        self.sales_main_frame.pack(fill="both", expand=True, pady=10)

        # Operational Control Bar
        self.sales_ctrl_bar = ctk.CTkFrame(self.sales_main_frame, fg_color="transparent")
        self.sales_ctrl_bar.pack(fill="x", padx=15, pady=15)

        # Live Dynamic Search Input
        self.sales_search_var = ctk.StringVar()
        self.sales_search_var.trace_add("write", self.sales_load_history)
        self.ent_sales_search = ctk.CTkEntry(self.sales_ctrl_bar, placeholder_text="🔍 Search invoices by ID, Customer Name, or Phone Number...", textvariable=self.sales_search_var, width=500, height=35)
        self.ent_sales_search.pack(side="left", padx=5)

        # NEW REFRESH BUTTON: Packed right after the search input bar
        self.btn_sales_refresh = ctk.CTkButton(self.sales_ctrl_bar, text="🔄", width=40, height=35, 
                                               fg_color="#2b2d3a", hover_color="#3e4154", 
                                               font=("Arial", 14), command=self.sales_load_history)
        self.btn_sales_refresh.pack(side="left", padx=5)

        # Action Button for Returns
        self.btn_sales_return = ctk.CTkButton(self.sales_ctrl_bar, text="↩ Process Product Return", fg_color="#e67e22", hover_color="#d35400", height=35, font=("Arial", 12, "bold"), command=self.sales_void_invoice)
        self.btn_sales_return.pack(side="right", padx=5)

        # Master Sales Data Grid View Layout
        self.sales_table = ttk.Treeview(self.sales_main_frame, columns=("inv_id", "datetime", "cust_name", "phone", "amount"), show="headings", height=15)
        self.sales_table.heading("inv_id", text="Invoice ID")
        self.sales_table.heading("datetime", text="Date & Time")
        self.sales_table.heading("cust_name", text="Customer Name")
        self.sales_table.heading("phone", text="Phone Number")
        self.sales_table.heading("amount", text="Amount Collected")
        
        self.sales_table.column("inv_id", width=160, anchor="center")
        self.sales_table.column("datetime", width=180, anchor="center")
        self.sales_table.column("cust_name", width=220, anchor="w")
        self.sales_table.column("phone", width=130, anchor="center")
        self.sales_table.column("amount", width=150, anchor="center")
        self.sales_table.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Bind double click to try opening the invoice file directly
        self.sales_table.bind("<Double-1>", self.sales_open_pdf)

        self.sales_load_history()

    # ==========================================
    # SALES HISTORY MODULE ACTION CODE
    # ==========================================
    def sales_load_history(self, *args):
        """Fetches sales headers from your new schema with live wildcard filtering."""
        for item in self.sales_table.get_children():
            self.sales_table.delete(item)

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        
        term = f"%{self.sales_search_var.get().strip()}%"
        cursor.execute("""
            SELECT invoice_id, date_time, customer_name, ph_number, amount_collected 
            FROM sales 
            WHERE invoice_id LIKE ? OR customer_name LIKE ? OR ph_number LIKE ?
            ORDER BY date_time DESC
        """, (term, term, term))
        
        for row in cursor.fetchall():
            display_row = (row[0], row[1], row[2], row[3], f"{row[4]:,} PKR")
            self.sales_table.insert("", "end", values=display_row)
        conn.close()

    def sales_open_pdf(self, event):
        """Double click handler to start visual file inspection instantly."""
        import os
        selected = self.sales_table.selection()
        if not selected: return
        inv_id = self.sales_table.item(selected[0])['values'][0]
        filename = f"{inv_id}.pdf"
        
        if os.path.exists(filename):
            os.startfile(filename)
        else:
            messagebox.showerror("File Error", f"Could not find local file: {filename}\nIt may have been renamed or moved.")

    def sales_void_invoice(self):
        """Moves entire invoice parameters into the Returns archive log and removes it from active sales."""
        selected = self.sales_table.selection()
        if not selected:
            messagebox.showwarning("Selection Missing", "Please pick an invoice line from the history list first!")
            return

        row_vals = self.sales_table.item(selected[0])['values']
        inv_id = str(row_vals[0])
        c_name = str(row_vals[2])
        c_phone = str(row_vals[3])
        collected_amt = int(str(row_vals[4]).replace(" PKR", "").replace(",", ""))

        confirm = messagebox.askyesno("Process Return", f"Are you entirely sure you want to completely void invoice #{inv_id}?\nThis record will be cataloged inside your Returns Archive Log.")
        if not confirm: return

        return_reason = ctk.CTkInputDialog(text="Enter Reason for Product Return:", title="Return Verification").get_input()
        if not return_reason or return_reason.strip() == "":
            return_reason = "Customer Return / Full Void" # Default fallback string
        else:
            return_reason = return_reason.strip()

        from datetime import datetime
        now = datetime.now()
        current_dt = now.strftime("%Y-%m-%Y %I:%M %p")

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()

        try:
            # 1. Fetch item entries belonging to this sale to refund warehouse quantities
            cursor.execute("SELECT product_id, product_name, quantity FROM sales_items WHERE invoice_id = ?", (inv_id,))
            items = cursor.fetchall()

            for p_id, p_name, qty in items:
                # Restores quantities back to available inventory records rows
                cursor.execute("UPDATE products SET stock_qty = stock_qty + ? WHERE id = ?", (qty, p_id))
                # Write individual rows to returns ledger archive logs
                cursor.execute("""
                    INSERT INTO returns (invoice_id, product_id, product_name, returned_qty, refund_amount, date_time, reason)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (inv_id, p_id, p_name, qty, collected_amt, current_dt, return_reason))

            # 2. Drop records completely from primary active sales logs tracking tables
            cursor.execute("DELETE FROM sales WHERE invoice_id = ?", (inv_id,))
            cursor.execute("DELETE FROM sales_items WHERE invoice_id = ?", (inv_id,))

            conn.commit()
            messagebox.showinfo("Success", f"Invoice #{inv_id} processed completely. Stock records restored.")

            self.refresh_dashboard_metrics()
            
            self.sales_load_history()
            self.inv_load_data() # Refresh background stock sheets views automatically
            
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed log shifting routine operations: {e}")
        finally:
            conn.close()

    # ==========================================
    # CORE INTERFACE: RETURNS ARCHIVE LOG PAGE
    # ==========================================
    def build_returns_view(self, parent_frame):
        self.ret_main_frame = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="#1a1c23")
        self.ret_main_frame.pack(fill="both", expand=True, pady=10)

        # Operational Control Bar
        self.ret_ctrl_bar = ctk.CTkFrame(self.ret_main_frame, fg_color="transparent")
        self.ret_ctrl_bar.pack(fill="x", padx=15, pady=15)

        # Live Dynamic Search Input for Returns
        self.ret_search_var = ctk.StringVar()
        self.ret_search_var.trace_add("write", self.ret_load_archive)
        self.ent_ret_search = ctk.CTkEntry(self.ret_ctrl_bar, placeholder_text="🔍 Search returns by Invoice ID or Product Name...", textvariable=self.ret_search_var, width=450, height=35)
        self.ent_ret_search.pack(side="left", padx=5)

        # Refresh button dedicated for tracking returns updates
        self.btn_ret_refresh = ctk.CTkButton(self.ret_ctrl_bar, text="🔄", width=40, height=35, 
                                               fg_color="#2b2d3a", hover_color="#3e4154", 
                                               font=("Arial", 14), command=self.ret_load_archive)
        self.btn_ret_refresh.pack(side="left", padx=5)

        # NEW ACTION CONTROL: Packed right next to the refresh button
        self.btn_ret_damaged = ctk.CTkButton(self.ret_ctrl_bar, text="⚠️ Mark Selected as Damaged", 
                                             fg_color="#7A1C1C", hover_color="#5A1515", height=35,
                                             font=("Arial", 12, "bold"), command=self.ret_mark_as_damaged)
        self.btn_ret_damaged.pack(side="right", padx=5)

        # Master Returns Data Grid View Layout Spreadsheet
        self.ret_table = ttk.Treeview(self.ret_main_frame, columns=("inv_id", "prod_name", "qty", "refund", "datetime", "reason"), show="headings", height=15)
        self.ret_table.heading("inv_id", text="Invoice Link ID")
        self.ret_table.heading("prod_name", text="Returned Product Item")
        self.ret_table.heading("qty", text="Qty")
        self.ret_table.heading("refund", text="Refunded Cost")
        self.ret_table.heading("datetime", text="Return Date & Time")
        self.ret_table.heading("reason", text="Reason / Action Log")
        
        self.ret_table.column("inv_id", width=140, anchor="center")
        self.ret_table.column("prod_name", width=200, anchor="w")
        self.ret_table.column("qty", width=60, anchor="center")
        self.ret_table.column("refund", width=120, anchor="center")
        self.ret_table.column("datetime", width=160, anchor="center")
        self.ret_table.column("reason", width=220, anchor="w")
        self.ret_table.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        self.ret_load_archive()

    # ==========================================
    # RETURNS ARCHIVE MODULE BACKEND ACTIONS
    # ==========================================
    def ret_load_archive(self, *args):
        """Fetches returned product items from the relational registry with live wildcard search filtering."""
        for item in self.ret_table.get_children():
            self.ret_table.delete(item)

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        
        term = f"%{self.ret_search_var.get().strip()}%"
        cursor.execute("""
            SELECT invoice_id, product_name, returned_qty, refund_amount, date_time, reason 
            FROM returns 
            WHERE invoice_id LIKE ? OR product_name LIKE ?
            ORDER BY id DESC
        """, (term, term))
        
        for row in cursor.fetchall():
            display_row = (row[0], row[1], row[2], f"{row[3]:,} PKR", row[4], row[5])
            self.ret_table.insert("", "end", values=display_row)
        conn.close()

    def ret_mark_as_damaged(self):
        """Flags an inventory item as unusable, ensuring it is deducted from your shelf count."""
        selected = self.ret_table.selection()
        if not selected:
            messagebox.showwarning("Selection Missing", "Please select a returned item line from the log first.")
            return

        row_vals = self.ret_table.item(selected[0])['values']
        invoice_link = str(row_vals[0])
        product_title = str(row_vals[1])
        qty_to_remove = int(row_vals[2])

        confirm = messagebox.askyesno("Confirm Write-Off", f"Do you want to flag {qty_to_remove}x '{product_title}' as DAMAGED?\n\nThis will permanently deduct them from your storefront stock shelves.")
        if not confirm: return

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        try:
            # 1. Look up the item by name to find its structural database entry ID
            cursor.execute("SELECT id FROM products WHERE product_name = ?", (product_title,))
            product_record = cursor.fetchone()
            
            if product_record:
                # Deduct it from active stock shelves because it's unsellable
                cursor.execute("UPDATE products SET stock_qty = MAX(0, stock_qty - ?) WHERE id = ?", (qty_to_remove, product_record[0]))
            
            # 2. Append/Update the reason string safely inside your returns ledger
            updated_reason = "⚠️ DAMAGED / WASTED WRITE-OFF"
            cursor.execute("UPDATE returns SET reason = ? WHERE invoice_id = ? AND product_name = ?", (updated_reason, invoice_link, product_title))
            
            conn.commit()
            messagebox.showinfo("Inventory Disposed", f"'{product_title}' flagged as damaged. Shelf counts adjusted.")
            
            self.ret_load_archive() # Refresh layout sheets view
            self.inv_load_data()    # Refresh inventory panels
        except Exception as e:
            conn.rollback()
            messagebox.showerror("Database Error", f"Failed write-off routine: {e}")
        finally:
            conn.close()

    
    # ==========================================
    # CORE INTERFACE: HIDDEN ADMIN PANEL PAGE
    # ==========================================
    def build_admin_view(self, parent_frame):
        self.admin_main_frame = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="#1a1c23")
        self.admin_main_frame.pack(fill="both", expand=True, pady=10)

        # Top Control & Information Banner Row
        self.admin_ctrl_bar = ctk.CTkFrame(self.admin_main_frame, fg_color="transparent")
        self.admin_ctrl_bar.pack(fill="x", padx=15, pady=15)

        ctk.CTkLabel(self.admin_ctrl_bar, text="🔒 Restricted Vault", 
                     font=("Arial", 16, "bold"), text_color="#e74c3c").pack(side="left", padx=5)

        # NEW: Live Dynamic Search Input for Admin Cost Sheet
        self.admin_search_var = ctk.StringVar()
        self.admin_search_var.trace_add("write", lambda *args: self.admin_load_cost_ledger())
        self.ent_admin_search = ctk.CTkEntry(self.admin_ctrl_bar, placeholder_text="🔍 Search vault by product name...", textvariable=self.admin_search_var, width=320, height=35)
        self.ent_admin_search.pack(side="left", padx=20)

        self.btn_view_expenses = ctk.CTkButton(self.admin_ctrl_bar, text="📊 View Expense Logs", width=150, height=35, fg_color="#2980b9", hover_color="#2471a3", command=self.admin_open_expenses_window)
        self.btn_view_expenses.pack(side="right", padx=5)

        # NEW: Change PIN Code Security Button Packed on the Control Bar
        self.btn_change_pin = ctk.CTkButton(self.admin_ctrl_bar, text="🔑 Change Security PIN", width=160, height=35, fg_color="#d35400", hover_color="#b33921", command=self.admin_change_pin_dialog)
        self.btn_change_pin.pack(side="right", padx=5)

        # Refresh button dedicated to reloading costs sheets
        self.btn_admin_refresh = ctk.CTkButton(self.admin_ctrl_bar, text="🔄 Refresh", width=160, height=35, 
                                               fg_color="#2b2d3a", hover_color="#3e4154", 
                                               command=self.admin_load_cost_ledger)
        self.btn_admin_refresh.pack(side="right", padx=5)

        # Secret Cost Analysis Data Grid View Layout Spreadsheet
        self.admin_table = ttk.Treeview(self.admin_main_frame, columns=("id", "name", "cat", "cost", "retail", "margin", "stock"), show="headings", height=15)
        self.admin_table.heading("id", text="ID")
        self.admin_table.heading("name", text="Product Description")
        self.admin_table.heading("cat", text="Category")
        self.admin_table.heading("cost", text="Wholesale Cost")
        self.admin_table.heading("retail", text="Retail Price")
        self.admin_table.heading("margin", text="Net Profit Margin")
        self.admin_table.heading("stock", text="In-Stock Qty")
        
        self.admin_table.column("id", width=40, anchor="center")
        self.admin_table.column("name", width=220, anchor="w")
        self.admin_table.column("cat", width=120, anchor="center")
        self.admin_table.column("cost", width=120, anchor="center")
        self.admin_table.column("retail", width=120, anchor="center")
        self.admin_table.column("margin", width=140, anchor="center")
        self.admin_table.column("stock", width=90, anchor="center")
        self.admin_table.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        self.admin_table.bind("<Double-1>", self.admin_inline_modify_cost)

        # Color highlight formatting rule tags for high-profit products
        self.admin_table.tag_configure("high_margin", background="#1e3d2f", foreground="#2ecc71")

        self.admin_load_cost_ledger()

    # ==========================================
    # HIDDEN ADMIN PANEL BACKEND ACTIONS
    # ==========================================

    def admin_inline_modify_cost(self, event):
        """Catches row selections and prompts the owner to directly modify wholesale price records."""
        selected = self.admin_table.selection()
        if not selected:
            return

        row_vals = self.admin_table.item(selected[0])['values']
        product_id = row_vals[0]
        product_desc = row_vals[1]
        current_cost = str(row_vals[3]).replace(" PKR", "").replace(",", "")

        # Target prompt box overlaying the dashboard layout
        new_cost_input = ctk.CTkInputDialog(text=f"Modify Wholesale Buying Cost for:\n'{product_desc}'\n\nCurrent: {current_cost} PKR\nEnter New Wholesale Cost Price:", title="Inline Cost Ledger Override").get_input()

        if new_cost_input is None: # Canceled operation
            return

        try:
            new_cost_val = int(new_cost_input.strip())
            if new_cost_val < 0: raise ValueError
            
            conn = sqlite3.connect("durrani_sports.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE products SET cost_price = ? WHERE id = ?", (new_cost_val, product_id))
            conn.commit()
            conn.close()
            
            messagebox.showinfo("Vault Modified", f"Updated cost for '{product_desc}' successfully.")
            self.admin_load_cost_ledger() # Hot-reload Admin spreadsheet rows grid view
            self.refresh_dashboard_metrics() # Instantly recalculate core cash metrics
            
        except ValueError:
            messagebox.showerror("Error", "Invalid pricing values. Please write numbers only.")

    def admin_load_cost_ledger(self):
        """Fetches financial data variables with live interactive string matching filtering."""
        for item in self.admin_table.get_children():
            self.admin_table.delete(item)

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        
        try:
            # Safely fetch active search entry string input
            search_term = f"%{self.admin_search_var.get().strip().lower()}%"
            
            cursor.execute("""
                SELECT id, product_name, category, cost_price, retail_price, (retail_price - cost_price), stock_qty 
                FROM products 
                WHERE LOWER(product_name) LIKE ?
                ORDER BY id ASC
            """, (search_term,))
            
            rows = cursor.fetchall()
            for row in rows:
                display_row = (
                    row[0], row[1], row[2],
                    f"{row[3]:,} PKR", f"{row[4]:,} PKR", f"{row[5]:,} PKR", row[6]
                )
                if row[5] >= 1000:
                    self.admin_table.insert("", "end", values=display_row, tags=("high_margin",))
                else:
                    self.admin_table.insert("", "end", values=display_row)
        except Exception as e:
            print(f"Error filtering cost sheet: {e}")
        finally:
            conn.close()

    def admin_open_expenses_window(self):
        """Spawns an analytical top-level ledger window displaying chronological expense logs."""
        expense_win = ctk.CTkToplevel(self)
        expense_win.title("Durrani Sports - Store Expenses")
        expense_win.geometry("650, 480")
        expense_win.resizable(False, False)
        expense_win.grab_set() # Focus lock on popup window

        # Top Metric Analytics Plate
        summary_frame = ctk.CTkFrame(expense_win, height=50, fg_color="#1a1c23")
        summary_frame.pack(fill="x", padx=15, pady=15)
        
        lbl_summary = ctk.CTkLabel(summary_frame, text="Historical Shop Expenditures", font=("Arial", 14, "bold"))
        lbl_summary.pack(pady=10)

        # Main Table UI Canvas Grid Spreadsheet Spreadsheet
        tree_scroll = ctk.CTkScrollbar(expense_win)
        tree_scroll.pack(side="right", fill="y")

        exp_tree = ttk.Treeview(expense_win, columns=("id", "date", "desc", "amount"), show="headings", yscrollcommand=tree_scroll.set, height=14)
        tree_scroll.configure(command=exp_tree.yview)

        exp_tree.heading("id", text="Log ID")
        exp_tree.heading("date", text="Date Logged")
        exp_tree.heading("desc", text="Expenditure Notes / Reason")
        exp_tree.heading("amount", text="Payout Amount")

        exp_tree.column("id", width=60, anchor="center")
        exp_tree.column("date", width=120, anchor="center")
        exp_tree.column("desc", width=300, anchor="w")
        exp_tree.column("amount", width=130, anchor="center")
        exp_tree.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Query and load entries from SQLite
        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT id, date, description, amount FROM daily_expenses ORDER BY id DESC")
            rows = cursor.fetchall()
            
            grand_total_expenses = 0
            for row in rows:
                exp_tree.insert("", "end", values=(row[0], row[1], row[2], f"{row[3]:,} PKR"))
                grand_total_expenses += row[3]
                
            lbl_summary.configure(text=f"Grand Total Payout: {grand_total_expenses:,} PKR")
        except Exception as e:
            print(f"Error drawing expense tables: {e}")
        finally:
            conn.close()

    # ==========================================
    # CORE INTERFACE: DEVELOPER DEBUG CONSOLE
    # ==========================================
    def build_developer_view(self, parent_frame):
        self.dev_main_frame = ctk.CTkFrame(parent_frame, corner_radius=10, fg_color="#1a1c23")
        self.dev_main_frame.pack(fill="both", expand=True, pady=10)

        # Top Control Header Title
        ctk.CTkLabel(self.dev_main_frame, text="🛠️ SQL Query Terminal Sandbox & Debugger", 
                     font=("Arial", 16, "bold"), text_color="#f1c40f").pack(anchor="w", padx=20, pady=(15, 5))
        
        ctk.CTkLabel(self.dev_main_frame, text="Warning: Running destructive queries (DROP/DELETE) here directly overwrites live storage files permanently.", 
                     font=("Arial", 11, "italic"), text_color="#a0a5b5").pack(anchor="w", padx=20, pady=(0, 10))

        # Raw Command Entry Box Layout Frame
        self.dev_input_frame = ctk.CTkFrame(self.dev_main_frame, fg_color="transparent")
        self.dev_input_frame.pack(fill="x", padx=15, pady=5)

        self.txt_dev_query = ctk.CTkTextbox(self.dev_input_frame, height=80, font=("Courier New", 13), fg_color="#101116", text_color="#2ecc71")
        self.txt_dev_query.pack(side="left", fill="x", expand=True, padx=(5, 10))
        self.txt_dev_query.insert("1.0", "-- Type your raw SQL query statement here and press Execute\nSELECT * FROM products;")

        self.btn_dev_run = ctk.CTkButton(self.dev_input_frame, text="⚡ RUN\nQUERY", width=100, height=80, 
                                         font=("Arial", 12, "bold"), fg_color="#27ae60", hover_color="#218c53",
                                         command=self.dev_execute_raw_sql)
        self.btn_dev_run.pack(side="right", padx=5)

        # Quick Utility Template Helper Buttons Container
        self.dev_utils_bar = ctk.CTkFrame(self.dev_main_frame, fg_color="transparent")
        self.dev_utils_bar.pack(fill="x", padx=15, pady=5)

        ctk.CTkLabel(self.dev_utils_bar, text="Quick Macros:", font=("Arial", 11, "bold")).pack(side="left", padx=5)
        
        macros = [
            ("Show Tables", "SELECT name FROM sqlite_master WHERE type='table';"),
            ("Clear Sales Logs", "DELETE FROM sales;\nDELETE FROM sales_items;"),
            ("Clear Returns Logs", "DELETE FROM returns;"),
            ("Reset All Stock to Zero", "UPDATE products SET stock_qty = 0;")
        ]
        for name, sql in macros:
            btn = ctk.CTkButton(self.dev_utils_bar, text=name, height=22, font=("Arial", 10), fg_color="#2c3e50", hover_color="#34495e",
                                command=lambda s=sql: self.dev_inject_macro(s))
            btn.pack(side="left", padx=4)

        # Live Results Terminal Display Table Canvas
        ctk.CTkLabel(self.dev_main_frame, text="Terminal Response Grid Output:", font=("Arial", 12, "bold")).pack(anchor="w", padx=20, pady=(10, 2))
        
        self.dev_output_frame = ctk.CTkFrame(self.dev_main_frame, fg_color="#101116", corner_radius=6)
        self.dev_output_frame.pack(fill="both", expand=True, padx=20, pady=(2, 20))
        
        # Placeholder dynamic output text space to display query summary strings or errors
        self.lbl_dev_status = ctk.CTkLabel(self.dev_output_frame, text="System Ready. Write a query to execute structural inspection loops.", 
                                           font=("Courier New", 12), text_color="#a0a5b5", anchor="w", justify="left")
        self.lbl_dev_status.pack(fill="x", padx=15, pady=10)

        # Main Dynamic Grid Container Frame
        self.dev_grid_container = ctk.CTkFrame(self.dev_output_frame, fg_color="transparent")
        self.dev_grid_container.pack(fill="both", expand=True, padx=10, pady=5)
        self.dev_result_grid = None # Instantiated dynamically on successful execution

    def dev_inject_macro(self, sql_statement):
        """Clears text area and inserts macro script."""
        self.txt_dev_query.delete("1.0", "end")
        self.txt_dev_query.insert("1.0", sql_statement)

    # ==========================================
    # DEVELOPER BACKEND ACTIONS
    # ==========================================

    def dev_execute_raw_sql(self):
        """Executes raw, open SQL string inputs directly and outputs interactive data structures onto screens views."""
        raw_input_sql = self.txt_dev_query.get("1.0", "end-1c").strip()
        if not raw_input_sql: return

        # Wipe out any older rendering treeview instances to keep screen layers fresh
        if self.dev_result_grid:
            self.dev_result_grid.destroy()

        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        
        try:
            # Handle multiple query separation lines (e.g., compounding truncate commands)
            statements = [s.strip() for s in raw_input_sql.split(";") if s.strip()]
            
            last_fetch_rows = None
            columns_description = None
            affected_rows_count = 0

            for statement in statements:
                cursor.execute(statement)
                if cursor.description: # If query returns rows (like SELECT loops)
                    last_fetch_rows = cursor.fetchall()
                    columns_description = [desc[0] for desc in cursor.description]
                else:
                    affected_rows_count += cursor.rowcount
            
            conn.commit()

            # UI Update Logic Block based on result variations
            if last_fetch_rows is not None and columns_description is not None:
                self.lbl_dev_status.configure(text=f"Success: Fetched {len(last_fetch_rows)} record lines successfully.", text_color="#2ecc71")
                
                # Build a dynamic, flexible spreadsheet to match structural table layout columns out on the fly
                self.dev_result_grid = ttk.Treeview(self.dev_grid_container, columns=columns_description, show="headings")
                for col in columns_description:
                    self.dev_result_grid.heading(col, text=col)
                    self.dev_result_grid.column(col, width=100, anchor="center")
                
                for row in last_fetch_rows:
                    self.dev_result_grid.insert("", "end", values=row)
                self.dev_result_grid.pack(fill="both", expand=True)
            else:
                self.lbl_dev_status.configure(text=f"Command Success: Transaction confirmed. Row entries modified: {affected_rows_count}", text_color="#2ecc71")
            
            # Hot-refresh all surrounding UI panel components to reflect database states instantly
            self.refresh_dashboard_metrics()
            self.inv_load_data()
            self.sales_load_history()
            self.ret_load_archive()

        except Exception as query_crash_error:
            self.lbl_dev_status.configure(text=f"❌ SQL Execution Error:\n{query_crash_error}", text_color="#e74c3c")
        finally:
            conn.close()

    # ==========================================
    # HARDWARE-LOCK ACTIVATION METHODS
    # ==========================================
    def check_license_activation(self):
        """Checks if a valid activation key is saved in system_config for this machine."""
        conn = sqlite3.connect("durrani_sports.db")
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT config_value FROM system_config WHERE config_key = 'activation_key'")
            row = cursor.fetchone()
        except Exception:
            row = None
        finally:
            conn.close()

        current_hwid = get_hardware_id()
        expected_key = generate_product_key(current_hwid)

        if row and row[0] == expected_key:
            return True
        return False

    def prompt_activation_window(self):
        """Spawns an activation lock window preventing workspace access until licensed."""
        self.withdraw()  # Temporarily hides the main dashboard window

        act_win = ctk.CTkToplevel(self)
        act_win.title("Product Activation Required - Durrani Sports POS")
        act_win.geometry("520x360")
        act_win.resizable(False, False)
        act_win.grab_set()

        ctk.CTkLabel(act_win, text="🔒 Software Unregistered", font=("Arial", 18, "bold"), text_color="#e74c3c").pack(pady=(20, 5))
        ctk.CTkLabel(act_win, text="This software instance requires a valid License Key.\nSend the following HWID to the administrator for activation.", font=("Arial", 11)).pack(pady=(0, 15))

        hwid = get_hardware_id()

        # Display Machine HWID Box with Copy Button
        hw_frame = ctk.CTkFrame(act_win, fg_color="#1a1c23")
        hw_frame.pack(fill="x", padx=30, pady=10)
        
        ctk.CTkLabel(hw_frame, text="Your Machine Hardware ID (HWID):", font=("Arial", 14)).pack(anchor="w", padx=15, pady=(8, 0))
        
        # Sub-frame placing the entry field and copy button side-by-side
        hwid_input_frame = ctk.CTkFrame(hw_frame, fg_color="transparent")
        hwid_input_frame.pack(fill="x", padx=15, pady=(2, 8))

        ent_hwid = ctk.CTkEntry(hwid_input_frame, font=("Courier New", 12, "bold"), text_color="#f1c40f", height=30)
        ent_hwid.insert(0, hwid)
        ent_hwid.configure(state="readonly")
        ent_hwid.pack(side="left", fill="x", expand=True, padx=(0, 5))

        def copy_hwid_to_clipboard():
            act_win.clipboard_clear()
            act_win.clipboard_append(hwid)
            act_win.update()
            btn_copy.configure(text="✓ Copied!", fg_color="#27ae60")
            act_win.after(2000, lambda: btn_copy.configure(text="📋 Copy", fg_color="#2b2d3a"))

        btn_copy = ctk.CTkButton(hwid_input_frame, text="📋 Copy", width=75, height=30, 
                                 font=("Arial", 11, "bold"), fg_color="#2b2d3a", hover_color="#3e4154", 
                                 command=copy_hwid_to_clipboard)
        btn_copy.pack(side="right")

        # License Input Entry
        ctk.CTkLabel(act_win, text="Enter Provided Product Key:", font=("Arial", 11, "bold")).pack(anchor="w", padx=30, pady=(10, 2))
        ent_key = ctk.CTkEntry(act_win, placeholder_text="e.g. SS-XXXX-XXXX-XXXX", font=("Courier New", 12), height=35)
        ent_key.pack(fill="x", padx=30, pady=2)

        def verify_and_activate():
            input_key = ent_key.get().strip()
            expected_key = generate_product_key(hwid)

            if input_key == expected_key:
                conn = sqlite3.connect("durrani_sports.db")
                cursor = conn.cursor()
                cursor.execute("INSERT OR REPLACE INTO system_config (config_key, config_value) VALUES ('activation_key', ?)", (input_key,))
                conn.commit()
                conn.close()

                messagebox.showinfo("Activation Successful", "Software activated successfully for this machine!")
                act_win.destroy()
                self.deiconify()  # Reveals the main app workspace
            else:
                messagebox.showerror("Activation Failed", "Invalid Product Key for this specific Machine Hardware ID!")

        btn_activate = ctk.CTkButton(act_win, text="⚡ ACTIVATE SOFTWARE", fg_color="#27ae60", hover_color="#218c53", height=38, font=("Arial", 12, "bold"), command=verify_and_activate)
        btn_activate.pack(fill="x", padx=30, pady=20)

        # Force app termination if user closes the popup without entering a valid key
        act_win.protocol("WM_DELETE_WINDOW", self.quit)

    def safely_terminate_application(self):
        """Clears all running background thread handlers before closing down Python cleanly."""
        try:
            # Wipes Matplotlib rendering engines completely out of memory trees
            plt.close('all')
        except:
            pass
        
        # Stops internal CustomTkinter loops before quitting the application safely
        self.quit()
        self.destroy()

if __name__ == "__main__":
    app = DurraniSportsApp()
    app.mainloop()