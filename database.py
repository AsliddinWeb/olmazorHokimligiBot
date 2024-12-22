import sqlite3

class Database:
    def __init__(self, db_name="bot_database.db"):
        self.connection = sqlite3.connect(db_name)
        self.cursor = self.connection.cursor()
        self._create_tables()

    def _create_tables(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            full_name TEXT,
            username TEXT NULL,
            chat_id INTEGER UNIQUE,
            language TEXT,
            phone TEXT
        );
        """)
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS appeals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            text TEXT,
            response_text TEXT NULL,
            status TEXT,
            FOREIGN KEY(user_id) REFERENCES users(id)
        );
        """)
        self.connection.commit()

    # Users
    def insert_user(self, full_name, username, chat_id, language, phone):
        try:
            self.cursor.execute("""
                INSERT OR IGNORE INTO users (full_name, username, chat_id, language, phone)
                VALUES (?, ?, ?, ?, ?);
            """, (full_name, username, chat_id, language, phone))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def get_user(self, chat_id):
        try:
            self.cursor.execute("""
                SELECT * FROM users WHERE chat_id = ?;
            """, (chat_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def update_language(self, chat_id, language):
        try:
            self.cursor.execute("""
                UPDATE users SET language = ? WHERE chat_id = ?;
            """, (language, chat_id))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def update_full_name(self, chat_id, full_name):
        try:
            self.cursor.execute("""
                UPDATE users SET full_name = ? WHERE chat_id = ?;
            """, (full_name, chat_id))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    # Appeals
    def get_user_appeals(self, user_id):
        try:
            self.cursor.execute("""
                SELECT * FROM appeals WHERE user_id = ?;
            """, (user_id,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return []

    def get_appeal(self, id):
        try:
            self.cursor.execute("""
                SELECT * FROM appeals WHERE id = ?;
            """, (id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None

    def create_appeal(self, user_id, text, status="♻️ Yuborildi"):
        try:
            self.cursor.execute("""
                INSERT INTO appeals (user_id, text, response_text, status)
                VALUES (?, ?, NULL, ?);
            """, (user_id, text, status))
            self.connection.commit()
            self.cursor.execute("""
                SELECT * FROM appeals WHERE id = (SELECT last_insert_rowid());
            """)
            return self.cursor.fetchone()

        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def update_appeal_status(self, appeal_id, status, response_text=None):
        try:
            self.cursor.execute("""
                UPDATE appeals SET status = ?, response_text = ? WHERE id = ?;
            """, (status, response_text, appeal_id))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")

    def close(self):
        self.connection.close()
