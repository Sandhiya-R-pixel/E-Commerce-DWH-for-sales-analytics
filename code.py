import sqlite3
import pandas as pd
from datetime import datetime

# -----------------------------
# 1. EXTRACT (Simulated CSV Data)
# -----------------------------
def extract_data():
    # Simulated datasets (you can replace with CSV files)
    customers = pd.DataFrame({
        "customer_id": [1, 2, 3],
        "name": ["Alice", "Bob", "Charlie"],
        "city": ["Chennai", "Madurai", "Coimbatore"]
    })

    products = pd.DataFrame({
        "product_id": [101, 102, 103],
        "product_name": ["Laptop", "Mobile", "Headphones"],
        "category": ["Electronics", "Electronics", "Accessories"],
        "price": [50000, 20000, 2000]
    })

    orders = pd.DataFrame({
        "order_id": [1001, 1002, 1003],
        "customer_id": [1, 2, 3],
        "order_date": ["2026-01-01", "2026-01-05", "2026-01-10"]
    })

    order_items = pd.DataFrame({
        "order_id": [1001, 1002, 1003],
        "product_id": [101, 102, 103],
        "quantity": [1, 2, 3]
    })

    return customers, products, orders, order_items


# -----------------------------
# 2. TRANSFORM
# -----------------------------
def transform_data(customers, products, orders, order_items):
    # Merge tables to create fact table
    merged = order_items.merge(products, on="product_id")
    merged = merged.merge(orders, on="order_id")
    merged = merged.merge(customers, on="customer_id")

    # Create total sales column
    merged["total_sales"] = merged["quantity"] * merged["price"]

    # Convert date
    merged["order_date"] = pd.to_datetime(merged["order_date"])

    return merged


# -----------------------------
# 3. LOAD (Data Warehouse)
# -----------------------------
def load_data(data):
    conn = sqlite3.connect("ecommerce_dw.db")
    cursor = conn.cursor()

    # Create Fact Table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS fact_sales (
        order_id INTEGER,
        customer_name TEXT,
        city TEXT,
        product_name TEXT,
        category TEXT,
        quantity INTEGER,
        price REAL,
        total_sales REAL,
        order_date TEXT
    )
    """)

    # Insert Data
    for _, row in data.iterrows():
        cursor.execute("""
        INSERT INTO fact_sales VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            row["order_id"],
            row["name"],
            row["city"],
            row["product_name"],
            row["category"],
            row["quantity"],
            row["price"],
            row["total_sales"],
            row["order_date"].strftime("%Y-%m-%d")
        ))

    conn.commit()
    conn.close()


# -----------------------------
# 4. ANALYTICS QUERIES
# -----------------------------
def run_analytics():
    conn = sqlite3.connect("ecommerce_dw.db")

    print("\n📊 Total Sales:")
    query1 = "SELECT SUM(total_sales) FROM fact_sales"
    print(pd.read_sql(query1, conn))

    print("\n📊 Sales by Category:")
    query2 = """
    SELECT category, SUM(total_sales) as total
    FROM fact_sales
    GROUP BY category
    """
    print(pd.read_sql(query2, conn))

    print("\n📊 Top Customers:")
    query3 = """
    SELECT customer_name, SUM(total_sales) as total
    FROM fact_sales
    GROUP BY customer_name
    ORDER BY total DESC
    """
    print(pd.read_sql(query3, conn))

    print("\n📊 Sales by City:")
    query4 = """
    SELECT city, SUM(total_sales) as total
    FROM fact_sales
    GROUP BY city
    """
    print(pd.read_sql(query4, conn))

    conn.close()


# -----------------------------
# MAIN PIPELINE
# -----------------------------
def main():
    print("🚀 Starting ETL Pipeline...")

    customers, products, orders, order_items = extract_data()
    transformed_data = transform_data(customers, products, orders, order_items)
    load_data(transformed_data)

    print("✅ Data Loaded Successfully!")
    run_analytics()


if __name__ == "__main__":
    main()
