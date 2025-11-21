from aiogram.fsm.state import State, StatesGroup

class Registration(StatesGroup):
    set_name = State()
    set_age = State()
    set_gender = State()
    set_goal = State()
    set_desired_genders = State()
    set_location = State()
    set_search_radius = State()
    set_photos = State()
    set_about_info = State()
    save_to_db = State()

class UserMenu(StatesGroup):
    main_menu = State()
    status_menu = State()
    rate_menu = State()
    complaints_menu = State()
    other_complaints = State()