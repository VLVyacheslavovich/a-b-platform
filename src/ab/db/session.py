import os
import psycopg

DSN = os.getenv("DB_DSN", "postgresql://ab:ab@db:5432/ab")

def get_conn():
    """
    Открывает новое соединение (контекстно-управляемое).
    Пример:
        with get_conn() as conn, conn.cursor() as cur:
            cur.execute("select 1")
    """
    return psycopg.connect(DSN)