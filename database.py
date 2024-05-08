import sqlite3
import error_logger

DATABASE_FILE = "motobdb.db"

class DatabaseConnection:
    def __enter__(self):
        self.conn = sqlite3.connect(DATABASE_FILE)
        self.cursor = self.conn.cursor()
        return self.conn, self.cursor

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            error_logger.log_error(exc_val)
        self.cursor.close()
        self.conn.close()

def connect_to_database():
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()
    return conn, cursor

def close_connection(conn, cursor):
    cursor.close()
    conn.close()


def initialize_database():
    conn = None
    cursor = None
    try:
        with DatabaseConnection() as (conn, cursor):
            # Create tables if they don't exist
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            stock INT NOT NULL,
            sold_stock INT DEFAULT 0,
            available_stock INT NOT NULL
                )
            """)

            cursor.execute('''CREATE TABLE IF NOT EXISTS purchases (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date TEXT NOT NULL,
                    item_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    total_price REAL NOT NULL
                )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS sales (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    item_name TEXT NOT NULL,
                    date TEXT NOT NULL,
                    customer_name TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price REAL NOT NULL
                )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS debtors (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    item TEXT NOT NULL,
                    date TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    unit_price INT NOT NULL,
                    total REAL NOT NULL
                )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS debts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    creditor TEXT,
                    date TEXT,
                    goods_purchased TEXT,
                    quantity INTEGER,
                    unit_price REAL,
                    total REAL
                )''')

            cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL,
                has_permissions INTEGER NOT NULL DEFAULT 0
                )''')

            cursor.execute("""
                CREATE TABLE IF NOT EXISTS activity_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    username TEXT NOT NULL,
                    action TEXT NOT NULL
                )""")

    except Exception as e:
        error_logger.log_error(e)

def add_product(name, stock, sold_stock):
    try:
        conn, cursor = connect_to_database()

        available_stock = stock - sold_stock

        cursor.execute("""
            INSERT INTO products (name, stock, sold_stock, available_stock)
            VALUES (?, ?, ?, ?)
        """, (name, stock, sold_stock, available_stock))
        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def product_exists(name):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT COUNT(*) FROM products WHERE name=?", (name,))
        count = cursor.fetchone()[0]

    except Exception as e:
        error_logger.log_error(e)
        count = 0

    finally:
        close_connection(conn, cursor)

    return count > 0

def update_product(product_id, new_name, new_stock, new_sold_stock):
    try:
        conn, cursor = connect_to_database()

        new_available_stock = new_stock - new_sold_stock

        cursor.execute("""
            UPDATE products
            SET name=?, stock=?, sold_stock=?, available_stock=?
            WHERE id=?
        """, (new_name, new_stock, new_sold_stock, new_available_stock, product_id))
        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def delete_product(product_id):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
        conn.commit()

    except sqlite3.Error as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def get_product_id(name):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT id FROM products WHERE name=?", (name,))
        product_id = cursor.fetchone()

    except Exception as e:
        error_logger.log_error(e)
        product_id = None

    finally:
        close_connection(conn, cursor)

    return product_id[0] if product_id else None

def get_all_products():
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT * FROM products")
        products = cursor.fetchall()

    except Exception as e:
        error_logger.log_error(e)
        products = []

    finally:
        close_connection(conn, cursor)

    return products

def add_purchase(item_name, date, quantity, unit_price):
    try:
        total_price = quantity * unit_price  # Calculate total price
        conn, cursor = connect_to_database()

        cursor.execute("""
            INSERT INTO purchases (date, item_name, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?)
        """, (date, item_name, quantity, unit_price, total_price))

        conn.commit()

        # Update available stock
        #cursor.execute("""
        #    UPDATE products
        #    SET available_stock = available_stock + ?
        #    WHERE id = ?
        #""", (quantity, product_id))
        #conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def purchase_exists(date, item_name, quantity, unit_price):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("""
            SELECT COUNT(*)
            FROM purchases
            WHERE date = ? AND item_name = ? AND quantity = ? AND unit_price = ?
        """, (date, item_name, quantity, unit_price))
        count = cursor.fetchone()[0]

    except Exception as e:
        error_logger.log_error(e)
        count = 0

    finally:
        close_connection(conn, cursor)

    return count > 0

def edit_purchase(purchase_id, date, item_name, quantity, unit_price, total_price):
    try:
        #total_price = quantity * unit_price  # Calculate total price
        conn, cursor = connect_to_database()

        cursor.execute("""
            UPDATE purchases
            SET date=?, item_name=?,  quantity=?, unit_price=?, total_price=?
            WHERE id=?
        """, (date, item_name, quantity, unit_price, total_price, purchase_id))

        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def delete_purchase(purchase_id):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("DELETE FROM purchases WHERE id=?", (purchase_id,))
        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def get_purchase_by_id(purchase_id):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT id, date, item_name, quantity, unit_price FROM purchases WHERE id = ?", (purchase_id,))
        purchase_details = cursor.fetchone()

    except Exception as e:
        error_logger.log_error(e)
        purchase_details = None

    finally:
        close_connection(conn, cursor)

    return purchase_details

def get_all_purchases():
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT id, date, item_name, quantity, unit_price FROM purchases")
        purchases = cursor.fetchall()

        # Calculate total for each purchase
        for i, purchase in enumerate(purchases):
            quantity = purchase[3]
            unit_price = purchase[4]
            total = quantity * unit_price
            purchases[i] = purchase + (total,)  # Append total to the purchase tuple

    except Exception as e:
        error_logger.log_error(e)
        purchases = []

    finally:
        close_connection(conn, cursor)

    return purchases

def add_sale(item_name, date, customer_name, quantity, unit_price):
    try:
        total_price = quantity * unit_price  # Calculate total price
        conn, cursor = connect_to_database()

        cursor.execute("""
            INSERT INTO sales (item_name, date, customer_name, quantity, unit_price, total_price)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (item_name, date, customer_name, quantity, unit_price, total_price))
        conn.commit()

        # Update available stock
        cursor.execute("""
            UPDATE products
            SET available_stock = available_stock - ?
            WHERE name = ?
        """, (quantity, item_name))
        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def sale_exists(product_id, date, customer_name, quantity, unit_price):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("""
            SELECT COUNT(*)
            FROM sales
            WHERE product_id = ? AND date = ? AND customer_name = ? AND quantity = ? AND unit_price = ?
        """, (product_id, date, customer_name, quantity, unit_price))
        count = cursor.fetchone()[0]

    except Exception as e:
        error_logger.log_error(e)
        count = 0

    finally:
        close_connection(conn, cursor)

    return count > 0

def edit_sale(sale_id, date, customer_name, item_name, quantity, unit_price):
    try:
        total_price = quantity * unit_price  # Calculate total price
        conn, cursor = connect_to_database()

        cursor.execute("""
            UPDATE sales
            SET date=?, customer_name=?, item_name=?, quantity=?, unit_price=?, total_price=?
            WHERE id=?
        """, (date, customer_name, item_name, quantity, unit_price, total_price, sale_id))
        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def delete_sale(sale_id):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("DELETE FROM sales WHERE id=?", (sale_id,))
        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def get_sale_by_id(sale_id):
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT date, item_name, customer_name, quantity, unit_price, total_price FROM sales WHERE id = ?", (sale_id,))
        sale_details = cursor.fetchone()

    except Exception as e:
        error_logger.log_error(e)
        sale_details = None

    finally:
        close_connection(conn, cursor)

    return sale_details

def get_all_sales():
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT * FROM sales")
        sales = cursor.fetchall()

    except Exception as e:
        error_logger.log_error(e)
        sales = []

    finally:
        close_connection(conn, cursor)

    return sales

def get_all_sales():
    try:
        conn, cursor = connect_to_database()

        cursor.execute("SELECT * FROM sales")
        sales = cursor.fetchall()

    except Exception as e:
        error_logger.log_error(e)
        sales = []

    finally:
        close_connection(conn, cursor)

    return sales

def calculate_profit_loss():
    try:
        conn, cursor = connect_to_database()

        cursor.execute("""
            SELECT 
                (SELECT SUM(quantity * unit_price) FROM sales) - 
                (SELECT SUM(quantity * unit_price) FROM purchases)
        """)
        result = cursor.fetchone()[0] or 0

    except Exception as e:
        error_logger.log_error(e)
        result = 0

    finally:
        close_connection(conn, cursor)

    return result

def add_debtor(name, item, date, quantity, unit_price):
    try:
        conn, cursor = connect_to_database()

        # Check if debtor already exists
        if debtor_exists(name, item, date, quantity, unit_price):
            print("Debtor already exists.")  # You can log this message or handle it as needed
            return

        total = quantity * unit_price  # Calculate the total
        cursor.execute('''INSERT INTO debtors (name, item, date, quantity, unit_price, total) VALUES (?, ?, ?, ?, ?, ?)''', (name, item, date, quantity, unit_price, total))
        conn.commit()
        print("Debtor added successfully.")

    except Exception as e:
        print("Error adding debtor:", e)
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

# Add a new function to check if a debtor already exists
def debtor_exists(name, item, date, quantity, unit_price):
    try:
        conn, cursor = connect_to_database()
        cursor.execute("SELECT COUNT(*) FROM debtors WHERE name=? AND item=? AND date=? AND quantity=? AND unit_price=?", (name, item, date, quantity, unit_price))
        count = cursor.fetchone()[0]
        return count > 0
    except Exception as e:
        error_logger.log_error(e)
        return False
    finally:
        close_connection(conn, cursor)

def update_debtor(debtor_id, name, item, date, quantity, unit_price):
    try:
        total = quantity * unit_price  # Calculate the total
        conn, cursor = connect_to_database()

        cursor.execute('''UPDATE debtors SET name=?, item=?, date=?, quantity=?, unit_price=?, total=? WHERE id=?''', (name, item, date, quantity, unit_price, total, debtor_id))
        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def delete_debtor(debtor_id):
    try:
        conn, cursor = connect_to_database()
        cursor.execute('''DELETE FROM debtors WHERE id=?''', (debtor_id,))
        conn.commit()
    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def get_all_debtors():
    try:
        conn, cursor = connect_to_database()
        cursor.execute('''SELECT * FROM debtors''')
        return cursor.fetchall()
    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def add_debt(creditor, date, goods_purchased, quantity, unit_price):
    try:
        total = quantity * unit_price  # Calculate the total
        conn, cursor = connect_to_database()

        cursor.execute('''INSERT INTO debts (creditor, date, goods_purchased, quantity, unit_price, total) VALUES (?, ?, ?, ?, ?, ?)''', (creditor, date, goods_purchased, quantity, unit_price, total))
        conn.commit()

    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def update_debt(debt_id, creditor, date, goods_purchased, quantity, unit_price, total):
    try:
        conn, cursor = connect_to_database()
        cursor.execute('''UPDATE debts SET creditor=?, date=?, goods_purchased=?, quantity=?, unit_price=?, total=? WHERE id=?''', (creditor, date, goods_purchased, quantity, unit_price, total, debt_id))
        conn.commit()
    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def delete_debt(debt_id):
    try:
        conn, cursor = connect_to_database()
        cursor.execute('''DELETE FROM debts WHERE id=?''', (debt_id,))
        conn.commit()
    except Exception as e:
        error_logger.log_error(e)

    finally:
        close_connection(conn, cursor)

def get_all_debts():
    try:
        conn, cursor = connect_to_database()
        cursor.execute('''SELECT * FROM debts''')
        return cursor.fetchall()
    except Exception as e:
        error_logger.log_error(e)
        raise  # Re-raise the exception so it can be handled by the caller
    finally:
        close_connection(conn, cursor)

def add_user(username, password, is_admin=False):
    try:
        conn, cursor = connect_to_database()
        # Convert is_admin to an integer (0 or 1) before inserting into the database
        cursor.execute("INSERT INTO users (username, password, is_admin) VALUES (?, ?, ?)", (username, password, int(is_admin)))
        conn.commit()
    except Exception as e:
        error_logger.log_error(e)
    finally:
        close_connection(conn, cursor)

def delete_user(username):
    try:
        conn, cursor = connect_to_database()
        cursor.execute("DELETE FROM users WHERE username=?", (username,))
        conn.commit()
    except Exception as e:
        error_logger.log_error(e)
    finally:
        close_connection(conn, cursor)

def get_user(username):
    try:
        conn, cursor = connect_to_database()
        cursor.execute("SELECT * FROM users WHERE username=?", (username,))
        return cursor.fetchone()
    except Exception as e:
        error_logger.log_error(e)
    finally:
        close_connection(conn, cursor)

def log_activity(username, action):
    try:
        conn, cursor = connect_to_database()
        cursor.execute("INSERT INTO activity_logs (username, action) VALUES (?, ?)", (username, action))
        conn.commit()
    except Exception as e:
        error_logger.log_error(e)
    finally:
        close_connection(conn, cursor)

def get_all_users():
    try:
        conn, cursor = connect_to_database()
        cursor.execute("SELECT * FROM users")
        users = cursor.fetchall()
        print("Users fetched successfully:", users)  # Add this line for debugging
        return users
    except Exception as e:
        error_logger.log_error(e)
        return []
    finally:
        close_connection(conn, cursor)

def get_all_users_with_permissions():
    try:
        conn, cursor = connect_to_database()
        cursor.execute("SELECT username, is_admin, has_permissions FROM users")
        return cursor.fetchall()
    except Exception as e:
        error_logger.log_error(e)
    finally:
        close_connection(conn, cursor)

def grant_permissions(username):
    try:
        conn, cursor = connect_to_database()
        cursor.execute("UPDATE users SET has_permissions=1 WHERE username=?", (username,))
        conn.commit()
    except Exception as e:
        error_logger.log_error(e)
    finally:
        close_connection(conn, cursor)

def revoke_permissions(username):
    try:
        conn, cursor = connect_to_database()
        cursor.execute("UPDATE users SET has_permissions=0 WHERE username=?", (username,))
        conn.commit()
    except Exception as e:
        error_logger.log_error(e)
    finally:
        close_connection(conn, cursor)
