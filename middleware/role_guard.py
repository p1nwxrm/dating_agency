import logging

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from database.queries import get_user_role
from handlers.common.start import cmd_start

# ---------------------------
# Middleware перевірки ролі
# ---------------------------
class RoleGuardMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        """
            1 — Адміністратор
            2 — Модератор
            3 — Користувач
        """

        state: FSMContext = data.get("state")

        # Поддержка как сообщений, так и коллбеков
        if isinstance(event, (Message, CallbackQuery)):
            user_id = event.from_user.id

            real_role = get_user_role(user_id)
            current_state = await state.get_state()

            if not current_state:
                current_role = 3
            else:
                if current_state.startswith("AdminPanel"):
                    current_role = 1
                elif current_state.startswith("ModeratorPanel"):
                    current_role = 2
                else:
                    current_role = 3

            # Якщо ролі не співпадають — очищаємо FSM і перенаправляємо в потрібне меню
            if current_role is not None and real_role != current_role:
                try:
                    # Очищаємо FSM
                    await state.clear()
                except Exception as e:
                    logging.exception(f"RoleGuardMiddleware: не вдалося очистити state для user_id={user_id}")

                # Визначаємо об’єкт message для callback
                message_obj = event.message if isinstance(event, CallbackQuery) else event

                # Викликаємо cmd_start, щоб користувач потрапив у відповідне меню
                try:
                    await cmd_start(message_obj, state)
                except Exception as e:
                    logging.exception(f"RoleGuardMiddleware: помилка при виклику cmd_start для user_id={user_id}")

                # Після цього не передаємо далі handler, бо ми вже перенаправили користувача
                return

        # Якщо роль збігається або event не Message/CallbackQuery — передаємо далі
        return await handler(event, data)