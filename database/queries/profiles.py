from ..db import get_connection

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
# Отримання інформації про користувача
# ---------------------------
def get_about_info(identifier):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    if isinstance(identifier, int):
        # Якщо передано user_id
        cursor.execute("""
            SELECT description
            FROM profiles
            WHERE user_id = %s
        """, (identifier,))
    else:
        # Якщо передано username
        cursor.execute("""
            SELECT p.description
            FROM profiles p
            JOIN users u ON p.user_id = u.id
            WHERE u.tg_username = %s
        """, (identifier,))

    row = cursor.fetchone()

    cursor.close()
    conn.close()

    return row["description"] if row and row["description"] else None


# --------------------------------------
# Отримання профілю
# --------------------------------------
def get_profile(identifier):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    if isinstance(identifier, int):
        # Пошук по user_id
        cursor.execute("""
            SELECT 
                p.id,
                p.user_id,
                p.name,
                p.age,
                p.gender_id,
                p.goal_id,
                p.city,
                p.description,
                p.is_active,
                p.search_radius_km,
                p.subscription_type_id
            FROM profiles p
            WHERE p.user_id = %s
        """, (identifier,))

    else:
        # Пошук по username
        cursor.execute("""
            SELECT 
                p.id,
                p.user_id,
                p.name,
                p.age,
                p.gender_id,
                p.goal_id,
                p.city,
                p.description,
                p.is_active,
                p.search_radius_km,
                p.subscription_type_id
            FROM profiles p
            JOIN users u ON p.user_id = u.id
            WHERE u.tg_username = %s
        """, (identifier,))

    profile = cursor.fetchone()

    cursor.close()
    conn.close()

    return profile


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