import sqlite3


class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self._conn = None

    def connect(self):
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def close(self):
        if self._conn:
            self._conn.close()
            self._conn = None

    def execute(self, query, params=None):
        conn = self.connect()
        cursor = conn.execute(query, params or ())
        conn.commit()
        return cursor

    def fetch_one(self, query, params=None):
        conn = self.connect()
        cursor = conn.execute(query, params or ())
        return cursor.fetchone()

    def fetch_all(self, query, params=None):
        conn = self.connect()
        cursor = conn.execute(query, params or ())
        return cursor.fetchall()
