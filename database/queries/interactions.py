import logging
from ..db import get_connection

# ---------------------------
# Повертає ID типу взаємодії "Лайк"
# ---------------------------
def get_like_type_id():
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id FROM interaction_types WHERE name = %s"
    cursor.execute(query, ("Лайк",))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None


# ---------------------------
# Повертає ID типу взаємодії "Дизлайк"
# ---------------------------
def get_dislike_type_id():
    conn = get_connection()
    cursor = conn.cursor()

    query = "SELECT id FROM interaction_types WHERE name = %s"
    cursor.execute(query, ("Дизлайк",))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result[0] if result else None


# ---------------------------
# Додає взаємодію в interaction_history
# ---------------------------
def add_interaction(evaluator_id: int, evaluated_id: int, interaction_type_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO interaction_history (evaluator_id, evaluated_id, interaction_type_id)
            VALUES (%s, %s, %s)
        """, (evaluator_id, evaluated_id, interaction_type_id))
        conn.commit()
        return True
    except Exception as e:
        logging.exception(e)
        return False
    finally:
        cursor.close()
        conn.close()