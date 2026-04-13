from telegram import Update
from telegram.ext import ContextTypes, ConversationHandler, MessageHandler, CallbackQueryHandler, CommandHandler, filters
from telegram.error import BadRequest
from database import create_user, get_user, update_user
from i18n import t
from bot.keyboards import (
    language_keyboard, gender_keyboard, goal_keyboard, gym_frequency_keyboard,
    gym_duration_keyboard, fitness_level_keyboard, diet_keyboard, water_goal_keyboard,
    main_menu_keyboard
)
import re

LANG, GENDER, AGE, HEIGHT, WEIGHT, GOAL, GYM_FREQ, GYM_DUR, FITNESS, DIET, WAKE, SLEEP, WATER, HEALTH, COMPLETE = range(15)

goal_map = {
    "goal_lose": "weight_loss",
    "goal_muscle": "muscle_gain",
    "goal_maintain": "maintain",
    "goal_endurance": "endurance",
    "goal_fitness": "general_fitness"
}

fitness_map = {
    "fit_beginner": "beginner",
    "fit_intermediate": "intermediate",
    "fit_advanced": "advanced"
}

diet_map = {
    "diet_none": "none",
    "diet_vegetarian": "vegetarian",
    "diet_vegan": "vegan",
    "diet_keto": "keto",
    "diet_halal": "halal"
}

gender_map = {
    "gender_male": "male",
    "gender_female": "female"
}

async def start_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start onboarding flow"""
    user_id = update.effective_user.id
    username = update.effective_user.username or "user"

    # Check if user exists
    user = await get_user(user_id)
    if user is None:
        await create_user(user_id, username)

    await context.bot.send_message(
        user_id,
        t("en", "welcome"),
        reply_markup=language_keyboard(),
        parse_mode="Markdown"
    )
    return LANG

async def set_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set user language"""
    query = update.callback_query
    await query.answer()

    lang_code = query.data.replace("lang_", "")
    context.user_data["lang"] = lang_code
    context.user_data["user_id"] = query.from_user.id

    await context.bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=t(lang_code, "choose_language"),
        reply_markup=language_keyboard()
    )

    await context.bot.send_message(
        query.from_user.id,
        t(lang_code, "ask_name")
    )
    return NAME

async def handle_name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle name input and ask for gender"""
    lang = context.user_data["lang"]
    name = update.message.text.strip()

    if len(name) < 1 or len(name) > 50:
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "invalid_input")
        )
        return NAME

    context.user_data["name"] = name

    await context.bot.send_message(
        update.effective_user.id,
        t(lang, "ask_gender"),
        reply_markup=gender_keyboard(lang)
    )
    return GENDER

async def set_gender(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set gender and ask age"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data["lang"]

    context.user_data["gender"] = gender_map.get(query.data, "male")

    await query.edit_message_text(
        text=t(lang, "ask_age")
    )
    return AGE

async def ask_age(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate age and ask height"""
    lang = context.user_data["lang"]

    try:
        age = int(update.message.text)
        if age < 10 or age > 100:
            await context.bot.send_message(
                update.effective_user.id,
                t(lang, "age_invalid")
            )
            return AGE

        context.user_data["age"] = age
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "ask_height")
        )
        return HEIGHT
    except ValueError:
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "invalid_number")
        )
        return AGE

async def ask_height(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate height and ask weight"""
    lang = context.user_data["lang"]

    try:
        height = float(update.message.text)
        if height < 100 or height > 250:
            await context.bot.send_message(
                update.effective_user.id,
                t(lang, "height_invalid")
            )
            return HEIGHT

        context.user_data["height"] = height
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "ask_weight")
        )
        return WEIGHT
    except ValueError:
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "invalid_number")
        )
        return HEIGHT

async def ask_weight(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate weight and ask goal"""
    lang = context.user_data["lang"]

    try:
        weight = float(update.message.text)
        if weight < 30 or weight > 300:
            await context.bot.send_message(
                update.effective_user.id,
                t(lang, "weight_invalid")
            )
            return WEIGHT

        context.user_data["weight"] = weight
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "ask_goal"),
            reply_markup=goal_keyboard(lang)
        )
        return GOAL
    except ValueError:
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "invalid_number")
        )
        return WEIGHT

async def set_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set goal and ask gym frequency"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data["lang"]

    context.user_data["goal"] = goal_map.get(query.data, "general_fitness")

    await query.edit_message_text(
        text=t(lang, "ask_gym_frequency"),
        reply_markup=gym_frequency_keyboard(lang)
    )
    return GYM_FREQ

async def set_gym_frequency(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set gym frequency and ask duration"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data["lang"]

    freq = int(query.data.split("_")[1])
    context.user_data["gym_frequency"] = freq

    await query.edit_message_text(
        text=t(lang, "ask_gym_duration"),
        reply_markup=gym_duration_keyboard(lang)
    )
    return GYM_DUR

async def set_gym_duration(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set gym duration and ask fitness level"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data["lang"]

    dur = int(query.data.split("_")[1])
    context.user_data["gym_duration"] = dur

    await query.edit_message_text(
        text=t(lang, "ask_fitness_level"),
        reply_markup=fitness_level_keyboard(lang)
    )
    return FITNESS

async def set_fitness_level(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set fitness level and ask diet"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data["lang"]

    context.user_data["fitness"] = fitness_map.get(query.data, "beginner")

    await query.edit_message_text(
        text=t(lang, "ask_diet_preference"),
        reply_markup=diet_keyboard(lang)
    )
    return DIET

async def set_diet(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set diet and ask wake time"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data["lang"]

    context.user_data["diet"] = diet_map.get(query.data, "none")

    await query.edit_message_text(
        text=t(lang, "ask_wake_time")
    )
    return WAKE

async def ask_wake_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate wake time and ask sleep time"""
    lang = context.user_data["lang"]

    time_str = update.message.text.strip()
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "invalid_time")
        )
        return WAKE

    context.user_data["wake_time"] = time_str
    await context.bot.send_message(
        update.effective_user.id,
        t(lang, "ask_sleep_time")
    )
    return SLEEP

async def ask_sleep_time(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Validate sleep time and ask water goal"""
    lang = context.user_data["lang"]

    time_str = update.message.text.strip()
    if not re.match(r"^\d{2}:\d{2}$", time_str):
        await context.bot.send_message(
            update.effective_user.id,
            t(lang, "invalid_time")
        )
        return SLEEP

    context.user_data["sleep_time"] = time_str
    await context.bot.send_message(
        update.effective_user.id,
        t(lang, "ask_daily_water"),
        reply_markup=water_goal_keyboard(lang)
    )
    return WATER

async def set_water_goal(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Set water goal and ask health conditions"""
    query = update.callback_query
    await query.answer()
    lang = context.user_data["lang"]

    water = int(query.data.split("_")[1])
    context.user_data["water_goal"] = water

    await query.edit_message_text(
        text=t(lang, "ask_health_conditions")
    )
    return HEALTH

async def ask_health(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Get health conditions and complete onboarding"""
    lang = context.user_data["lang"]

    health = update.message.text.strip()
    if health.lower() in ["none", "no", "нет", "nu"]:
        health = ""

    context.user_data["health"] = health

    # Calculate BMI and calorie target
    weight = context.user_data["weight"]
    height = context.user_data["height"]
    age = context.user_data["age"]
    gender = context.user_data["gender"]
    gym_freq = context.user_data["gym_frequency"]
    goal = context.user_data["goal"]

    bmi = weight / ((height / 100) ** 2)

    if bmi < 18.5:
        bmi_category = "Underweight"
    elif bmi < 25:
        bmi_category = "Normal"
    elif bmi < 30:
        bmi_category = "Overweight"
    else:
        bmi_category = "Obese"

    # Mifflin-St Jeor formula (assuming male, as asked)
    if gender == "male":
        bmr = 10 * weight + 6.25 * height - 5 * age + 5
    else:
        bmr = 10 * weight + 6.25 * height - 5 * age - 161

    # Activity multiplier
    if gym_freq <= 2:
        multiplier = 1.375
    elif gym_freq <= 4:
        multiplier = 1.55
    else:
        multiplier = 1.725

    tdee = int(bmr * multiplier)

    # Goal adjustment
    if goal == "weight_loss":
        calorie_target = tdee - 300
        protein_ratio = 0.40
        carbs_ratio = 0.30
        fat_ratio = 0.30
    elif goal == "muscle_gain":
        calorie_target = tdee + 300
        protein_ratio = 0.35
        carbs_ratio = 0.45
        fat_ratio = 0.20
    else:
        calorie_target = tdee
        protein_ratio = 0.30
        carbs_ratio = 0.40
        fat_ratio = 0.30

    # Calculate macros
    protein_target = (calorie_target * protein_ratio) / 4
    carbs_target = (calorie_target * carbs_ratio) / 4
    fat_target = (calorie_target * fat_ratio) / 9

    user_id = context.user_data["user_id"]
    await update_user(user_id, **{
        "language": lang,
        "gender": gender,
        "name": context.user_data["name"],
        "age": context.user_data["age"],
        "height_cm": context.user_data["height"],
        "weight_kg": context.user_data["weight"],
        "goal": context.user_data["goal"],
        "gym_frequency": context.user_data["gym_frequency"],
        "gym_duration_min": context.user_data["gym_duration"],
        "fitness_level": context.user_data["fitness"],
        "diet_preference": context.user_data["diet"],
        "wake_time": context.user_data["wake_time"],
        "sleep_time": context.user_data["sleep_time"],
        "daily_water_goal": context.user_data["water_goal"],
        "health_conditions": context.user_data["health"],
        "bmi": bmi,
        "bmi_category": bmi_category,
        "calorie_target": calorie_target,
        "protein_target": protein_target,
        "carbs_target": carbs_target,
        "fat_target": fat_target,
        "onboarding_complete": 1
    })

    complete_msg = t(lang, "onboarding_complete",
        name=context.user_data["name"],
        bmi=bmi,
        bmi_category=bmi_category,
        calorie_target=calorie_target,
        protein_target=protein_target,
        carbs_target=carbs_target,
        fat_target=fat_target
    )

    await context.bot.send_message(
        user_id,
        complete_msg,
        reply_markup=main_menu_keyboard(lang),
        parse_mode="Markdown"
    )

    return ConversationHandler.END

async def cancel_onboarding(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel onboarding"""
    lang = context.user_data.get("lang", "en")
    await context.bot.send_message(
        update.effective_user.id,
        t(lang, "cancel")
    )
    return ConversationHandler.END

# Conversation handler setup
onboarding_handler = ConversationHandler(
    entry_points=[CommandHandler("start", start_onboarding)],
    states={
        LANG: [CallbackQueryHandler(set_language, pattern="^lang_")],
        NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_name)],
        GENDER: [CallbackQueryHandler(set_gender, pattern="^gender_")],
        AGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_age)],
        HEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_height)],
        WEIGHT: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_weight)],
        GOAL: [CallbackQueryHandler(set_goal, pattern="^goal_")],
        GYM_FREQ: [CallbackQueryHandler(set_gym_frequency, pattern="^freq_")],
        GYM_DUR: [CallbackQueryHandler(set_gym_duration, pattern="^dur_")],
        FITNESS: [CallbackQueryHandler(set_fitness_level, pattern="^fit_")],
        DIET: [CallbackQueryHandler(set_diet, pattern="^diet_")],
        WAKE: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_wake_time)],
        SLEEP: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_sleep_time)],
        WATER: [CallbackQueryHandler(set_water_goal, pattern="^water_")],
        HEALTH: [MessageHandler(filters.TEXT & ~filters.COMMAND, ask_health)],
    },
    fallbacks=[CommandHandler("cancel", cancel_onboarding)],
    per_message=False,
)
