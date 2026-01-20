import sqlite3
from sqlite3 import Error

def create_connection():
    """Create a connection to the SQLite database."""
    conn = None
    try:
        conn = sqlite3.connect('clothes.db')
        print("Successfully connected to SQLite database")
        return conn
    except Error as e:
        print(f"Error connecting to SQLite: {e}")
    return conn

def create_tables(conn):
    """Create the database tables for the Clothes Management System."""
    try:
        cursor = conn.cursor()

        # Creating the Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Users (
                user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(255) NOT NULL,
                email VARCHAR(100) UNIQUE NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                role TEXT CHECK(role IN ('admin', 'user')) NOT NULL DEFAULT 'user',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')

        # Creating the Categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Categories (
                category_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_name VARCHAR(50) NOT NULL UNIQUE
            )
        ''')

        # Creating the ClothItems table with season field
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ClothItems (
                item_id INTEGER PRIMARY KEY AUTOINCREMENT,
                category_id INTEGER NOT NULL,
                item_name VARCHAR(100) NOT NULL,
                description TEXT,
                unit_price DECIMAL(10, 2) NOT NULL,
                sale_price DECIMAL(10, 2) NOT NULL,
                stock_quantity INTEGER NOT NULL DEFAULT 0,
                season TEXT CHECK(season IN ('Spring','Summer','Autumn','Winter')) NOT NULL,
                item_image TEXT,
                FOREIGN KEY (category_id) REFERENCES Categories(category_id) ON DELETE RESTRICT
            )
        ''')

        # Creating the Sales table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Sales (
                sale_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                quantity_sold INTEGER NOT NULL,
                sale_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_amount DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (item_id) REFERENCES ClothItems(item_id) ON DELETE RESTRICT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE RESTRICT
            )
        ''')

        # Creating the Purchases table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Purchases (
                purchase_id INTEGER PRIMARY KEY AUTOINCREMENT,
                item_id INTEGER NOT NULL,
                user_id INTEGER NOT NULL,
                quantity_purchased INTEGER NOT NULL,
                purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                total_cost DECIMAL(10, 2) NOT NULL,
                FOREIGN KEY (item_id) REFERENCES ClothItems(item_id) ON DELETE RESTRICT,
                FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE RESTRICT
            )
        ''')

        # Creating indexes for performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_item_name ON ClothItems(item_name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sale_date ON Sales(sale_date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_purchase_date ON Purchases(purchase_date)')

        # Inserting admin user
        cursor.execute('''
            INSERT OR IGNORE INTO Users (username, password, email, full_name, role)
            VALUES (?, ?, ?, ?, ?)
        ''', ('admin', 'admin', 'admin@clothes.com', 'Admin User', 'admin'))

        conn.commit()
        print("Tables created and admin user inserted successfully")

    except Error as e:
        print(f"Error creating tables or inserting admin user: {e}")

def main():
    # Create database connection and tables
    conn = create_connection()
    if conn is not None:
        create_tables(conn)
        conn.close()
        print("Database connection closed")
    else:
        print("Cannot create database connection")

if __name__ == '__main__':
    main()
