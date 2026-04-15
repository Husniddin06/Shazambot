import sqlite3

conn = sqlite3.connect("database.db")
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER,
    lang TEXT
)
""")

# SETTINGS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    key TEXT,
    value TEXT
)
""")

conn.commit()


# SETTING SAQLASH
def set_setting(key, value):
    cursor.execute("DELETE FROM settings WHERE key=?", (key,))
    cursor.execute("INSERT INTO settings VALUES (?,?)", (key, value))
    conn.commit()


# SETTING OLISH
def get_setting(key):
    cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
    res = cursor.fetchone()
    return res[0] if res else None
