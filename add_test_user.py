import sqlite3

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

# Добавляем тестового пользователя
cursor.execute(
    "INSERT OR IGNORE INTO users (user_id, balance, username) VALUES (?, ?, ?)",
    (1323712500, 500, 'test_user')  # Замените 123456789 на ваш ID в Telegram
)
conn.commit()
conn.close()
print("Тестовый пользователь добавлен!")