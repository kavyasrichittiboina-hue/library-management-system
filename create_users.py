import sqlite3

connection = sqlite3.connect("library.db")
cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS Users
(
    UserId INTEGER PRIMARY KEY AUTOINCREMENT,
    LoginId TEXT UNIQUE NOT NULL,
    Password TEXT NOT NULL,
    Role TEXT NOT NULL
)
""")

cursor.execute("""
INSERT OR IGNORE INTO Users
(LoginId, Password, Role)
VALUES (?, ?, ?)
""", ("5241411166", "student123", "Student"))

cursor.execute("""
INSERT OR IGNORE INTO Users
(LoginId, Password, Role)
VALUES (?, ?, ?)
""", ("6241411166", "teacher123", "Teacher"))

cursor.execute("""
INSERT OR IGNORE INTO Users
(LoginId, Password, Role)
VALUES (?, ?, ?)
""", ("22435-CSE-001", "admin123", "Admin"))

connection.commit()
connection.close()

print("Users table created successfully")
print("Login accounts added successfully")