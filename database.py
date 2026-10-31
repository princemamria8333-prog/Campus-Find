import sqlite3

DATABASE_NAME = "campusfind.db"


def connect():
    return sqlite3.connect(DATABASE_NAME)


def create_table():
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reports (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            item_type TEXT NOT NULL,
            item_name TEXT NOT NULL,
            description TEXT NOT NULL,
            location TEXT NOT NULL,
            image BLOB,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    connection.commit()
    connection.close()


def add_report(item_type, item_name, description, location, image):
    connection = connect()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO reports
        (item_type, item_name, description, location, image)
        VALUES (?, ?, ?, ?, ?)
    """, (item_type, item_name, description, location, image))

    connection.commit()
    connection.close()


def get_reports():
    connection = connect()
    connection.row_factory = sqlite3.Row
    cursor = connection.cursor()

    cursor.execute("SELECT * FROM reports ORDER BY id DESC")
    reports = [dict(row) for row in cursor.fetchall()]

    connection.close()
    return reports