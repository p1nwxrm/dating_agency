from aiogram.fsm.state import State, StatesGroup

class ModeratorPanel(StatesGroup):
    main_menu = State()

class ModeratorBan(StatesGroup):
    enter_username = State()
    choose_reason = State()
    other_reason = State()