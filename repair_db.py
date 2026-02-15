import sqlite3

conn = sqlite3.connect('db.sqlite3')
cursor = conn.cursor()

# چک کردن سلامت دیتابیس
cursor.execute('PRAGMA integrity_check;')
print(f"Integrity check: {cursor.fetchone()[0]}")

# غیرفعال کردن چک کردن کلید خارجی برای لحظاتی
cursor.execute('PRAGMA foreign_keys = OFF;')
conn.commit()
print("Foreign keys disabled globally.")

conn.close()