from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from database.queries import get_admins_and_moderators
from utils.show_moderator_stats import show_moderator_stats
from states.admin_states import AdminPanel
from show_menus.admins.main_menu import show_admin_main_menu

router = Router()

# --------------------------------------
# Обробка кнопки "👑 Адміни та модератори"
# --------------------------------------
@router.message(AdminPanel.main_menu, F.text == "👑 Адміни та модератори")
async def show_staff_list(message: types.Message, state: FSMContext):
	# Отримуємо список адміністраторів та модераторів
	staff = get_admins_and_moderators()

	# Якщо таблиця пуста (теоретично)
	if not staff:
		await message.answer("Немає жодного адміністратора або модератора у системі.")
		await show_admin_main_menu(message.bot, message.chat.id)
		await state.set_state(AdminPanel.main_menu)
		return

	# Формуємо текст списку
	admins_text = "🛡 Адміністратори:\n"
	moderators_ids = []

	for person in staff:
		if person["role_name"] == "Адміністратор":
			admins_text += f"• @{person['tg_username']} (ID {person['id']})\n"
		else:
			moderators_ids.append(person["id"])

	if admins_text.strip() == "🛡 Адміністратори:":
		admins_text += "• Немає\n"

	await message.answer(admins_text)

	# Виводимо статистику кожного модератора
	if moderators_ids:
		for mod_id in moderators_ids:
			await show_moderator_stats(bot = message.bot, chat_id = message.chat.id, user_id = mod_id)
	else:
		await message.answer("‍👮‍♂️ Наразі немає жодного модератора.")

	# Повертаємося до головного меню
	await show_admin_main_menu(message.bot, message.chat.id)
	await state.set_state(AdminPanel.main_menu)