# database.py
import sqlite3
import os
from datetime import datetime

DATABASE_FILE = "demoga_emaldo.db"

def connect_db():
    db_path = os.path.join(os.path.dirname(__file__), DATABASE_FILE)
    conn = sqlite3.connect(db_path)
    return conn

def create_tables():
    conn = connect_db(); cursor = conn.cursor()
    # ... (El código de create_tables no cambia, se mantiene igual)
    cursor.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, full_name TEXT NOT NULL, email TEXT NOT NULL UNIQUE, password TEXT NOT NULL, role TEXT NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS products (code TEXT PRIMARY KEY, name TEXT NOT NULL, description TEXT, category TEXT, supplier TEXT, stock INTEGER NOT NULL, sale_price REAL NOT NULL, cost_price REAL NOT NULL);")
    cursor.execute("CREATE TABLE IF NOT EXISTS sales (id INTEGER PRIMARY KEY AUTOINCREMENT, invoice_number TEXT NOT NULL UNIQUE, product_code TEXT NOT NULL, quantity_sold INTEGER NOT NULL, total_price REAL NOT NULL, customer_name TEXT, seller_name TEXT, sale_date TEXT NOT NULL, FOREIGN KEY (product_code) REFERENCES products (code));")
    cursor.execute("CREATE TABLE IF NOT EXISTS purchases (id INTEGER PRIMARY KEY AUTOINCREMENT, po_number TEXT NOT NULL UNIQUE, product_code TEXT NOT NULL, quantity_received INTEGER NOT NULL, supplier_name TEXT, purchase_date TEXT NOT NULL, status TEXT NOT NULL, FOREIGN KEY (product_code) REFERENCES products (code));")
    cursor.execute("CREATE TABLE IF NOT EXISTS customers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT, phone TEXT, address TEXT, razon_social TEXT, tipo_pago TEXT, uso_cfdi TEXT, payment_terms INTEGER DEFAULT 0);")
    cursor.execute("CREATE TABLE IF NOT EXISTS suppliers (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, contact_person TEXT, email TEXT, phone TEXT, address TEXT, razon_social TEXT, tipo_pago TEXT, uso_cfdi TEXT, payment_terms INTEGER DEFAULT 0);")
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS customer_orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER NOT NULL, product_code TEXT NOT NULL,
        quantity_ordered INTEGER NOT NULL, entry_date TEXT NOT NULL, required_date TEXT NOT NULL,
        status TEXT NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES customers (id),
        FOREIGN KEY (product_code) REFERENCES products (code)
    );
    """)
    conn.commit(); conn.close()

# --- Funciones (Se omiten las que no cambian por brevedad) ---
def get_all_users():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT full_name, email, role FROM users"); users = cursor.fetchall(); conn.close(); return users
def add_user(full_name, email, password, role):
    conn = connect_db(); cursor = conn.cursor()
    try: cursor.execute("INSERT INTO users (full_name, email, password, role) VALUES (?, ?, ?, ?)", (full_name, email, password, role)); conn.commit(); return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()
def check_user_credentials(email, password):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT role FROM users WHERE email = ? AND password = ?", (email, password)); user = cursor.fetchone(); conn.close(); return user[0] if user else None
def delete_user(email):
    conn = connect_db(); cursor = conn.cursor()
    if email == 'admin': conn.close(); return False
    cursor.execute("DELETE FROM users WHERE email = ?", (email,)); conn.commit(); success = cursor.rowcount > 0; conn.close(); return success
def get_user_by_email(email):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT full_name, email, role FROM users WHERE email = ?", (email,)); user = cursor.fetchone(); conn.close(); return user
def update_user(original_email, full_name, new_email, role):
    conn = connect_db(); cursor = conn.cursor()
    try: cursor.execute("UPDATE users SET full_name = ?, email = ?, role = ? WHERE email = ?", (full_name, new_email, role, original_email)); conn.commit(); return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()
def update_user_password(email, new_password):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("UPDATE users SET password = ? WHERE email = ?", (new_password, email)); conn.commit(); conn.close()
def get_all_products():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT code, name, description, category, supplier, stock, sale_price, cost_price FROM products"); products = cursor.fetchall(); conn.close(); return products
def update_product(code, name, description, category, supplier, sale_price, cost_price):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("UPDATE products SET name = ?, description = ?, category = ?, supplier = ?, sale_price = ?, cost_price = ? WHERE code = ?", (name, description, category, supplier, sale_price, cost_price, code)); conn.commit(); conn.close()
def add_product(code, name, description, category, supplier, stock, sale_price, cost_price):
    conn = connect_db(); cursor = conn.cursor()
    try: cursor.execute("INSERT INTO products (code, name, description, category, supplier, stock, sale_price, cost_price) VALUES (?,?,?,?,?,?,?,?)", (code, name, description, category, supplier, stock, sale_price, cost_price)); conn.commit(); return True
    except sqlite3.IntegrityError: return False
    finally: conn.close()
def delete_product(code):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("DELETE FROM products WHERE code = ?", (code,)); conn.commit(); success = cursor.rowcount > 0; conn.close(); return success
def get_sales_history():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT s.sale_date, s.invoice_number, p.name, p.category, s.customer_name, s.total_price, s.seller_name FROM sales s JOIN products p ON s.product_code = p.code ORDER BY s.sale_date DESC"); sales = cursor.fetchall(); conn.close(); return sales
def register_sale(product_code, quantity, customer_name, seller_name):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT stock, sale_price FROM products WHERE code = ?", (product_code,)); product = cursor.fetchone()
    if not product: conn.close(); return "Producto no encontrado."
    current_stock, sale_price = product
    if quantity > current_stock: conn.close(); return f"Stock insuficiente. Solo hay {current_stock}."
    new_stock = current_stock - quantity; total_price = quantity * sale_price
    cursor.execute("UPDATE products SET stock = ? WHERE code = ?", (new_stock, product_code))
    sale_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); invoice_number = f"INV-{int(datetime.now().timestamp())}"
    cursor.execute("INSERT INTO sales (invoice_number, product_code, quantity_sold, total_price, customer_name, seller_name, sale_date) VALUES (?, ?, ?, ?, ?, ?, ?)", (invoice_number, product_code, quantity, total_price, customer_name, seller_name, sale_date))
    conn.commit(); conn.close(); return "Venta registrada con éxito."
def delete_sale(invoice_number):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT product_code, quantity_sold FROM sales WHERE invoice_number = ?", (invoice_number,)); sale_details = cursor.fetchone()
    if not sale_details: conn.close(); return False
    product_code, quantity_sold = sale_details
    cursor.execute("UPDATE products SET stock = stock + ? WHERE code = ?", (quantity_sold, product_code))
    cursor.execute("DELETE FROM sales WHERE invoice_number = ?", (invoice_number,)); conn.commit(); conn.close(); return True
def get_sale_by_invoice(invoice_number):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT customer_name, seller_name FROM sales WHERE invoice_number = ?", (invoice_number,)); sale = cursor.fetchone(); conn.close(); return sale
def update_sale(invoice_number, customer_name, seller_name):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("UPDATE sales SET customer_name = ?, seller_name = ? WHERE invoice_number = ?", (customer_name, seller_name, invoice_number)); conn.commit(); conn.close()
def get_all_customers():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT id, name, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms FROM customers"); return cursor.fetchall()
def add_customer(name, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("INSERT INTO customers (name, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (name, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms)); conn.commit(); conn.close()
def update_customer(customer_id, name, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("UPDATE customers SET name = ?, email = ?, phone = ?, address = ?, razon_social = ?, tipo_pago = ?, uso_cfdi = ?, payment_terms = ? WHERE id = ?", (name, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms, customer_id)); conn.commit(); conn.close()
def delete_customer(customer_id):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("DELETE FROM customers WHERE id = ?", (customer_id,)); conn.commit(); conn.close()
def get_all_suppliers():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT id, name, contact_person, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms FROM suppliers"); return cursor.fetchall()
def add_supplier(name, contact_person, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("INSERT INTO suppliers (name, contact_person, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)", (name, contact_person, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms)); conn.commit(); conn.close()
def update_supplier(supplier_id, name, contact_person, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("UPDATE suppliers SET name = ?, contact_person = ?, email = ?, phone = ?, address = ?, razon_social = ?, tipo_pago = ?, uso_cfdi = ?, payment_terms = ? WHERE id = ?", (name, contact_person, email, phone, address, razon_social, tipo_pago, uso_cfdi, payment_terms, supplier_id)); conn.commit(); conn.close()
def delete_supplier(supplier_id):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("DELETE FROM suppliers WHERE id = ?", (supplier_id,)); conn.commit(); conn.close()
def get_purchase_history():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT pu.purchase_date, pu.po_number, p.name, pu.supplier_name, pu.quantity_received, pu.status FROM purchases pu JOIN products p ON pu.product_code = p.code ORDER BY pu.purchase_date DESC"); purchases = cursor.fetchall(); conn.close(); return purchases
def register_purchase(product_code, quantity, supplier_name):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT stock FROM products WHERE code = ?", (product_code,)); product = cursor.fetchone()
    if not product: conn.close(); return "Producto no encontrado."
    new_stock = product[0] + quantity
    cursor.execute("UPDATE products SET stock = ? WHERE code = ?", (new_stock, product_code))
    purchase_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S"); po_number = f"PO-{int(datetime.now().timestamp())}"
    cursor.execute("INSERT INTO purchases (po_number, product_code, quantity_received, supplier_name, purchase_date, status) VALUES (?, ?, ?, ?, ?, ?)", (po_number, product_code, quantity, supplier_name, purchase_date, "Recibido"))
    conn.commit(); conn.close(); return "Compra registrada y stock actualizado con éxito."
def delete_purchase(po_number):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT product_code, quantity_received FROM purchases WHERE po_number = ?", (po_number,)); purchase_details = cursor.fetchone()
    if not purchase_details: conn.close(); return "Orden de compra no encontrada."
    product_code, quantity_received = purchase_details
    cursor.execute("SELECT stock FROM products WHERE code = ?", (product_code,)); product_stock = cursor.fetchone()[0]
    if quantity_received > product_stock: conn.close(); return f"No se puede anular. Stock actual ({product_stock}) es menor a la cantidad recibida ({quantity_received})."
    cursor.execute("UPDATE products SET stock = stock - ? WHERE code = ?", (quantity_received, product_code))
    cursor.execute("DELETE FROM purchases WHERE po_number = ?", (po_number,)); conn.commit(); conn.close()
    return "Compra eliminada y stock descontado con éxito."
def get_purchase_by_po(po_number):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT supplier_name, status FROM purchases WHERE po_number = ?", (po_number,)); purchase = cursor.fetchone(); conn.close(); return purchase
def update_purchase(po_number, supplier_name, status):
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("UPDATE purchases SET supplier_name = ?, status = ? WHERE po_number = ?", (supplier_name, status, po_number)); conn.commit(); conn.close()
def get_dashboard_kpis():
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT SUM(total_price) FROM sales WHERE strftime('%Y-%m', sale_date) = strftime('%Y-%m', 'now')"); monthly_sales = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT SUM(stock * cost_price) FROM products"); inventory_value = cursor.fetchone()[0] or 0.0
    cursor.execute("SELECT COUNT(*) FROM purchases"); pending_orders = cursor.fetchone()[0] or 0
    conn.close(); return {"ventas_mes": monthly_sales, "valor_inventario": inventory_value, "ordenes_pendientes": pending_orders}
def get_sales_by_customer():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT customer_name, SUM(total_price) as total FROM sales GROUP BY customer_name ORDER BY total DESC LIMIT 5"); data = cursor.fetchall(); conn.close(); return data
def get_monthly_sales_summary():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT strftime('%Y-%m', sale_date) as month, SUM(total_price) FROM sales GROUP BY month ORDER BY month ASC LIMIT 12"); data = cursor.fetchall(); conn.close(); return data
def get_top_selling_products():
    conn = connect_db(); cursor = conn.cursor(); cursor.execute("SELECT p.code, p.name, SUM(s.quantity_sold) as total_quantity FROM sales s JOIN products p ON s.product_code = p.code GROUP BY p.code, p.name ORDER BY total_quantity DESC LIMIT 10"); data = cursor.fetchall(); conn.close(); return data
def get_filtered_sales_report(start_date=None, end_date=None, customer_name=None):
    conn = connect_db(); cursor = conn.cursor()
    query = "SELECT s.sale_date, s.invoice_number, p.code, p.name, s.quantity_sold, p.sale_price, p.cost_price, s.customer_name FROM sales s JOIN products p ON s.product_code = p.code WHERE 1=1"
    params = []
    if start_date: query += " AND date(s.sale_date) >= ?"; params.append(start_date)
    if end_date: query += " AND date(s.sale_date) <= ?"; params.append(end_date)
    if customer_name and customer_name != "Todos": query += " AND s.customer_name = ?"; params.append(customer_name)
    query += " ORDER BY s.sale_date DESC"
    cursor.execute(query, params); report_data = cursor.fetchall(); conn.close(); return report_data
def add_customer_order(customer_id, product_code, quantity, required_date):
    conn = connect_db(); cursor = conn.cursor()
    entry_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("INSERT INTO customer_orders (customer_id, product_code, quantity_ordered, entry_date, required_date, status) VALUES (?, ?, ?, ?, ?, ?)",
                   (customer_id, product_code, quantity, entry_date, required_date, "Pendiente"))
    conn.commit(); conn.close()
def get_all_customer_orders():
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("""
        SELECT co.id, c.name, co.entry_date, co.required_date, p.code, p.description, p.sale_price, co.quantity_ordered, co.status
        FROM customer_orders co
        JOIN customers c ON co.customer_id = c.id
        JOIN products p ON co.product_code = p.code
        ORDER BY co.entry_date DESC
    """)
    return cursor.fetchall()
def delete_customer_order(order_id):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("DELETE FROM customer_orders WHERE id = ?", (order_id,)); conn.commit(); conn.close()

# --- NUEVAS FUNCIONES ---
def get_customer_order_by_id(order_id):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("SELECT customer_id, product_code, quantity_ordered FROM customer_orders WHERE id = ?", (order_id,))
    return cursor.fetchone()

def update_customer_order_status(order_id, new_status):
    conn = connect_db(); cursor = conn.cursor()
    cursor.execute("UPDATE customer_orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit(); conn.close()

# --- Inicializar la base de datos al importar ---
create_tables()
