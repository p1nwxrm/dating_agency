from aiogram.fsm.state import State, StatesGroup

class ModeratorPanel(StatesGroup):
    main_menu = State()
    view_stats = State()