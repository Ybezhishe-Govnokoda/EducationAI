import sqlite3 as sql
from tkinter.constants import INSERT


class Databaser:
    def __init__(self, db_name='database.db'):
        self.connection = sql.connect(db_name, check_same_thread=False)
        self.connection.row_factory = sql.Row
        self.cursor = self.connection.cursor()
        self.cursor.execute("PRAGMA foreign_keys = ON")

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL,
                            mail TEXT NOT NULL,
                            password TEXT NOT NULL)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS courses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            name TEXT NOT NULL)''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS course_files (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            course_id INTEGER,
                            name TEXT,
                            path TEXT,
                            type TEXT,
                            FOREIGN KEY(course_id) REFERENCES courses(id))''')

        self.cursor.execute('''CREATE TABLE IF NOT EXISTS transcribed_files (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            file_id INTEGER,
                            name TEXT,
                            path TEXT,
                            summered BOOL,
                            FOREIGN KEY(file_id) REFERENCES course_files(id))''')

    # Для работы с пользователями
    def add_user(self, name: str, mail: str, password: str):
        self.cursor.execute('''INSERT INTO users (name, mail, password) 
                VALUES (?, ?, ?)''', (name, mail, password))
        self.connection.commit()

    def add_user_admin(self, name: str, mail: str, password: str):
        self.cursor.execute('''INSERT INTO users (name, mail, password, is_admin) 
                VALUES (?, ?, 1)''', (name, mail, password))
        self.connection.commit()

    def get_user(self, user_id):
        self.cursor.execute('''SELECT * FROM users
                                WHERE user_id = ?''', (user_id,))
        r = self.cursor.fetchone()
        if not r:
            return "None"
        return dict(r)

    def check_user(self, mail: str, password: str):
        self.cursor.execute('''SELECT * FROM users 
                                WHERE mail = ? 
                                AND password = ?''',
                            (mail, password))
        r = self.cursor.fetchone()
        if not r:
            return "None"
        return dict(r)

    # Для работы с курсами
    def add_course(self, name):
        self.cursor.execute('''INSERT INTO courses (name) VALUES (?)''', (name,))
        self.connection.commit()

    def get_courses(self):
        self.cursor.execute('''SELECT * FROM courses''')
        courses_list = self.cursor.fetchall()
        courses_list = list(map(dict, courses_list))

        return courses_list

    # Для работы с файлами курсов
    def get_files(self):
        self.cursor.execute('''SELECT * FROM course_files''')
        files_list = self.cursor.fetchall()
        files_list = list(map(dict, files_list))

        return files_list

    def get_files_from_course(self, course_id):
        self.cursor.execute('''SELECT * FROM course_files
                            WHERE course_id = ?''', (course_id,))
        rows = self.cursor.fetchall()
        return [dict(row) for row in rows] if rows else []

    def add_file_to_course(self, course_id: int, name: str, path: str, type: str):
        self.cursor.execute('''INSERT INTO course_files (course_id, name, path, type) 
                        VALUES (?, ?, ?, ?)''',(course_id, name, path, type))
        self.connection.commit()

    def get_file(self, file_id):
        self.cursor.execute('''SELECT * FROM course_files 
                                WHERE id = ?''',
                                (file_id,))
        r = self.cursor.fetchone()
        if not r:
            return "None"
        return dict(r)

    def get_file_by_name(self, filename):
        self.cursor.execute('''SELECT * FROM course_files 
                                        WHERE name = ?''',
                            (filename,))
        r = self.cursor.fetchone()
        if not r:
            return "None"
        return dict(r)

    # Транскрибированные файлы
    def add_transcribed_file(self, file_id: int, name: str, path: str):
        self.cursor.execute('''INSERT INTO transcribed_files (file_id, name, path, summered) 
                            VALUES (?, ?, ?, 0)''', (file_id, name, path))
        self.connection.commit()

    def get_transcribed_file(self, file_id):
        self.cursor.execute('''SELECT * FROM transcribed_files 
                                        WHERE id = ?''',
                            (file_id,))
        r = self.cursor.fetchone()
        if not r:
            return "None"
        return dict(r)

    # def summary_done(self, file_id: int):
    #     self.cursor.execute('''UPDATE transcribed_files SET summered = ? WHERE id = ?''',
    #                         (1, file_id))
    #     self.connection.commit()


# db = Databaser()
# user = db.check_user('egor@mail.com', 'egor')
# print(user)
# print(user['user_id'])
