from aiogram import Bot
from database.db import get_connection

# ---------------------------
# Універсальна функція для відображення статистики модератора
# ---------------------------
async def show_moderator_stats(bot: Bot, chat_id: int, user_id: int):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    # Отримуємо юзернейм модератора
    cursor.execute("SELECT tg_username FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    moderator_name = user["tg_username"] if user else f"ID {user_id}"

    # Підрахунок банів
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM bans
        JOIN actions_on_users ON bans.action_id = actions_on_users.id
        WHERE bans.reviewer_id = %s AND actions_on_users.name = 'Бан'
    """, (user_id,))
    bans_count = cursor.fetchone()["count"]

    # Підрахунок розбанів
    cursor.execute("""
        SELECT COUNT(*) AS count
        FROM bans
        JOIN actions_on_users ON bans.action_id = actions_on_users.id
        WHERE bans.reviewer_id = %s AND actions_on_users.name = 'Розбан'
    """, (user_id,))
    unbans_count = cursor.fetchone()["count"]

    # Підрахунок переглянутих скарг (інформативні / неінформативні)
    cursor.execute("""
        SELECT 
            SUM(is_informative = TRUE) AS informative,
            SUM(is_informative = FALSE) AS non_informative
        FROM complaint_reviews
        WHERE reviewer_id = %s
    """, (user_id,))
    reviews = cursor.fetchone()
    informative = reviews["informative"] or 0
    non_informative = reviews["non_informative"] or 0
    total_reviews = informative + non_informative

    cursor.close()
    conn.close()

    # Обчислення відсотків
    informative_pct = (informative / total_reviews * 100) if total_reviews > 0 else 0
    non_informative_pct = (non_informative / total_reviews * 100) if total_reviews > 0 else 0

    # Формування тексту відповіді
    text = (
	    f"👮‍♂️ Статистика модератора @{moderator_name}\n\n"
	    f"🔒 Заблоковано користувачів: {bans_count}\n"
	    f"🔓 Розблоковано користувачів: {unbans_count}\n\n"
	    f"📋 Переглянуто скарг: {total_reviews}\n"
	    f"💡 Інформативних: {informative} ({informative_pct:.1f}%)\n"
	    f"💤 Неінформативних: {non_informative} ({non_informative_pct:.1f}%)"
    )

    await bot.send_message(chat_id, text)