import logging
from ..db import get_connection

# --------------------------------------
# Отримуємо усі причини скарг
# --------------------------------------
def get_all_reasons() -> list[dict]:
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        cursor.execute("SELECT id, name FROM reasons ORDER BY id")
        reasons = cursor.fetchall()
        return reasons


    except Exception as e:
        logging.exception(e)
        return []

    finally:
        cursor.close()
        conn.close()

# --------------------------------------
# Отримати причину по її ID
# --------------------------------------
def get_reason_by_id(reason_id: int) -> str | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("SELECT name FROM reasons WHERE id = %s", (reason_id,))
        row = cursor.fetchone()
        if row:
            return row["name"]
        return None


    except Exception as e:
        logging.exception(e)
        return None

    finally:
        cursor.close()
        conn.close()