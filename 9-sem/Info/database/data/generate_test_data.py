#!/usr/bin/env python3
"""
TechMarket Test Data Generator
Генерує тестові дані для всіх баз даних системи:
- Auth DB: користувачі, ролі, токени
- Catalog DB: категорії, товари
- Orders DB: регіони, клієнти, менеджери, замовлення
- Payments DB: платежі
- DWH: не наповнюється тут (ETL процес)

Вимоги:
- менеджерів: 5+
- покупців: 20+
- товарів: 20+
- продажі: 500+
"""

import uuid
import random
import hashlib
from datetime import datetime, timedelta
from typing import List, Dict
from decimal import Decimal
import mysql.connector
import psycopg2
from faker import Faker

fake = Faker(['uk_UA', 'en_US'])
Faker.seed(42)
random.seed(42)

# ============================================
# Database Connections Configuration
# ============================================

DB_CONFIGS = {
    'auth': {
        'host': 'localhost',
        'port': 3306,
        'user': 'auth_user',
        'password': 'auth_pass',
        'database': 'auth_db'
    },
    'catalog': {
        'host': 'localhost',
        'port': 3307,
        'user': 'catalog_user',
        'password': 'catalog_pass',
        'database': 'catalog_db'
    },
    'orders': {
        'host': 'localhost',
        'port': 3308,
        'user': 'orders_user',
        'password': 'orders_pass',
        'database': 'orders_db'
    },
    'payments': {
        'host': 'localhost',
        'port': 3309,
        'user': 'payments_user',
        'password': 'payments_pass',
        'database': 'payments_db'
    }
}

# ============================================
# Helper Functions
# ============================================

def generate_uuid() -> str:
    """Генерує UUID як строку"""
    return str(uuid.uuid4())

def hash_password(password: str) -> str:
    """Створює простий хеш пароля"""
    return hashlib.sha256(password.encode()).hexdigest()

def random_date(start_date: datetime, end_date: datetime) -> datetime:
    """Генерує випадкову дату між двома датами"""
    delta = end_date - start_date
    random_days = random.randint(0, delta.days)
    return start_date + timedelta(days=random_days)

# ============================================
# Auth Database Population
# ============================================

def populate_auth_db(customer_ids: List[str], employee_ids: List[str]):
    """Наповнює Auth DB користувачами та ролями"""
    print(" Populating Auth DB...")
    
    conn = mysql.connector.connect(**DB_CONFIGS['auth'])
    cursor = conn.cursor()
    
    # Очищення існуючих даних
    print("   - Clearing existing auth data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DELETE FROM auth_tokens")
    cursor.execute("DELETE FROM auth_users")
    cursor.execute("DELETE FROM roles")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    
    # Створення ролей
    roles = [
        (generate_uuid(), 'ADMIN', 'Адміністратор системи'),
        (generate_uuid(), 'SALES', 'Менеджер продажів'),
        (generate_uuid(), 'CUSTOMER', 'Клієнт'),
        (generate_uuid(), 'BI_VIEWER', 'Аналітик BI')
    ]
    
    role_ids = {}
    for role_id, name, comment in roles:
        cursor.execute(
            "INSERT INTO roles (id, name, comment) VALUES (%s, %s, %s)",
            (role_id, name, comment)
        )
        role_ids[name] = role_id
    
    # Створення користувачів для співробітників
    user_ids = []
    for emp_id in employee_ids:
        user_id = generate_uuid()
        email = fake.email()
        cursor.execute(
            """INSERT INTO auth_users (id, email, status, created_at, updated_at, employee_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, email, 'active', datetime.now(), datetime.now(), emp_id)
        )
        
        # Credentials
        cursor.execute(
            """INSERT INTO auth_credentials (id, user_id, password_hash, algo, password_updated_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (generate_uuid(), user_id, hash_password('password123'), 'sha256', datetime.now(), datetime.now())
        )
        
        # Роль SALES
        cursor.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
            (user_id, role_ids['SALES'])
        )
        user_ids.append(user_id)
    
    # Створення користувачів для клієнтів
    for cust_id in customer_ids:
        user_id = generate_uuid()
        email = fake.email()
        cursor.execute(
            """INSERT INTO auth_users (id, email, status, created_at, updated_at, customer_id)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (user_id, email, 'active', datetime.now(), datetime.now(), cust_id)
        )
        
        # Credentials
        cursor.execute(
            """INSERT INTO auth_credentials (id, user_id, password_hash, algo, password_updated_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s)""",
            (generate_uuid(), user_id, hash_password('password123'), 'sha256', datetime.now(), datetime.now())
        )
        
        # Роль CUSTOMER
        cursor.execute(
            "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
            (user_id, role_ids['CUSTOMER'])
        )
        user_ids.append(user_id)
    
    # Створення адмін користувача
    admin_id = generate_uuid()
    cursor.execute(
        """INSERT INTO auth_users (id, email, status, created_at, updated_at)
           VALUES (%s, %s, %s, %s, %s)""",
        (admin_id, 'admin@techmarket.com', 'active', datetime.now(), datetime.now())
    )
    cursor.execute(
        """INSERT INTO auth_credentials (id, user_id, password_hash, algo, password_updated_at, updated_at)
           VALUES (%s, %s, %s, %s, %s, %s)""",
        (generate_uuid(), admin_id, hash_password('admin123'), 'sha256', datetime.now(), datetime.now())
    )
    cursor.execute(
        "INSERT INTO user_roles (user_id, role_id) VALUES (%s, %s)",
        (admin_id, role_ids['ADMIN'])
    )
    
    # Генерація токенів для деяких користувачів
    for _ in range(20):
        user_id = random.choice(user_ids)
        token_hash = hashlib.sha256(str(uuid.uuid4()).encode()).hexdigest()
        issued = datetime.now() - timedelta(days=random.randint(0, 30))
        expires = issued + timedelta(days=30)
        
        cursor.execute(
            """INSERT INTO auth_tokens (id, user_id, token_hash, issued_at, expires_at, 
               revoked, last_used_at, user_agent, ip, scopes)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (generate_uuid(), user_id, token_hash, issued, expires, False,
             datetime.now(), fake.user_agent(), fake.ipv4(), 'read,write')
        )
    
    conn.commit()
    cursor.close()
    conn.close()
    print(" Auth DB populated")

# ============================================
# Catalog Database Population
# ============================================

def populate_catalog_db() -> Dict[str, List[str]]:
    """Наповнює Catalog DB категоріями та товарами"""
    print(" Populating Catalog DB...")
    
    conn = mysql.connector.connect(**DB_CONFIGS['catalog'])
    cursor = conn.cursor()
    
    # Очищення існуючих даних
    print("   - Clearing existing catalog data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DELETE FROM products")
    cursor.execute("DELETE FROM categories")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    
    # Створення категорій верхнього рівня
    main_categories = [
        'Ноутбуки та комп\'ютери',
        'Смартфони та планшети',
        'Периферія',
        'Аксесуари',
        'Аудіо та відео',
        'Мережеве обладнання'
    ]
    
    category_ids = {}
    for cat_name in main_categories:
        cat_id = generate_uuid()
        cursor.execute(
            "INSERT INTO categories (id, name, parent_category_id) VALUES (%s, %s, NULL)",
            (cat_id, cat_name)
        )
        category_ids[cat_name] = cat_id
    
    # Підкатегорії
    subcategories = [
        ('Ноутбуки', category_ids['Ноутбуки та комп\'ютери']),
        ('Настільні ПК', category_ids['Ноутбуки та комп\'ютери']),
        ('Моноблоки', category_ids['Ноутбуки та комп\'ютери']),
        ('Смартфони', category_ids['Смартфони та планшети']),
        ('Планшети', category_ids['Смартфони та планшети']),
        ('Миші', category_ids['Периферія']),
        ('Клавіатури', category_ids['Периферія']),
        ('Монітори', category_ids['Периферія']),
    ]
    
    for subcat_name, parent_id in subcategories:
        subcat_id = generate_uuid()
        cursor.execute(
            "INSERT INTO categories (id, name, parent_category_id) VALUES (%s, %s, %s)",
            (subcat_id, subcat_name, parent_id)
        )
        category_ids[subcat_name] = subcat_id
    
    # Створення товарів (20+)
    products = [
        # Ноутбуки
        ('MacBook Pro 16"', 'LAPTOP-001', 'Ноутбуки', 89999, 75000),
        ('Dell XPS 15', 'LAPTOP-002', 'Ноутбуки', 67999, 55000),
        ('Lenovo ThinkPad X1', 'LAPTOP-003', 'Ноутбуки', 54999, 45000),
        ('ASUS ROG Zephyrus', 'LAPTOP-004', 'Ноутбуки', 72999, 60000),
        ('HP Pavilion 15', 'LAPTOP-005', 'Ноутбуки', 32999, 27000),
        
        # Настільні ПК
        ('Custom Gaming PC', 'PC-001', 'Настільні ПК', 45999, 38000),
        ('Dell Optiplex 7090', 'PC-002', 'Настільні ПК', 38999, 32000),
        
        # Смартфони
        ('iPhone 15 Pro', 'PHONE-001', 'Смартфони', 44999, 38000),
        ('Samsung Galaxy S24', 'PHONE-002', 'Смартфони', 38999, 32000),
        ('Google Pixel 8', 'PHONE-003', 'Смартфони', 32999, 27000),
        ('OnePlus 12', 'PHONE-004', 'Смартфони', 28999, 24000),
        ('Xiaomi 14', 'PHONE-005', 'Смартфони', 24999, 21000),
        
        # Планшети
        ('iPad Pro 12.9"', 'TAB-001', 'Планшети', 42999, 36000),
        ('Samsung Galaxy Tab S9', 'TAB-002', 'Планшети', 34999, 29000),
        
        # Периферія
        ('Logitech MX Master 3S', 'MOUSE-001', 'Миші', 3499, 2800),
        ('Razer DeathAdder V3', 'MOUSE-002', 'Миші', 2799, 2200),
        ('Keychron K2', 'KB-001', 'Клавіатури', 4299, 3500),
        ('Corsair K70 RGB', 'KB-002', 'Клавіатури', 5999, 4800),
        ('Dell UltraSharp U2723DE', 'MON-001', 'Монітори', 18999, 15000),
        ('LG 27UP850', 'MON-002', 'Монітори', 16999, 14000),
        
        # Додаткові товари
        ('Sony WH-1000XM5', 'AUDIO-001', 'Аудіо та відео', 12999, 10500),
        ('AirPods Pro 2', 'AUDIO-002', 'Аудіо та відео', 9999, 8200),
        ('TP-Link Archer AX73', 'NET-001', 'Мережеве обладнання', 4299, 3500),
        ('USB-C Hub 7-in-1', 'ACC-001', 'Аксесуари', 1299, 900),
        ('Laptop Backpack', 'ACC-002', 'Аксесуари', 1899, 1400),
    ]
    
    product_ids = []
    for name, sku, cat_name, price, cost in products:
        product_id = generate_uuid()
        cursor.execute(
            """INSERT INTO products (id, name, sku, category_id, price, cost, status, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (product_id, name, sku, category_ids[cat_name], price, cost, 'active', datetime.now(), datetime.now())
        )
        product_ids.append(product_id)
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f" Catalog DB populated: {len(category_ids)} categories, {len(product_ids)} products")
    
    return {'product_ids': product_ids}

# ============================================
# Orders Database Population
# ============================================

def populate_orders_db(product_ids: List[str]) -> Dict[str, List[str]]:
    """Наповнює Orders DB регіонами, клієнтами, менеджерами та замовленнями"""
    print(" Populating Orders DB...")
    
    conn = mysql.connector.connect(**DB_CONFIGS['orders'])
    cursor = conn.cursor()
    
    # Очищення існуючих даних
    print("   - Clearing existing orders data...")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
    cursor.execute("DELETE FROM order_items")
    cursor.execute("DELETE FROM orders")
    cursor.execute("DELETE FROM customers")
    cursor.execute("DELETE FROM employees")
    cursor.execute("DELETE FROM regions")
    cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
    conn.commit()
    
    # Регіони
    regions = [
        ('Київська область', 'KV'),
        ('Львівська область', 'LV'),
        ('Одеська область', 'OD'),
        ('Харківська область', 'KH'),
        ('Дніпропетровська область', 'DP'),
    ]
    
    region_ids = []
    for name, code in regions:
        region_id = generate_uuid()
        cursor.execute(
            "INSERT INTO regions (id, name, code) VALUES (%s, %s, %s)",
            (region_id, name, code)
        )
        region_ids.append(region_id)
    
    # Співробітники (менеджери) - мінімум 5
    employee_ids = []
    for i in range(10):  # Створюємо 10 менеджерів
        emp_id = generate_uuid()
        is_manager = i < 5  # Перші 5 - менеджери
        hired_date = random_date(datetime(2020, 1, 1), datetime(2024, 1, 1))
        
        cursor.execute(
            """INSERT INTO employees (id, first_name, last_name, email, hired_at, is_manager, region_id)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (emp_id, fake.first_name(), fake.last_name(), fake.email(), 
             hired_date.date(), is_manager, random.choice(region_ids))
        )
        employee_ids.append(emp_id)
    
    # Клієнти - мінімум 20
    customer_ids = []
    for _ in range(50):  # Створюємо 50 клієнтів
        cust_id = generate_uuid()
        cursor.execute(
            """INSERT INTO customers (id, first_name, last_name, email, phone, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s)""",
            (cust_id, fake.first_name(), fake.last_name(), fake.email(), 
             fake.phone_number(), datetime.now(), datetime.now())
        )
        customer_ids.append(cust_id)
    
    # Замовлення - мінімум 500
    order_ids = []
    start_date = datetime(2024, 1, 1)
    end_date = datetime.now()
    
    statuses = ['new', 'paid', 'shipped', 'cancelled']
    status_weights = [0.05, 0.70, 0.20, 0.05]  # 70% paid, 20% shipped
    
    for _ in range(600):  # Створюємо 600 замовлень
        order_id = generate_uuid()
        order_date = random_date(start_date, end_date)
        status = random.choices(statuses, weights=status_weights)[0]
        
        # Замовлення має 1-5 товарів
        num_items = random.randint(1, 5)
        total_amount = 0
        
        # Спочатку створюємо замовлення
        cursor.execute(
            """INSERT INTO orders (id, customer_id, employee_id, region_id, order_date, status, total_amount, created_at, updated_at)
               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)""",
            (order_id, random.choice(customer_ids), random.choice(employee_ids),
             random.choice(region_ids), order_date, status, 0, order_date, order_date)
        )
        
        # Створюємо позиції замовлення
        selected_products = random.sample(product_ids, min(num_items, len(product_ids)))
        for product_id in selected_products:
            # Отримуємо ціну товару з Catalog DB
            catalog_conn = mysql.connector.connect(**DB_CONFIGS['catalog'])
            catalog_cursor = catalog_conn.cursor()
            catalog_cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
            result = catalog_cursor.fetchone()
            catalog_cursor.close()
            catalog_conn.close()
            
            unit_price = Decimal(str(result[0])) if result else Decimal('10000')
            quantity = random.randint(1, 3)
            discount = random.choice([Decimal('0'), unit_price * Decimal('0.05'), unit_price * Decimal('0.1')])  # 0%, 5%, 10% знижка
            
            item_total = unit_price * quantity - discount
            total_amount += item_total
            
            cursor.execute(
                """INSERT INTO order_items (id, order_id, product_id, quantity, unit_price, discount)
                   VALUES (%s, %s, %s, %s, %s, %s)""",
                (generate_uuid(), order_id, product_id, quantity, unit_price, discount)
            )
        
        # Оновлюємо загальну суму замовлення
        cursor.execute(
            "UPDATE orders SET total_amount = %s WHERE id = %s",
            (total_amount, order_id)
        )
        
        order_ids.append((order_id, order_date, status, total_amount))
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f" Orders DB populated: {len(region_ids)} regions, {len(employee_ids)} employees, {len(customer_ids)} customers, {len(order_ids)} orders")
    
    return {
        'customer_ids': customer_ids,
        'employee_ids': employee_ids,
        'order_ids': order_ids
    }

# ============================================
# Payments Database Population
# ============================================

def populate_payments_db(order_ids: List[tuple]):
    """Наповнює Payments DB платежами"""
    print(" Populating Payments DB...")
    
    conn = mysql.connector.connect(**DB_CONFIGS['payments'])
    cursor = conn.cursor()
    
    # Очищення існуючих даних
    print("   - Clearing existing payments data...")
    cursor.execute("DELETE FROM payments")
    conn.commit()
    
    payment_methods = ['card', 'paypal', 'bank_transfer', 'cash']
    
    # Створюємо платежі тільки для paid та shipped замовлень
    payment_count = 0
    for order_id, order_date, status, amount in order_ids:
        if status in ['paid', 'shipped']:
            payment_id = generate_uuid()
            paid_at = order_date + timedelta(minutes=random.randint(5, 120))
            
            cursor.execute(
                """INSERT INTO payments (id, order_id, method, paid_at, amount)
                   VALUES (%s, %s, %s, %s, %s)""",
                (payment_id, order_id, random.choice(payment_methods), paid_at, amount)
            )
            payment_count += 1
    
    conn.commit()
    cursor.close()
    conn.close()
    print(f" Payments DB populated: {payment_count} payments")

# ============================================
# DWH Database Population (ETL Simulation)
# ============================================

def populate_dwh_db(catalog_data: Dict, orders_data: Dict):
    """Наповнює DWH (імітація ETL процесу)"""
    print(" Populating DWH DB (ETL simulation)...")
    
    # Підключення до DWH
    dwh_conn = psycopg2.connect(
        host='localhost',
        port=5432,
        user='dwh_user',
        password='dwh_pass',
        database='dwh_db'
    )
    dwh_cursor = dwh_conn.cursor()
    
    # Очищення існуючих даних у DWH
    print("   - Clearing existing DWH data...")
    dwh_cursor.execute("TRUNCATE TABLE fact_sales CASCADE")
    dwh_cursor.execute("TRUNCATE TABLE dim_employee CASCADE")
    dwh_cursor.execute("TRUNCATE TABLE dim_customer CASCADE")
    dwh_cursor.execute("TRUNCATE TABLE dim_product CASCADE")
    dwh_cursor.execute("TRUNCATE TABLE dim_category CASCADE")
    dwh_cursor.execute("TRUNCATE TABLE dim_region CASCADE")
    dwh_cursor.execute("TRUNCATE TABLE dim_date CASCADE")
    dwh_conn.commit()
    
    # Підключення до OLTP баз
    catalog_conn = mysql.connector.connect(**DB_CONFIGS['catalog'])
    catalog_cursor = catalog_conn.cursor(dictionary=True, buffered=True)
    
    orders_conn = mysql.connector.connect(**DB_CONFIGS['orders'])
    orders_cursor = orders_conn.cursor(dictionary=True, buffered=True)
    
    try:
        # 1. Populate dim_date (останні 2 роки)
        print("   - Building dim_date...")
        start_date = datetime.now() - timedelta(days=730)
        for i in range(730):
            current_date = start_date + timedelta(days=i)
            date_key = int(current_date.strftime('%Y%m%d'))
            dwh_cursor.execute("""
                INSERT INTO dim_date (date_key, date, year, quarter, month, day, day_of_week, is_weekend)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (date_key) DO NOTHING
            """, (
                date_key,
                current_date.date(),
                current_date.year,
                (current_date.month - 1) // 3 + 1,
                current_date.month,
                current_date.day,
                current_date.weekday() + 1,
                current_date.weekday() >= 5
            ))
        
        # 2. Populate dim_region
        print("   - Building dim_region...")
        orders_cursor.execute("SELECT * FROM regions")
        regions = orders_cursor.fetchall()
        region_mapping = {}
        for region in regions:
            dwh_cursor.execute("""
                INSERT INTO dim_region (region_id, name, code, updated_at)
                VALUES (%s, %s, %s, %s)
                RETURNING region_key
            """, (region['id'], region['name'], region['code'], datetime.now()))
            region_mapping[region['id']] = dwh_cursor.fetchone()[0]
        
        # 3. Populate dim_category
        print("   - Building dim_category...")
        catalog_cursor.execute("SELECT * FROM categories ORDER BY parent_category_id IS NULL DESC, parent_category_id")
        categories = catalog_cursor.fetchall()
        category_mapping = {}
        for category in categories:
            parent_key = category_mapping.get(category['parent_category_id']) if category['parent_category_id'] else None
            dwh_cursor.execute("""
                INSERT INTO dim_category (category_id, name, parent_category_key, updated_at)
                VALUES (%s, %s, %s, %s)
                RETURNING category_key
            """, (category['id'], category['name'], parent_key, datetime.now()))
            category_mapping[category['id']] = dwh_cursor.fetchone()[0]
        
        # 4. Populate dim_product
        print("   - Building dim_product...")
        catalog_cursor.execute("SELECT * FROM products")
        products = catalog_cursor.fetchall()
        product_mapping = {}
        for product in products:
            dwh_cursor.execute("""
                INSERT INTO dim_product (product_id, name, sku, category_key, updated_at)
                VALUES (%s, %s, %s, %s, %s)
                RETURNING product_key
            """, (
                product['id'],
                product['name'],
                product['sku'],
                category_mapping.get(product['category_id']),
                datetime.now()
            ))
            product_mapping[product['id']] = dwh_cursor.fetchone()[0]
        
        # 5. Populate dim_customer
        print("   - Building dim_customer...")
        orders_cursor.execute("SELECT * FROM customers")
        customers = orders_cursor.fetchall()
        customer_mapping = {}
        for customer in customers:
            # Get customer's region from their first order (customers don't have direct region)
            region_cursor = orders_conn.cursor(dictionary=True, buffered=True)
            region_cursor.execute("""
                SELECT region_id FROM orders WHERE customer_id = %s LIMIT 1
            """, (customer['id'],))
            order_region = region_cursor.fetchone()
            region_cursor.close()
            customer_region_key = region_mapping.get(order_region['region_id']) if order_region else None
            
            dwh_cursor.execute("""
                INSERT INTO dim_customer (customer_id, first_name, last_name, email, region_key, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING customer_key
            """, (
                customer['id'],
                customer['first_name'],
                customer['last_name'],
                customer['email'],
                customer_region_key,
                datetime.now()
            ))
            customer_mapping[customer['id']] = dwh_cursor.fetchone()[0]
        
        # 6. Populate dim_employee
        print("   - Building dim_employee...")
        orders_cursor.execute("SELECT * FROM employees")
        employees = orders_cursor.fetchall()
        employee_mapping = {}
        for employee in employees:
            dwh_cursor.execute("""
                INSERT INTO dim_employee (employee_id, first_name, last_name, email, region_key, updated_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING employee_key
            """, (
                employee['id'],
                employee['first_name'],
                employee['last_name'],
                employee['email'],
                region_mapping.get(employee['region_id']),
                datetime.now()
            ))
            employee_mapping[employee['id']] = dwh_cursor.fetchone()[0]
        
        # 7. Populate fact_sales
        print("   - Building fact_sales...")
        orders_cursor.execute("""
            SELECT o.id as order_id, o.order_date, o.customer_id, o.employee_id,
                   o.region_id,
                   oi.id as order_item_id, oi.product_id, oi.quantity, 
                   oi.unit_price, oi.discount
            FROM orders o
            JOIN order_items oi ON o.id = oi.order_id
            WHERE o.status IN ('paid', 'shipped', 'delivered')
        """)
        
        sales_count = 0
        for sale in orders_cursor:
            order_date = sale['order_date']
            date_key = int(order_date.strftime('%Y%m%d'))
            
            # Перевірка чи існує date_key у dim_date
            dwh_cursor.execute("SELECT 1 FROM dim_date WHERE date_key = %s", (date_key,))
            if not dwh_cursor.fetchone():
                # Якщо дати немає в dim_date - пропускаємо цей запис
                continue
            
            revenue = float(sale['unit_price']) * sale['quantity']
            discount_amount = float(sale['discount']) if sale['discount'] else 0.0
            cost = revenue * 0.6  # Припускаємо собівартість 60% від ціни
            margin = revenue - discount_amount - cost
            
            dwh_cursor.execute("""
                INSERT INTO fact_sales (
                    order_id, order_item_id, date_key, product_key, customer_key,
                    employee_key, region_key, quantity, revenue, discount_amount,
                    cost, margin
                )
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (
                sale['order_id'],
                sale['order_item_id'],
                date_key,
                product_mapping.get(sale['product_id']),
                customer_mapping.get(sale['customer_id']),
                employee_mapping.get(sale['employee_id']),
                region_mapping.get(sale['region_id']),
                sale['quantity'],
                revenue,
                discount_amount,
                cost,
                margin
            ))
            sales_count += 1
        
        dwh_conn.commit()
        print(f"   - DWH tables populated:")
        print(f"     * dim_date: 730 days")
        print(f"     * dim_region: {len(regions)}")
        print(f"     * dim_category: {len(categories)}")
        print(f"     * dim_product: {len(products)}")
        print(f"     * dim_customer: {len(customers)}")
        print(f"     * dim_employee: {len(employees)}")
        print(f"     * fact_sales: {sales_count}")
        
    finally:
        catalog_cursor.close()
        catalog_conn.close()
        orders_cursor.close()
        orders_conn.close()
        dwh_cursor.close()
        dwh_conn.close()

# ============================================
# Main Execution
# ============================================

def main():
    """Головна функція для запуску генерації даних"""
    print("=" * 60)
    print(" TechMarket Test Data Generator")
    print("=" * 60)
    
    try:
        # 1. Catalog DB (незалежне)
        catalog_data = populate_catalog_db()
        
        # 2. Orders DB (потребує product_ids)
        orders_data = populate_orders_db(catalog_data['product_ids'])
        
        # 3. Auth DB (потребує customer_ids та employee_ids)
        populate_auth_db(orders_data['customer_ids'], orders_data['employee_ids'])
        
        # 4. Payments DB (потребує order_ids)
        populate_payments_db(orders_data['order_ids'])
        
        # 5. DWH DB (ETL імітація - потребує даних з Catalog та Orders)
        populate_dwh_db(catalog_data, orders_data)
        
        print("=" * 60)
        print(" All databases populated successfully!")
        print("=" * 60)
        print("\n Summary:")
        print(f"  - Products: {len(catalog_data['product_ids'])}")
        print(f"  - Customers: {len(orders_data['customer_ids'])}")
        print(f"  - Employees: {len(orders_data['employee_ids'])}")
        print(f"  - Orders: {len(orders_data['order_ids'])}")
        print(f"\n Database connections:")
        print(f"  - Auth DB: localhost:3306")
        print(f"  - Catalog DB: localhost:3307")
        print(f"  - Orders DB: localhost:3308")
        print(f"  - Payments DB: localhost:3309")
        print(f"  - DWH DB: localhost:5432")
        print(f"\n Adminer: http://localhost:8080")
        
    except Exception as e:
        print(f" Error: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
