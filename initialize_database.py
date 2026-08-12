import sqlite3

def build_pos_database():
    conn = sqlite3.connect("durrani_sports.db")
    cursor = conn.cursor()
    
    print("Initializing Durrani Sports Relational Database...")

    # 1. Core Products Inventory Table (With Cost Price tracking)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            product_name TEXT NOT NULL,
            category TEXT,
            cost_price INTEGER NOT NULL,
            retail_price INTEGER NOT NULL,
            stock_qty INTEGER NOT NULL
        )
    ''')

    # 2. Master Sales Invoices Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales (
            invoice_id TEXT PRIMARY KEY,
            customer_name TEXT,
            ph_number TEXT,
            date_time TEXT NOT NULL,
            subtotal INTEGER NOT NULL,
            discount_amount INTEGER NOT NULL,
            amount_collected INTEGER NOT NULL
        )
    ''')

    # 3. Itemized Invoice Content Breakdown Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sales_items (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            quantity INTEGER NOT NULL,
            sold_price INTEGER NOT NULL,
            FOREIGN KEY (invoice_id) REFERENCES sales (invoice_id),
            FOREIGN KEY (product_id) REFERENCES products (id)
        )
    ''')

    # 4. Independent Returns Registry Table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS returns (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            invoice_id TEXT NOT NULL,
            product_id INTEGER NOT NULL,
            product_name TEXT NOT NULL,
            returned_qty INTEGER NOT NULL,
            refund_amount INTEGER NOT NULL,
            date_time TEXT NOT NULL,
            reason TEXT
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS daily_expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            description TEXT NOT NULL,
            amount INTEGER NOT NULL
        )
    ''')

    # 1. Create a table to permanently hold system configurations like the PIN
    cursor.execute('''
            CREATE TABLE IF NOT EXISTS system_config (
                config_key TEXT PRIMARY KEY,
                config_value TEXT NOT NULL
            )
        ''')

    cursor.execute("INSERT OR IGNORE INTO system_config (config_key, config_value) VALUES ('admin_pin', '1234')")

    cursor.execute('''
            CREATE TABLE IF NOT EXISTS pin_change_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                change_date TEXT NOT NULL,
                old_pin_masked TEXT NOT NULL,
                new_pin_masked TEXT NOT NULL
            )
        ''')
        

    conn.commit()
    conn.close()
    print("Database infrastructure 'durrani_sports.db' built successfully!")

if __name__ == "__main__":
    build_pos_database()




