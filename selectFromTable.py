import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

# List tables
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()
print("Tables:", tables)

# Check if 'users' table exists
if ('users',) in tables:
    print("The 'users' table exists.")
else:
    print("The 'users' table does not exist.")

conn.close()