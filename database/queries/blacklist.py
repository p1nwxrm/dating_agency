import logging
from ..db import get_connection

# ---------------------------
# Додати користувача до ЧС
# ---------------------------
def add_to_blacklist(blocker_id: int, blocked_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
                INSERT INTO blacklist (blocker_id, blocked_id)
                VALUES (%s, %s)
            """, (blocker_id, blocked_id))

        conn.commit()
        return True
    except Exception as e:
        logging.exception(e)
        return False
    finally:
        cursor.close()
        conn.close()


# ---------------------------
# Видалити користувача з ЧС
# ---------------------------
def remove_from_blacklist(blocker_id: int, blocked_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute("""
            DELETE FROM blacklist
            WHERE blocker_id = %s AND blocked_id = %s
        """, (blocker_id, blocked_id))

        conn.commit()
        return True

    except Exception as e:
        logging.exception(e)
        return False

    finally:
        cursor.close()
        conn.close()