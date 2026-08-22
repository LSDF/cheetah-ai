import sqlite3
import json
from datetime import datetime
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "cheetah_memory.db"

class Memory:
    def __init__(self):
        DB_PATH.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        self._init_db()

    def _init_db(self):
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                mode TEXT,
                created_at TEXT
            )
        """)
        self.conn.execute("""
            CREATE TABLE IF NOT EXISTS improvements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT,
                changes TEXT,
                score_before REAL,
                score_after REAL,
                accepted INTEGER,
                created_at TEXT
            )
        """)
        self.conn.commit()

    def add_message(self, session_id: str, role: str, content: str, mode: str = "private"):
        self.conn.execute(
            "INSERT INTO messages (session_id, role, content, mode, created_at) VALUES (?, ?, ?, ?, ?)",
            (session_id, role, content, mode, datetime.utcnow().isoformat())
        )
        self.conn.commit()

    def get_history(self, session_id: str, limit: int = 20):
        rows = self.conn.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id DESC LIMIT ?",
            (session_id, limit)
        ).fetchall()
        return [{"role": r["role"], "content": r["content"]} for r in reversed(rows)]

    def log_improvement(self, description: str, changes: str, score_before: float, score_after: float, accepted: bool):
        self.conn.execute(
            "INSERT INTO improvements (description, changes, score_before, score_after, accepted, created_at) VALUES (?, ?, ?, ?, ?, ?)",
            (description, changes, score_before, score_after, int(accepted), datetime.utcnow().isoformat())
        )
        self.conn.commit()
