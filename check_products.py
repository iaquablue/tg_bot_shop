import sqlite3

def check_db():
    conn = sqlite3.connect("data/products.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = cursor.fetchall()
    print(f"Таблицы в БД: {tables}")
    
    cursor.execute("PRAGMA table_info(products)")
    columns = cursor.fetchall()
    print("\nСтруктура таблицы products:")
    for col in columns:
        print(f"{col[1]} | {col[2]}")
    
    cursor.execute("SELECT * FROM products")
    products = cursor.fetchall()
    print("\nТекущие товары:", products)
    
    conn.close()

if __name__ == "__main__":
    check_db()