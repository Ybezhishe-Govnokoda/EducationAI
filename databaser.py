import sqlite3 as sql

class Databaser:
    def __init__(self, db_name='database.db'):
        self.connection = sql.connect(db_name, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT,
                            mail TEXT PRIMARY KEY,
                            password TEXT)''')
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS study_files (
                            file_id INTEGER PRIMARY KEY AUTOINCREMENT,
                            path TEXT,
                            type TEXT)''')

    def add_user(self, name: str, mail: str, password: str):
        self.cursor.execute('''INSERT INTO users (name, mail, password) 
                VALUES (?, ?, ?)''', (name, mail, password))
        self.connection.commit()

    def check_user(self, mail: str, password: str):
        self.cursor.execute('SELECT * FROM users WHERE mail = ? AND password = ?', (mail, password))
        r = self.cursor.fetchone()
        if not r:
            return "None"

        return dict(r)

    def add_file(self, path_to_file: str):
        self.cursor.execute('''INSERT INTO users (path, type) 
                        VALUES (?, ?)''', (path_to_file, path_to_file.rsplit('.', 1)[-1]))
        self.connection.commit()
