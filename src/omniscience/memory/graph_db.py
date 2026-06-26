import sqlite3
import os

class GraphDB:
    def __init__(self, db_path: str = "./.omniscience/graph.db"):
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self.conn = sqlite3.connect(db_path, check_same_thread=False)
        self._init_db()

    def _init_db(self):
        cursor = self.conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dependencies (
                caller_id TEXT,
                callee_id TEXT,
                UNIQUE(caller_id, callee_id)
            )
        ''')
        self.conn.commit()

    def add_dependency(self, caller_id: str, callee_id: str):
        cursor = self.conn.cursor()
        cursor.execute('''
            INSERT OR IGNORE INTO dependencies (caller_id, callee_id)
            VALUES (?, ?)
        ''', (caller_id, callee_id))
        self.conn.commit()

    def get_blast_radius(self, symbol_id: str) -> list[str]:
        cursor = self.conn.cursor()
        cursor.execute('SELECT caller_id FROM dependencies WHERE callee_id = ?', (symbol_id,))
        rows = cursor.fetchall()
        return [r[0] for r in rows]

    def clear_file_dependencies(self, file_path: str):
        cursor = self.conn.cursor()
        cursor.execute('DELETE FROM dependencies WHERE caller_id LIKE ?', (f"{file_path}::%",))
        self.conn.commit()
