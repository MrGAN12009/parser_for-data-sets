import sqlite3

with sqlite3.connect("database.db") as db:
    sql = db.cursor()
    sql.execute(
        """
        CREATE TABLE IF NOT EXISTS pages (
            source TEXT NOT NULL,
            link TEXT NOT NULL UNIQUE,
            title TEXT,
            content TEXT
        );
        """
    )
    db.commit()
    print("SQLite подключен")

sql.execute(f"SELECT title, content FROM pages WHERE link = 'https://belabraziv.ru/catalog/'")
print(sql.fetchone())