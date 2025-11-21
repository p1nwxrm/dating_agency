from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Dict

from database.db import get_connection

class UsernameCheckMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data: Dict):
        user = None

        # Підтримка Message та CallbackQuery
        if isinstance(event, (Message, CallbackQuery)):
            user = event.from_user

        if user:
            user_id = user.id
            new_username = user.username

            conn = get_connection()
            cursor = conn.cursor(dictionary = True)

            cursor.execute("SELECT tg_username FROM users WHERE id = %s", (user_id,))
            row = cursor.fetchone()

            if row:
                old_username = row["tg_username"]

                if old_username != new_username:
                    cursor.execute(
                        "UPDATE users SET tg_username = %s WHERE id = %s",
                        (new_username, user_id)
                    )
                    conn.commit()

            cursor.close()
            conn.close()

        return await handler(event, data)