from ..db import get_connection

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