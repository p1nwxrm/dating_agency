from aiogram.fsm.state import State, StatesGroup

class AdminPanel(StatesGroup):
    main_menu = State()
    view_stats = State()
    view_staff = State()
