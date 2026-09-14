import sqlite3
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from config import DB_PATH  
HERE = Path(__file__).resolve().parent


def apply(conn, filename):
    sql = (HERE / filename).read_text(encoding="utf-8")
    conn.executescript(sql)
    print(f"applied {filename}")


def main():
    conn = sqlite3.connect(DB_PATH)
    try:
        apply(conn, "schema_extension.sql")
        apply(conn, "seed_data.sql")
        conn.commit()
    finally:
        conn.close()
    print(f"database ready: {DB_PATH}")


if __name__ == "__main__":
    main()
