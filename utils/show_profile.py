from database.db import get_connection
from aiogram import Bot
from aiogram.types import InputMediaPhoto

# ---------------------------
# Універсальна функція для відображення анкети
# ---------------------------
async def show_profile(bot: Bot, chat_id: int, user_id: int, show_username: bool = False):
    conn = get_connection()
    cursor = conn.cursor(dictionary = True)

    # Отримуємо дані анкети
    cursor.execute("""
        SELECT p.id, p.name, p.age, p.city, p.description, u.tg_username
        FROM profiles p
        JOIN users u ON p.user_id = u.id
        WHERE u.id = %s
    """, (user_id,))
    profile = cursor.fetchone()

    # Якщо анкети немає
    if not profile:
        await bot.send_message(chat_id, "❌ Анкету не знайдено.")
        cursor.close()
        conn.close()
        return

    # Отримуємо фото
    cursor.execute("SELECT photo_url FROM profile_photos WHERE profile_id = %s", (profile["id"],))
    photos = cursor.fetchall()

    cursor.close()
    conn.close()

    # Формуємо текст анкети
    text = ""
    if show_username and profile.get("tg_username"):
        text += f"@{profile['tg_username']}\n\n"

    text += f"{profile['name']}, {profile['age']}, {profile['city']}"
    if profile.get("description"):
        text += f" — {profile['description']}"

    # Відправляємо фото або тільки текст
    if photos:
        media = [InputMediaPhoto(media = p["photo_url"]) for p in photos]
        media[0].caption = text
        await bot.send_media_group(chat_id, media)
    else:
        await bot.send_message(chat_id, text)