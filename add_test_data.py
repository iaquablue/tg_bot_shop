import sqlite3

def add_test_data():
    conn = sqlite3.connect('data/products.db')
    cursor = conn.cursor()
    
    try:
        # Очистка старых данных (опционально)
        cursor.executescript("""
            DELETE FROM products;
            DELETE FROM categories;
            UPDATE SQLITE_SEQUENCE SET SEQ=0 WHERE NAME IN ('products', 'categories');
        """)
        
        # Добавляем категории
        cursor.executescript("""
            INSERT INTO categories (name) VALUES ('Аккаунты'), ('Игры');
            INSERT INTO categories (name, parent_id) VALUES ('Steam', 1), ('Epic', 1);
        """)
        
        # Добавляем товары
        products = [
            ('Аккаунт CS2', 1000, 3),
            ('Аккаунт Dota 2', 800, 3),
            ('Аккаунт Fortnite', 1200, 4),
            ('Игра Cyberpunk', 2000, 2)
        ]
        cursor.executemany(
            "INSERT INTO products (name, price, category_id) VALUES (?, ?, ?)",
            products
        )
        
        conn.commit()
        print("✅ Тестовые данные успешно добавлены")
        
    except Exception as e:
        print(f"❌ Ошибка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    add_test_data()