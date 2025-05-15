import sqlite3

def add_admin(user_id: int, username: str):
    conn = sqlite3.connect("data/products.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO users (user_id, username, role) VALUES (?, ?, ?)",
        (user_id, username, "admin")
    )
    conn.commit()
    conn.close()
    print(f"✅ Пользователь @{username} (ID: {user_id}) добавлен как админ")

if __name__ == "__main__":
    # Замените значения на свои!
    add_admin(
        user_id=7905398325,  # Ваш Telegram ID (узнать у @userinfobot)
        username="asdsadasdasdfasg"  # Без @
    )