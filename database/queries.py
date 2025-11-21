from .db import get_connection
import logging

# ---------------------------
# Отримання фото з БД
# ---------------------------
def get_existing_photos(username: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("""
        SELECT pp.photo_url
        FROM profile_photos pp
        JOIN profiles p ON pp.profile_id = p.id
        JOIN users u ON p.user_id = u.id
        WHERE u.tg_username = %s
    """, (username,))

    photos = cursor.fetchall()

    cursor.close()
    conn.close()

    return photos

# ---------------------------
# Отримання списку гендерів
# ---------------------------
def get_genders():
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("SELECT id, name FROM genders ORDER BY id")
    genders = cursor.fetchall()

    cursor.close()
    conn.close()

    return genders

# ---------------------------
# Отримання інформації про користувача
# ---------------------------
def get_about_info(username: str):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("""
                SELECT p.description
                FROM profiles p
                JOIN users u ON p.user_id = u.id
                WHERE u.tg_username = %s
            """, (username,))

    profile = cursor.fetchone()
    cursor.close()
    conn.close()

    about = profile["description"] if profile and profile["description"] else None
    return about

# ---------------------------
# Отримання списку цілей знайомтсва
# ---------------------------
def get_dating_goals():
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("SELECT id, name FROM dating_goals ORDER BY id")
    goals = cursor.fetchall()

    cursor.close()
    conn.close()

    return goals

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
# Отримання загальної статистики про всіх користувачів
# ---------------------------
def get_global_statistics():
    conn = get_connection()
    cursor = conn.cursor()

    # 1 — Загальна кількість користувачів
    cursor.execute("SELECT COUNT(*) FROM profiles")
    total_users = cursor.fetchone()[0]

    # 2 — Кількість користувачів за статтю
    cursor.execute("""
        SELECT g.name, COUNT(*)
        FROM profiles p
        JOIN genders g ON g.id = p.gender_id
        GROUP BY g.name
    """)
    gender_stats = cursor.fetchall()  # [('Чоловіча', 100), ('Жіноча', 80), ...]

    # 3 — Загальна кількість взаємодій
    cursor.execute("SELECT COUNT(*) FROM interaction_history")
    total_interactions = cursor.fetchone()[0]

    # 4 — Лайки та дизлайки
    cursor.execute("""
        SELECT it.name, COUNT(*)
        FROM interaction_history ih
        JOIN interaction_types it ON it.id = ih.interaction_type_id
        GROUP BY it.name
    """)
    reaction_stats = cursor.fetchall()  # [('Лайк', 120), ('Дизлайк', 40)]

    # 5 — Загальна кількість метчів (= взаємних лайків)
    cursor.execute("""
        SELECT COUNT(DISTINCT CONCAT(LEAST(ih.evaluator_id, ih.evaluated_id), ':', GREATEST(ih.evaluator_id, ih.evaluated_id))) AS matches
        FROM interaction_history ih
        JOIN (
            -- знаходимо "наступну" подію для тієї ж пари
            SELECT ih1.id AS id, (
                SELECT ih2.id
                FROM interaction_history ih2
                WHERE LEAST(ih2.evaluator_id, ih2.evaluated_id) = LEAST(ih1.evaluator_id, ih1.evaluated_id)
                  AND GREATEST(ih2.evaluator_id, ih2.evaluated_id) = GREATEST(ih1.evaluator_id, ih1.evaluated_id)
                  AND ih2.datetime > ih1.datetime
                ORDER BY ih2.datetime
                LIMIT 1
            ) AS next_id
            FROM interaction_history ih1
        ) nxt ON nxt.id = ih.id
        JOIN interaction_history ih_next ON ih_next.id = nxt.next_id
        WHERE ih.interaction_type_id = 1
          AND ih_next.interaction_type_id = 1
          AND ih.evaluator_id <> ih_next.evaluator_id;
    """)
    matches = cursor.fetchone()[0]

    # 6 — Загальна кількість скарг
    cursor.execute("SELECT COUNT(*) FROM complaints")
    total_complaints = cursor.fetchone()[0]

    # 7 — Переглянуті скарги
    cursor.execute("SELECT COUNT(*) FROM complaint_reviews")
    reviewed_complaints = cursor.fetchone()[0]

    # 8 — Інформативні та неінформативні скарги
    cursor.execute("""
        SELECT 
            SUM(is_informative = 1),
            SUM(is_informative = 0)
        FROM complaint_reviews
    """)
    informative, non_informative = cursor.fetchone()

    cursor.close()
    conn.close()

    return {
        "total_users": total_users,
        "gender_stats": gender_stats,
        "total_interactions": total_interactions,
        "reaction_stats": reaction_stats,
        "matches": matches,
        "total_complaints": total_complaints,
        "reviewed_complaints": reviewed_complaints,
        "informative": informative or 0,
        "non_informative": non_informative or 0,
    }

# --------------------------------------
# Отримуємо список адміністраторів та модераторів
# --------------------------------------
def get_admins_and_moderators():
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("""
        SELECT users.id, users.tg_username, roles.name AS role_name
        FROM users
        JOIN roles ON users.role_id = roles.id
        WHERE roles.name IN ('Адміністратор', 'Модератор')
        ORDER BY roles.id ASC, users.id ASC
    """)

    staff = cursor.fetchall()
    cursor.close()
    conn.close()

    return staff

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

# --------------------------------------
# Перевіряє, чи має користувач створену анкету
# --------------------------------------
def profile_exists(user_id: int) -> bool:
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("SELECT id FROM profiles WHERE user_id = %s", (user_id,))
    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    return profile is not None

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

# ---------------------------
# Додає скаргу в БД
# ---------------------------
def send_complaint(applicant_id: int, violator_id: int, reason_id: int, extra_description: str = None) -> bool:
    conn = get_connection()
    cursor = conn.cursor()
    try:
        if extra_description:
            cursor.execute("""
                        INSERT INTO complaints (applicant_id, violator_id, reason_id, extra_description)
                        VALUES (%s, %s, %s, %s)
                    """, (applicant_id, violator_id, reason_id, extra_description))
        else:
            cursor.execute("""
                        INSERT INTO complaints (applicant_id, violator_id, reason_id)
                        VALUES (%s, %s, %s)
                    """, (applicant_id, violator_id, reason_id))
        conn.commit()
        return True
    except Exception as e:
        logging.exception(e)
        return False
    finally:
        cursor.close()
        conn.close()