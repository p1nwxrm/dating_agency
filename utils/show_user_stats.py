from aiogram import Bot
from database.db import get_connection

# ---------------------------
# Універсальна функція для відображення статистики анкети
# ---------------------------
async def show_user_stats(bot: Bot, chat_id: int, user_id: int = None, username: str = None):
    # Якщо user_id і username не задані — бере поточного користувача з message.
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    # --- Визначаємо користувача ---
    if user_id:
        cursor.execute("SELECT id, tg_username FROM users WHERE id = %s", (user_id,))
    elif username:
        cursor.execute("SELECT id, tg_username FROM users WHERE tg_username = %s", (username,))
    else:
        await bot.send_message(chat_id, "❌ Не вказано користувача для перегляду статистики.")
        return

    user = cursor.fetchone() or {}
    if not user:
        await bot.send_message(chat_id, "❌ Користувача не знайдено у базі даних.")
        cursor.close()
        conn.close()
        return

    user_id = user["id"]

    # --- Профіль і підписка ---
    cursor.execute("""
        SELECT p.id, p.is_active, s.name AS subscription_name
        FROM profiles p
        JOIN subscription_types s ON p.subscription_type_id = s.id
        WHERE p.user_id = %s
    """, (user_id,))

    profile = cursor.fetchone() or {}

    if not profile:
        await bot.send_message(chat_id, "❌ У користувача немає створеної анкети.")
        cursor.close()
        conn.close()
        return

    # --- Отримані лайки/дизлайки ---
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN interaction_type_id = (SELECT id FROM interaction_types WHERE name = 'Лайк') THEN 1 ELSE 0 END) AS received_likes,
            SUM(CASE WHEN interaction_type_id = (SELECT id FROM interaction_types WHERE name = 'Дизлайк') THEN 1 ELSE 0 END) AS received_dislikes,
            COUNT(*) AS total_received
        FROM interaction_history
        WHERE evaluated_id = %s
    """, (user_id,))
    received = cursor.fetchone() or {}

    # --- Поставлені лайки/дизлайки ---
    cursor.execute("""
        SELECT 
            SUM(CASE WHEN interaction_type_id = (SELECT id FROM interaction_types WHERE name = 'Лайк') THEN 1 ELSE 0 END) AS given_likes,
            SUM(CASE WHEN interaction_type_id = (SELECT id FROM interaction_types WHERE name = 'Дизлайк') THEN 1 ELSE 0 END) AS given_dislikes,
            COUNT(*) AS total_viewed
        FROM interaction_history
        WHERE evaluator_id = %s
    """, (user_id,))
    given = cursor.fetchone() or {}

    # --- Кількість скарг ---
    cursor.execute("""
        SELECT 
            (SELECT COUNT(*) FROM complaints WHERE applicant_id = %s) AS submitted_complaints,
            (SELECT COUNT(*) FROM complaints WHERE violator_id = %s) AS received_complaints
    """, (user_id, user_id))
    complaints = cursor.fetchone() or {}

    # --- Обчислення відсотків ---
    total_received = received["total_received"] or 0
    received_likes = received["received_likes"] or 0
    received_dislikes = received["received_dislikes"] or 0
    if total_received > 0:
        received_like_percent = round(received_likes / total_received * 100, 1)
        received_dislike_percent = round(received_dislikes / total_received * 100, 1)
    else:
        received_like_percent = received_dislike_percent = 0.0

    total_viewed = given["total_viewed"] or 0
    given_likes = given["given_likes"] or 0
    given_dislikes = given["given_dislikes"] or 0
    if total_viewed > 0:
        given_like_percent = round(given_likes / total_viewed * 100, 1)
        given_dislike_percent = round(given_dislikes / total_viewed * 100, 1)
    else:
        given_like_percent = given_dislike_percent = 0.0

    # --- Формуємо текст ---
    text = (
        f"📊 Статистика користувача @{user['tg_username']}\n\n"
        f"🔸 Статус анкети: {'🟢 Активна' if profile['is_active'] else '🔴 Неактивна'}\n"
        f"💎 Підписка: {profile['subscription_name']}\n\n"
        f"❤️ Отримано лайків: {received_likes}\n"
        f"💔 Отримано дизлайків: {received_dislikes}\n"
        f"📈 Відсоток реакцій:\n❤️ {received_like_percent}% | 💔 {received_dislike_percent}%\n\n"
        f"👍 Поставлено лайків: {given_likes}\n"
        f"👎 Поставлено дизлайків: {given_dislikes}\n"
        f"👀 Переглянуто анкет: {total_viewed}\n"
        f"📊 Відсоток реакцій:\n👍 {given_like_percent}% | 👎 {given_dislike_percent}%\n\n"
        f"📨 Подані скарги: {complaints['submitted_complaints'] or 0}\n"
        f"🚫 Отримані скарги: {complaints['received_complaints'] or 0}"
    )
    await bot.send_message(chat_id, text)

    cursor.close()
    conn.close()