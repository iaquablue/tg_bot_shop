import sqlite3

conn = sqlite3.connect('bot.db')
cursor = conn.cursor()

# Проверяем содержимое таблицы users
cursor.execute("SELECT * FROM users")
print(cursor.fetchall())

conn.close()