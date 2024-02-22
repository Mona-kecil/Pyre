def initialize_table(conn):
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS reminders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                time TEXT,
                reminder TEXT
        )
    """)
    conn.commit()

def insert(conn, authorId, time, remindMessage):
    cursor = conn.cursor()

    cursor.execute("""
        INSERT INTO reminders (user_id, time, reminder)
        VALUES (?, ?, ?)
    """, (authorId, time, remindMessage))
    conn.commit()

def view(conn, authorId):
    cursor = conn.cursor()

    cursor.execute("""
        SELECT * FROM reminders WHERE user_id = ?
    """, (authorId, ))
    data = cursor.fetchall()
    return data

def update(conn, authorId, time, remindMessage):
    pass

def delete(conn, authorId, time):
    pass

def find_data(conn, id, authorId):
    pass

"""
Create v
Read v
Update \
Delete \
Search \
"""