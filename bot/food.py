from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, CallbackQueryHandler, filters
from database import get_user, log_food
from i18n import t
from bot.keyboards import food_action_keyboard
from bot.progress import show_daily_progress
from bot.ai_engine import analyze_food_photo
import aiohttp

async def handle_food_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle food photo upload"""
    user_id = update.effective_user.id
    user = await get_user(user_id)

    if not user:
        await context.bot.send_message(user_id, "Please start with /start")
        return

    lang = user["language"] or "en"

    await context.bot.send_message(user_id, t(lang, "food_photo_received"))

    try:
        # Get photo
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)

        # Download photo bytes
        file_bytes = await file.download_as_bytearray()

        # Analyze with Claude
        analysis = await analyze_food_photo(bytes(file_bytes), lang)

        # Store analysis in context
        context.user_data["food_analysis"] = analysis
        context.user_data["photo_file_id"] = photo.file_id
        context.user_data["lang"] = lang

        # Show analysis with action buttons
        analysis_msg = t(lang, "food_analysis",
            meal_name=analysis.get("meal_name", "Unknown"),
            calories=analysis.get("calories", 500),
            protein=analysis.get("protein_g", 20),
            carbs=analysis.get("carbs_g", 50),
            fat=analysis.get("fat_g", 15),
            confidence=analysis.get("confidence", "medium")
        )

        await context.bot.send_message(
            user_id,
            analysis_msg,
            reply_markup=food_action_keyboard(lang),
            parse_mode="Markdown"
        )

    except Exception as e:
        await context.bot.send_message(user_id, t(lang, "error", error=str(e)))

async def handle_food_action(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle food action (record, edit, skip)"""
    query = update.callback_query
    await query.answer()

    lang = context.user_data.get("lang", "en")
    action = query.data
    user_id = update.effective_user.id

    if action == "record_food":
        analysis = context.user_data.get("food_analysis", {})
        photo_id = context.user_data.get("photo_file_id")

        await log_food(
            user_id,
            analysis.get("meal_name", "Unknown meal"),
            int(analysis.get("calories", 500)),
            float(analysis.get("protein_g", 20)),
            float(analysis.get("carbs_g", 50)),
            float(analysis.get("fat_g", 15)),
            photo_id
        )

        await query.edit_message_text(t(lang, "food_recorded"))
        await show_daily_progress(update, context, user_id, lang)

    elif action == "edit_food":
        await query.edit_message_text(t(lang, "enter_calories"))
        context.user_data["editing"] = "calories"

    elif action == "skip_food":
        await query.edit_message_text(t(lang, "food_skipped"))

async def handle_food_edit_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle manual food editing"""
    lang = context.user_data.get("lang", "en")
    user_id = update.effective_user.id

    try:
        value = float(update.message.text)
        editing = context.user_data.get("editing")

        if editing == "calories":
            context.user_data["edited_calories"] = int(value)
            await context.bot.send_message(user_id, t(lang, "enter_protein"))
            context.user_data["editing"] = "protein"
        elif editing == "protein":
            context.user_data["edited_protein"] = value
            await context.bot.send_message(user_id, t(lang, "enter_carbs"))
            context.user_data["editing"] = "carbs"
        elif editing == "carbs":
            context.user_data["edited_carbs"] = value
            await context.bot.send_message(user_id, t(lang, "enter_fat"))
            context.user_data["editing"] = "fat"
        elif editing == "fat":
            context.user_data["edited_fat"] = value

            # Save edited food
            analysis = context.user_data.get("food_analysis", {})
            photo_id = context.user_data.get("photo_file_id")

            await log_food(
                user_id,
                analysis.get("meal_name", "Unknown meal"),
                context.user_data.get("edited_calories", 500),
                context.user_data.get("edited_protein", 20),
                context.user_data.get("edited_carbs", 50),
                context.user_data.get("edited_fat", 15),
                photo_id
            )

            await context.bot.send_message(user_id, t(lang, "meal_updated"))
            await show_daily_progress(update, context, user_id, lang)

    except ValueError:
        await context.bot.send_message(user_id, t(lang, "invalid_number"))

# Handlers
food_handler = MessageHandler(filters.PHOTO, handle_food_photo)
food_action_handler = CallbackQueryHandler(handle_food_action, pattern="^(record_food|edit_food|skip_food)$")
food_edit_handler = MessageHandler(filters.TEXT & ~filters.COMMAND, handle_food_edit_input)
