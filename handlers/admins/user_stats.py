from aiogram import Router, F, types
from aiogram.fsm.context import FSMContext
from states.admin_states import AdminPanel
from database.queries import get_global_statistics
from .show_menus import show_admin_main_menu

router = Router()

@router.message(AdminPanel.main_menu, F.text == "📊 Статистика")
async def admin_statistics(message: types.Message, state: FSMContext):
    stats = get_global_statistics()

    t_users = stats["total_users"]

    # Розподіл користувачів за статтю
    genders_text = ""
    for name, count in stats["gender_stats"]:
        percent = round((count / t_users * 100), 1) if t_users else 0
        genders_text += f"• {name}: {count} ({percent}%)\n"

    # Реакції (лайки та дизлайки)
    likes = next((c for n, c in stats["reaction_stats"] if n == "Лайк"), 0)
    dislikes = next((c for n, c in stats["reaction_stats"] if n == "Дизлайк"), 0)
    ti = stats["total_interactions"]

    likes_pct = round(likes / ti * 100, 1) if ti else 0
    dislikes_pct = round(dislikes / ti * 100, 1) if ti else 0

    # Скарги користувачів
    total_complaints = stats["total_complaints"]
    reviewed = stats["reviewed_complaints"]

    reviewed_pct = round(reviewed / total_complaints * 100, 1) if total_complaints else 0

    informative = stats["informative"]
    informative_pct = round(informative / reviewed * 100, 1) if reviewed else 0

    non_informative = stats["non_informative"]
    non_informative_pct = round(non_informative / reviewed * 100, 1) if reviewed else 0

    # ---------------------------
    # Підсумковий текст
    # ---------------------------
    text = (
        "📊 Загальна статистика користувачів\n\n"

        f"👥 Користувачів всього: {t_users}"
    )

    if t_users:
        text += (
            "\n\n🧬 Розподіл за статтю:\n"
            f"{genders_text}\n"
            f"🔄 Взаємодій всього: {ti}"
        )

        if ti:
            text +=(
                f"\n\n👍 Лайків: {likes} ({likes_pct}%)\n"
                f"👎 Дизлайків: {dislikes} ({dislikes_pct}%)\n\n"
                f"💞 Взаємних симпатій (метчів): {stats['matches']}\n"

            )

            if total_complaints:
                text += (
                    f"\n📝 Скарг всього: {total_complaints}"
                    f"\n👀 Переглянуто: {reviewed} ({reviewed_pct}%)\n\n"
                    f"✅ Інформативних: {informative} ({informative_pct}%)\n"
                    f"❌ Неінформативних: {non_informative} ({non_informative_pct}%)\n"
                )
            else:
                text += f"📝 Скарг всього: {total_complaints}"

    await message.answer(text)
    await show_admin_main_menu(message.bot, message.chat.id)
    await state.set_state(AdminPanel.main_menu)