from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from i18n import t

def language_keyboard():
    """3-button language selector"""
    buttons = [
        [InlineKeyboardButton("🇷🇴 Română", callback_data="lang_ro"),
         InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")]
    ]
    return InlineKeyboardMarkup(buttons)

def gender_keyboard(lang: str):
    """Gender selection"""
    buttons = [
        [InlineKeyboardButton(t(lang, "gender_male"), callback_data="gender_male"),
         InlineKeyboardButton(t(lang, "gender_female"), callback_data="gender_female")]
    ]
    return InlineKeyboardMarkup(buttons)

def goal_keyboard(lang: str):
    """5 goal options"""
    buttons = [
        [InlineKeyboardButton(t(lang, "goal_lose_weight"), callback_data="goal_lose")],
        [InlineKeyboardButton(t(lang, "goal_gain_muscle"), callback_data="goal_muscle")],
        [InlineKeyboardButton(t(lang, "goal_maintain"), callback_data="goal_maintain")],
        [InlineKeyboardButton(t(lang, "goal_endurance"), callback_data="goal_endurance")],
        [InlineKeyboardButton(t(lang, "goal_general_fitness"), callback_data="goal_fitness")]
    ]
    return InlineKeyboardMarkup(buttons)

def gym_frequency_keyboard(lang: str):
    """1-7 days per week"""
    buttons = []
    for i in range(1, 8):
        buttons.append(InlineKeyboardButton(str(i), callback_data=f"freq_{i}"))
    return InlineKeyboardMarkup([buttons])

def gym_duration_keyboard(lang: str):
    """Duration options: 30/45/60/90/120"""
    buttons = [
        [InlineKeyboardButton("30 min", callback_data="dur_30"),
         InlineKeyboardButton("45 min", callback_data="dur_45"),
         InlineKeyboardButton("60 min", callback_data="dur_60")],
        [InlineKeyboardButton("90 min", callback_data="dur_90"),
         InlineKeyboardButton("120 min", callback_data="dur_120")]
    ]
    return InlineKeyboardMarkup(buttons)

def fitness_level_keyboard(lang: str):
    """Beginner/Intermediate/Advanced"""
    buttons = [
        [InlineKeyboardButton(t(lang, "fitness_beginner"), callback_data="fit_beginner")],
        [InlineKeyboardButton(t(lang, "fitness_intermediate"), callback_data="fit_intermediate")],
        [InlineKeyboardButton(t(lang, "fitness_advanced"), callback_data="fit_advanced")]
    ]
    return InlineKeyboardMarkup(buttons)

def diet_keyboard(lang: str):
    """5 diet options"""
    buttons = [
        [InlineKeyboardButton(t(lang, "diet_none"), callback_data="diet_none")],
        [InlineKeyboardButton(t(lang, "diet_vegetarian"), callback_data="diet_vegetarian")],
        [InlineKeyboardButton(t(lang, "diet_vegan"), callback_data="diet_vegan")],
        [InlineKeyboardButton(t(lang, "diet_keto"), callback_data="diet_keto")],
        [InlineKeyboardButton(t(lang, "diet_halal"), callback_data="diet_halal")]
    ]
    return InlineKeyboardMarkup(buttons)

def water_goal_keyboard(lang: str):
    """Water goal: 6/8/10/12 glasses"""
    buttons = [
        [InlineKeyboardButton("6", callback_data="water_6"),
         InlineKeyboardButton("8", callback_data="water_8"),
         InlineKeyboardButton("10", callback_data="water_10"),
         InlineKeyboardButton("12", callback_data="water_12")]
    ]
    return InlineKeyboardMarkup(buttons)

def main_menu_keyboard(lang: str):
    """Main menu reply keyboard"""
    buttons = [
        [KeyboardButton(t(lang, "btn_gym")),
         KeyboardButton(t(lang, "btn_food"))],
        [KeyboardButton(t(lang, "btn_progress")),
         KeyboardButton(t(lang, "btn_stats"))],
        [KeyboardButton(t(lang, "btn_settings"))]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)

def gym_menu_keyboard(lang: str):
    """Gym session menu"""
    buttons = [
        [InlineKeyboardButton(t(lang, "add_exercise"), callback_data="add_ex")],
        [InlineKeyboardButton(t(lang, "view_today"), callback_data="view_ex")],
        [InlineKeyboardButton(t(lang, "exercise_done"), callback_data="finish_gym")]
    ]
    return InlineKeyboardMarkup(buttons)

def food_action_keyboard(lang: str):
    """Food analysis actions"""
    buttons = [
        [InlineKeyboardButton(t(lang, "record_meal"), callback_data="record_food"),
         InlineKeyboardButton(t(lang, "edit_meal"), callback_data="edit_food")],
        [InlineKeyboardButton(t(lang, "skip_meal"), callback_data="skip_food")]
    ]
    return InlineKeyboardMarkup(buttons)

def sets_keyboard():
    """1-6 sets"""
    buttons = [[InlineKeyboardButton(str(i), callback_data=f"sets_{i}") for i in range(1, 7)]]
    return InlineKeyboardMarkup(buttons)

def reps_keyboard():
    """Common rep ranges"""
    reps = [5, 6, 8, 10, 12, 15, 20]
    buttons = [[InlineKeyboardButton(str(r), callback_data=f"reps_{r}") for r in reps]]
    return InlineKeyboardMarkup(buttons)

def intensity_keyboard(lang: str):
    """Easy/Medium/Hard"""
    buttons = [
        [InlineKeyboardButton("Easy", callback_data="int_easy"),
         InlineKeyboardButton("Medium", callback_data="int_medium"),
         InlineKeyboardButton("Hard", callback_data="int_hard")]
    ]
    return InlineKeyboardMarkup(buttons)

def confirm_keyboard(lang: str):
    """Yes/No confirmation"""
    buttons = [
        [InlineKeyboardButton("✅ Yes", callback_data="confirm_yes"),
         InlineKeyboardButton("❌ No", callback_data="confirm_no")]
    ]
    return InlineKeyboardMarkup(buttons)

def back_keyboard(lang: str):
    """Back button"""
    buttons = [[InlineKeyboardButton(t(lang, "back"), callback_data="back")]]
    return InlineKeyboardMarkup(buttons)
