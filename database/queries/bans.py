import logging
from ..db import get_connection

# --------------------------------------
# Отримання ID дії "Бан"
# --------------------------------------
def get_ban_action_id() -> int | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        cursor.execute("""
            SELECT id
            FROM actions_on_users
            WHERE name = 'Бан'
            LIMIT 1
        """)
        row = cursor.fetchone()
        return row["id"] if row else None

    except Exception as e:
        logging.exception(e)

    finally:
        cursor.close()
        conn.close()


# --------------------------------------
# Отримання ID дії "Розбан"
# --------------------------------------
def get_unban_action_id() -> int | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        cursor.execute("""
            SELECT id
            FROM actions_on_users
            WHERE name = 'Розбан'
            LIMIT 1
        """)
        row = cursor.fetchone()
        return row["id"] if row else None

    except Exception as e:
        logging.exception(e)

    finally:
        cursor.close()
        conn.close()

# --------------------------------------
# Перевірка статусу бану
# --------------------------------------
def is_user_banned(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("""
        SELECT action_id
        FROM bans
        WHERE user_id = %s
        ORDER BY id DESC
        LIMIT 1
    """, (user_id,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    if not row:
        return False  # нема записів - нема бана

    return row["action_id"] == get_ban_action_id()

# --------------------------------------
# Бан користувача
# --------------------------------------
def ban_user(reviewer_id: int, user_id: int, reason_id: int, extra_info: str = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)

    try:
        # Проверяем состояние последней записи (если action_id = 1 → пользователь уже в бане)
        cursor.execute("""
            SELECT action_id
            FROM bans
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()

        ban_action_id = get_ban_action_id()

        if row and row["action_id"] == ban_action_id:
            cursor.close()
            conn.close()
            return False  # уже забанен

        # Определяем роль модератора/админа
        cursor.execute("""
            SELECT role_id
            FROM users
            WHERE id = %s
        """, (reviewer_id,))
        reviewer = cursor.fetchone()

        if not reviewer:
            cursor.close()
            conn.close()
            return False

        executor_role_id = reviewer["role_id"]

        cursor.execute("""
            INSERT INTO bans (user_id, reviewer_id, executor_role_id, action_id, reason_id, extra_info)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, reviewer_id, executor_role_id, ban_action_id, reason_id, extra_info))

        conn.commit()
        return True

    except Exception as e:
        logging.exception(e)
        return False

    finally:
        cursor.close()
        conn.close()


# --------------------------------------
# Розбан користувача
# --------------------------------------
def unban_user(reviewer_id: int, user_id: int, reason_id: int = None, extra_info: str = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        # Проверяем, есть ли активный бан
        cursor.execute("""
            SELECT action_id
            FROM bans
            WHERE user_id = %s
            ORDER BY id DESC
            LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()

        unban_action_id = get_unban_action_id()

        if not row or row["action_id"] == unban_action_id:
            cursor.close()
            conn.close()
            return False  # пользователя нет в бане → некого разбанивать

        # Определяем роль, с которой действует модератор/админ
        cursor.execute("""
            SELECT role_id
            FROM users
            WHERE id = %s
        """, (reviewer_id,))
        reviewer = cursor.fetchone()

        if not reviewer:
            cursor.close()
            conn.close()
            return False

        executor_role_id = reviewer["role_id"]

        cursor.execute("""
            INSERT INTO bans (user_id, reviewer_id, executor_role_id, action_id, reason_id, extra_info)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, reviewer_id, executor_role_id, unban_action_id, reason_id, extra_info))

        conn.commit()
        return True

    except Exception as e:
        logging.exception(e)
        return False

    finally:
        cursor.close()
        conn.close()


# --------------------------------------
# Отримати інформацію про бан користувача
# --------------------------------------
def get_ban_info(user_id: int) -> dict | None:
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    try:
        # Беремо останній запис про бан користувача
        cursor.execute("""
            SELECT b.id, b.reviewer_id, b.reason_id, b.extra_info, b.datetime, a.name AS action_name, r.name AS reason_name
            FROM bans b
            JOIN actions_on_users a ON b.action_id = a.id
            JOIN reasons r ON b.reason_id = r.id
            WHERE b.user_id = %s
            ORDER BY b.id DESC
            LIMIT 1
        """, (user_id,))
        row = cursor.fetchone()

        if not row:
            return None  # користувача взагалі не банили

        # Перевірка: активний бан чи вже розбанений
        if row["action_name"] == "Розбан":
            return None

        return {
            "reason_name": row["reason_name"],
            "extra_info": row.get("extra_info"),
            "reviewer_id": row["reviewer_id"],
            "datetime": row["datetime"]
        }

    except Exception as e:
        logging.exception(e)
        return None

    finally:
        cursor.close()
        conn.close()