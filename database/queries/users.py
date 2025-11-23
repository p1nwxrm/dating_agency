import logging
from ..db import get_connection

# --------------------------------------
# Повертає роль користувача
# --------------------------------------
def get_user_role(user_id: int) -> int:
    """
    1 — Адміністратор
    2 — Модератор
    3 — Користувач
    """

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("SELECT role_id FROM users WHERE id = %s", (user_id,))
    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row["role_id"] if row else 3


# --------------------------------------
# Перевіряє, чи існує користувач у таблиці users
# --------------------------------------
def user_exists(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("SELECT id FROM users WHERE id = %s", (user_id,))
    result = cursor.fetchone()

    cursor.close()
    conn.close()

    return result is not None

# ---------------------------
# Додає нового користувача до БД
# ---------------------------
def add_new_user(user_id: int, username: str, role_id: int = 3):
    # Повертає True, якщо користувача додано, False — якщо сталася помилка.
    conn = get_connection()
    cursor = conn.cursor()

    try:
        cursor.execute(
            "INSERT INTO users (id, tg_username, role_id) VALUES (%s, %s, %s)",
            (user_id, username, role_id)
        )
        conn.commit()
        return True
    except Exception as e:
        logging.exception(e)
        return False
    finally:
        cursor.close()
        conn.close()


# --------------------------------------
# Отримання користувача
# --------------------------------------
def get_user(identifier):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    if isinstance(identifier, int):
        cursor.execute("""
            SELECT u.id, u.tg_username, r.name AS role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.id = %s
        """, (identifier,))
    else:
        cursor.execute("""
            SELECT u.id, u.tg_username, r.name AS role_name
            FROM users u
            JOIN roles r ON u.role_id = r.id
            WHERE u.tg_username = %s
        """, (identifier,))

    user = cursor.fetchone()
    cursor.close()
    conn.close()
    return user