from telegram import Update
from telegram.ext import ContextTypes
from datetime import datetime
from database import get_user, get_daily_summary, get_today_meals
from i18n import t
from bot.ai_engine import get_daily_tip

def progress_bar(current: float, total: float, length: int = 10) -> str:
    """Generate a text progress bar"""
    if total == 0:
        total = 1
    filled = int(length * min(current / total, 1.0))
    return "█" * filled + "░" * (length - filled)

async def show_daily_progress(update: Update, context: ContextTypes.DEFAULT_TYPE, user_id: int, lang: str):
    """Display daily progress dashboard"""
    try:
        user = await get_user(user_id)
        if not user:
            await context.bot.send_message(user_id, t(lang, "error", error="User not found"))
            return

        summary = await get_daily_summary(user_id)
        meals = await get_today_meals(user_id)

        calorie_target = user["calorie_target"] or 2000
        protein_target = user["protein_target"] or 150
        carbs_target = user["carbs_target"] or 200
        fat_target = user["fat_target"] or 65
        water_target = user["daily_water_goal"] or 8

        consumed_calories = summary["total_calories"] or 0
        burned_calories = summary["calories_burned"] or 0
        net_calories = consumed_calories - burned_calories

        meals_text = ""
        if meals:
            for meal in meals:
                meals_text += f"• {meal['meal_name']} — {meal['calories']} kcal\n"
        else:
            meals_text = "No meals logged yet"

        gym_status = t(lang, "gym_done", duration=summary.get("gym_duration_min", 0)) if summary.get("gym_session") else t(lang, "gym_not_done")

        tip = await get_daily_tip(dict(user), summary, lang)

        date_str = datetime.now().strftime("%Y-%m-%d")

        progress_msg = t(lang, "daily_progress",
            date=date_str,
            consumed=consumed_calories,
            target=calorie_target,
            burned=burned_calories,
            net=max(0, net_calories),
            cal_bar=progress_bar(consumed_calories, calorie_target),
            protein_g=summary["total_protein"] or 0,
            protein_target=protein_target,
            protein_bar=progress_bar(summary["total_protein"] or 0, protein_target),
            carbs_g=summary["total_carbs"] or 0,
            carbs_target=carbs_target,
            carbs_bar=progress_bar(summary["total_carbs"] or 0, carbs_target),
            fat_g=summary["total_fat"] or 0,
            fat_target=fat_target,
            fat_bar=progress_bar(summary["total_fat"] or 0, fat_target),
            water=summary["water_glasses"] or 0,
            water_target=water_target,
            water_bar=progress_bar(summary["water_glasses"] or 0, water_target),
            gym_status=gym_status,
            meals_count=len(meals),
            meals_list=meals_text,
            tip=tip
        )

        await context.bot.send_message(user_id, progress_msg, parse_mode="Markdown")

    except Exception as e:
        await context.bot.send_message(user_id, t(lang, "error", error=str(e)))
