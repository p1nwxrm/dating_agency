import asyncio
import logging
from aiogram import Bot
from database.db import get_connection
from config import USERNAME_CHECK_INTERVAL

# ---------------------------
# Перевірка оновлення username
# ---------------------------
async def update_all_usernames(bot: Bot):
    logging.info("🔍 Починаю перевірку актуальності username користувачів...")

    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    cursor.execute("SELECT id, tg_username FROM users")
    users = cursor.fetchall()

    updated = 0
    skipped = 0

    for user in users:
        user_id = user["id"]
        old_username = user["tg_username"]

        try:
            chat = await bot.get_chat(user_id)
            new_username = chat.username  # може бути None, якщо користувач видалив username

            if old_username != new_username:
                cursor.execute(
                    "UPDATE users SET tg_username = %s WHERE id = %s",
                    (new_username, user_id)
                )
                conn.commit()
                logging.info(f"🔄 Оновлено username: {old_username} → {new_username}")
                updated += 1
            else:
                skipped += 1

        except Exception as e:
            logging.warning(f"⚠️ Не вдалося отримати інформацію для user_id={user_id}: {e}")

    cursor.close()
    conn.close()

    logging.info(f"✅ Перевірку завершено. Оновлено: {updated}, без змін: {skipped}")

# ---------------------------
# Фонова перевірка юзернеймів кожні 4 години
# ---------------------------
async def check_usernames_periodically(bot: Bot):
    while True:
        try:
            await update_all_usernames(bot)
        except Exception as e:
            logging.error(f"Помилка при оновленні username: {e}")
        await asyncio.sleep(USERNAME_CHECK_INTERVAL)