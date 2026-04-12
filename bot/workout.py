from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, CommandHandler, MessageHandler, CallbackQueryHandler, filters
from database import start_gym_session, add_exercise, end_gym_session, get_session_exercises, get_user
from i18n import t
from bot.keyboards import gym_menu_keyboard, sets_keyboard, reps_keyboard, confirm_keyboard
from bot.progress import show_daily_progress

GYM_MENU, ADD_EXERCISE, EXERCISE_NAME, SETS, REPS, WEIGHT = range(6)

async def start_gym_session_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start new gym session"""
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if not user:
        await context.bot.send_message(user_id, "Please start with /start")
        return ConversationHandler.END

    lang = user["language"] or "en"

    # Create session
    session_id = await start_gym_session(user_id)
    context.user_data["session_id"] = session_id
    context.user_data["lang"] = lang
    context.user_data["exercises"] = []

    await context.bot.send_message(
        user_id,
        t(lang, "start_gym"),
        reply_markup=gym_menu_keyboard(lang),
        parse_mode="Markdown"
    )
    return GYM_MENU

async def gym_menu_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle gym menu selections"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "en")
    choice = query.data

    if choice == "add_ex":
        await query.edit_message_text(t(lang, "ask_exercise_name"))
        return EXERCISE_NAME
    elif choice == "view_ex":
        session_id = context.user_data.get("session_id")
        exercises = await get_session_exercises(session_id)

        if not exercises:
            await query.edit_message_text(
                t(lang, "no_exercises"),
                reply_markup=gym_menu_keyboard(lang)
            )
        else:
            ex_text = ""
            for ex in exercises:
                ex_text += f"• {ex['name']} — {ex['sets']}x{ex['reps']} @ {ex['weight_kg']}kg\n"

            await query.edit_message_text(
                f"*Exercises logged:*\n{ex_text}",
                reply_markup=gym_menu_keyboard(lang),
                parse_mode="Markdown"
            )
        return GYM_MENU
    elif choice == "finish_gym":
        session_id = context.user_data.get("session_id")
        user_id = update.effective_user.id

        stats = await end_gym_session(session_id, user_id)

        exercises = await get_session_exercises(session_id)
        ex_text = ""
        for ex in exercises:
            ex_text += f"• {ex['name']} — {ex['sets']}x{ex['reps']} @ {ex['weight_kg']}kg\n"

        summary = t(lang, "session_summary",
            duration=stats["duration_min"],
            calories=stats["calories_burned"],
            volume=stats["total_volume"],
            exercises=ex_text or t(lang, "no_exercises")
        )

        await query.edit_message_text(summary, parse_mode="Markdown")

        # Show daily progress
        await show_daily_progress(update, context, user_id, lang)

        return ConversationHandler.END

    return GYM_MENU

async def ask_exercise_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get exercise name"""
    lang = context.user_data.get("lang", "en")
    context.user_data["ex_name"] = update.message.text

    await context.bot.send_message(
        update.effective_user.id,
        t(lang, "ask_sets"),
        reply_markup=sets_keyboard()
    )
    return SETS

async def ask_sets(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get number of sets"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    sets_num = int(query.data.split("_")[1])
    context.user_data["ex_sets"] = sets_num

    await query.edit_message_text(
        t(lang, "ask_reps"),
        reply_markup=reps_keyboard()
    )
    return REPS

async def ask_reps(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get number of reps"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data.get("lang", "en")

    reps_num = int(query.data.split("_")[1])
    context.user_data["ex_reps"] = reps_num

    await query.edit_message_text(t(lang, "ask_weight_used"))
    return WEIGHT

async def ask_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get weight and save exercise"""
    lang = context.user_data.get("lang", "en")

    try:
        weight = float(update.message.text)
    except ValueError:
        await context.bot.send_message(update.effective_user.id, t(lang, "invalid_number"))
        return WEIGHT

    # Add exercise
    session_id = context.user_data.get("session_id")
    user_id = update.effective_user.id

    await add_exercise(
        session_id,
        user_id,
        context.user_data["ex_name"],
        context.user_data["ex_sets"],
        context.user_data["ex_reps"],
        weight
    )

    # Show confirmation
    confirm_msg = t(lang, "exercise_added",
        exercise=context.user_data["ex_name"],
        sets=context.user_data["ex_sets"],
        reps=context.user_data["ex_reps"],
        weight=weight
    )

    await context.bot.send_message(
        user_id,
        confirm_msg + "\n\n" + t(lang, "start_gym"),
        reply_markup=gym_menu_keyboard(lang)
    )

    return GYM_MENU

async def cancel_workout(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel workout"""
    lang = context.user_data.get("lang", "en")
    await context.bot.send_message(update.effective_user.id, t(lang, "cancel"))
    return ConversationHandler.END

# Conversation handler
workout_handler = ConversationHandler(
    entry_points=[
        CommandHandler("gym", start_gym_session_cmd),
        CallbackQueryHandler(lambda u, c: start_gym_session_cmd(u, c), pattern="^gym$")
    ],
    states={
        GYM_MENU: [CallbackQueryHandler(gym_menu_handler)],
        EXERCISE_NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_exercise_name)],
        SETS: [CallbackQueryHandler(ask_sets)],
        REPS: [CallbackQueryHandler(ask_reps)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weight)],
    },
    fallbacks=[CommandHandler("cancel", cancel_workout)],
)
