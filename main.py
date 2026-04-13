import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters

from config import TELEGRAM_TOKEN
from database import init_db
from bot.onboarding import onboarding_handler
from bot.workout import workout_handler
from bot.food import food_handler, food_action_handler, food_edit_handler
from bot.dev_agent import dev_command
from bot import handlers

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Called after the application is initialized — safe place for async setup."""
    await init_db()
    logger.info("✅ Database initialized")


def main() -> None:
    """Start the bot — synchronous entry point."""
    app = (
        Application.builder()
        .token(TELEGRAM_TOKEN)
        .post_init(post_init)
        .build()
    )

    # Register all handlers (ConversationHandlers FIRST)
    app.add_handler(onboarding_handler)  # Handles /start with entry point
    app.add_handler(workout_handler)
    app.add_handler(food_handler)
    app.add_handler(food_action_handler)
    app.add_handler(food_edit_handler)
    # Then command handlers
    app.add_handler(CommandHandler("dev", dev_command))
    app.add_handler(CommandHandler("help", handlers.help_cmd))
    app.add_handler(CommandHandler("progress", handlers.progress_cmd))
    app.add_handler(CommandHandler("stats", handlers.stats_cmd))
    app.add_handler(CommandHandler("settings", handlers.settings_cmd))
    # Then generic text handler LAST
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handlers.text_handler))

    logger.info("🐾 Capybara Bot is running!")

    # run_polling() manages its own event loop — do NOT wrap with asyncio.run()
    app.run_polling(allowed_updates=["message", "callback_query"])


if __name__ == "__main__":
    main()
