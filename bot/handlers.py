from telegram import Update
from telegram.ext import ContextTypes
from database import get_user, is_onboarding_complete, get_weekly_stats, get_daily_summary
from i18n import t
from bot.keyboards import main_menu_keyboard
from bot.progress import show_daily_progress, progress_bar

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "user"

    user = await get_user(user_id)

    if user is None:
        # User doesn't exist, import and start onboarding
        from bot.onboarding import start_onboarding
        return await start_onboarding(update, context)
    elif user["onboarding_complete"] == 0:
        # Onboarding not complete, resume it
        from bot.onboarding import start_onboarding
        return await start_onboarding(update, context)
    else:
        # Onboarding complete, show main menu
        lang = user["language"] or "en"
        await context.bot.send_message(
            user_id,
            t(lang, "welcome"),
            reply_markup=main_menu_keyboard(lang),
            parse_mode="Markdown"
        )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if not user:
        await context.bot.send_message(user_id, "Please start with /start")
        return

    lang = user["language"] or "en"
    await context.bot.send_message(
        user_id,
        t(lang, "help_text"),
        parse_mode="Markdown"
    )

async def progress_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /progress command"""
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if not user:
        await context.bot.send_message(user_id, "Please start with /start")
        return

    lang = user["language"] or "en"
    await show_daily_progress(update, context, user_id, lang)

async def stats_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if not user:
        await context.bot.send_message(user_id, "Please start with /start")
        return

    lang = user["language"] or "en"

    try:
        stats = await get_weekly_stats(user_id)

        stats_msg = t(lang, "stats_weekly",
            avg_calories=stats["avg_calories"],
            total_burned=stats["total_burned"],
            sessions=stats["sessions"],
            total_volume=stats["total_volume"],
            avg_protein=stats["avg_protein"],
            avg_carbs=stats["avg_carbs"],
            avg_fat=stats["avg_fat"],
            avg_water=stats["avg_water"]
        )

        await context.bot.send_message(user_id, stats_msg, parse_mode="Markdown")
    except Exception as e:
        await context.bot.send_message(user_id, t(lang, "error", error=str(e)))

async def gym_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /gym command"""
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if not user:
        await context.bot.send_message(user_id, "Please start with /start")
        return

    lang = user["language"] or "en"

    from bot.workout import start_gym_session_cmd
    return await start_gym_session_cmd(update, context)

async def settings_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /settings command"""
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if not user:
        await context.bot.send_message(user_id, "Please start with /start")
        return

    lang = user["language"] or "en"
    settings_msg = f"""⚙️ *Your Settings*

👤 Name: {user['name']}
🎂 Age: {user['age']}
📏 Height: {user['height_cm']} cm
⚖️ Weight: {user['weight_kg']} kg
🎯 Goal: {user['goal']}
💪 Fitness Level: {user['fitness_level']}
🏋️ Gym: {user['gym_frequency']} days/week
🥗 Diet: {user['diet_preference']}
⏰ Wake: {user['wake_time']}
🌙 Sleep: {user['sleep_time']}
💧 Water Target: {user['daily_water_goal']} glasses
🔥 Daily Calories: {user['calorie_target']:.0f} kcal
🥩 Protein: {user['protein_target']:.0f}g
🍞 Carbs: {user['carbs_target']:.0f}g
🧈 Fat: {user['fat_target']:.0f}g
"""
    await context.bot.send_message(user_id, settings_msg, parse_mode="Markdown")

async def text_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle text messages (menu buttons)"""
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if not user:
        await context.bot.send_message(user_id, "Please start with /start")
        return

    lang = user["language"] or "en"
    text = update.message.text

    # Build button texts from i18n for the current language
    gym_btn = t(lang, "btn_gym")
    food_btn = t(lang, "btn_food")
    progress_btn = t(lang, "btn_progress")
    stats_btn = t(lang, "btn_stats")
    settings_btn = t(lang, "btn_settings")

    # Check button presses
    if text == gym_btn:
        from bot.workout import start_gym_session_cmd
        return await start_gym_session_cmd(update, context)

    elif text == food_btn:
        await context.bot.send_message(user_id, t(lang, "food_photo_received"))
        return

    elif text == progress_btn:
        await show_daily_progress(update, context, user_id, lang)

    elif text == stats_btn:
        await stats_cmd(update, context)

    elif text == settings_btn:
        await settings_cmd(update, context)

    else:
        # Check if it's a food editing input or other context
        if context.user_data.get("editing"):
            from bot.food import handle_food_edit_input
            return await handle_food_edit_input(update, context)
        else:
            await context.bot.send_message(
                user_id,
                t(lang, "invalid_input"),
                reply_markup=main_menu_keyboard(lang)
            )
