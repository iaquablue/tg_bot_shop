import sqlite3
from sqlite3 import Error
from config import DB_NAME

def create_connection():
    """Создает подключение к базе данных"""
    conn = None
    try:
        conn = sqlite3.connect(DB_NAME)
        conn.execute("PRAGMA foreign_keys = ON")
        return conn
    except Error as e:
        print(f"Ошибка подключения: {e}")
    return conn

def init_db():
    """Инициализирует таблицы"""
    commands = [
        """CREATE TABLE IF NOT EXISTS categories (
            category_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL
        )""",
        """CREATE TABLE IF NOT EXISTS products (
            product_id INTEGER PRIMARY KEY,
            name TEXT NOT NULL,
            price REAL NOT NULL,
            category_id INTEGER NOT NULL,
            FOREIGN KEY (category_id) REFERENCES categories(category_id)
        )""",
        """CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            username TEXT,
            balance REAL DEFAULT 0
        )"""
    ]
    
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            for command in commands:
                cursor.execute(command)
            conn.commit()
        except Error as e:
            print(f"Ошибка при создании таблиц: {e}")
        finally:
            conn.close()

def init_test_data():
    """Добавляет тестовые данные"""
    test_data = [
        ("INSERT OR IGNORE INTO categories VALUES (?, ?)", [(1, "Аккаунты"), (2, "Игровые предметы")]),
        ("INSERT OR IGNORE INTO products VALUES (?, ?, ?, ?)", [
            (1, "Аккаунт Premium", 100.0, 1),
            (2, "Золотая монета", 50.0, 2)
        ]),
        ("INSERT OR IGNORE INTO users VALUES (?, ?, ?)", [
            (7905398325, "Admin", 500.0)  # Замените на ваш ID
        ])
    ]
    
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            for query, data in test_data:
                cursor.executemany(query, data)
            conn.commit()
        except Error as e:
            print(f"Ошибка при добавлении тестовых данных: {e}")
        finally:
            conn.close()

def get_user_balance(user_id: int) -> float:
    """Возвращает баланс пользователя"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
            result = cursor.fetchone()
            return result[0] if result else 0.0
        except Error as e:
            print(f"Ошибка при запросе баланса: {e}")
            return 0.0
        finally:
            conn.close()
    return 0.0

def update_user_balance(user_id: int, delta: float):
    """Обновляет баланс пользователя"""
    conn = create_connection()
    if conn:
        try:
            cursor = conn.cursor()
            cursor.execute(
                "INSERT OR IGNORE INTO users (user_id, balance) VALUES (?, 0)",
                (user_id,)
            )
            cursor.execute(
                "UPDATE users SET balance = balance + ? WHERE user_id = ?",
                (delta, user_id)
            )
            conn.commit()
        except Error as e:
            print(f"Ошибка при обновлении баланса: {e}")
        finally:
            conn.close()

if __name__ == "__main__":
    init_db()
    init_test_data()
    print("✅ База данных инициализирована")