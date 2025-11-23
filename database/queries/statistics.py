from ..db import get_connection

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