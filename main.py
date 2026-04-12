import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters

from config import TELEGRAM_TOKEN
from database import init_db
from bot.onboarding import onboarding_handler
from bot.workout import workout_handler
from bot.food import food_handler, food_action_handler, food_edit_handler
from bot.dev_agent import dev_command
from bot import handlers

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    """Main bot function"""
    await init_db()

    app = Application.builder().token(TELEGRAM_TOKEN).build()

    # Register handlers
    app.add_handler(onboarding_handler)
    app.add_handler(workout_handler)

    # Food handlers
    app.add_handler(food_handler)
    app.add_handler(food_action_handler)
    app.add_handler(food_edit_handler)

    # Command handlers
    app.add_handler(CommandHandler("start", handlers.start))
    app.add_handler(CommandHandler("help", handlers.help_cmd))
    app.add_handler(CommandHandler("progress", handlers.progress_cmd))
    app.add_handler(CommandHandler("stats", handlers.stats_cmd))
    app.add_handler(CommandHandler("gym", handlers.gym_cmd))
    app.add_handler(CommandHandler("settings", handlers.settings_cmd))
    app.add_handler(CommandHandler("dev", dev_command))

    # Text message handler (for menu buttons and other text)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_handler))

    print("🐾 Capybara Bot is running!")
    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
