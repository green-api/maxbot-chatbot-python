import asyncio, structlog, sys, os

sys.dont_write_bytecode = True
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from maxbot_api_client_python import API, Config
from maxbot_chatbot_python import Bot, MapStateManager

log = structlog.get_logger(__name__)

async def main():
    setup_logger(debug=True)
    
    api_client = API(cfg = Config(
        base_url="https://platform-bot.max.ru",  # Base url for MAX API requests
        token="YOUR_BOT_TOKEN",                  # Max bot token
    ))

    bot = Bot(api_client)
    bot.state_manager = MapStateManager(init_data={})

    @bot.router.register("message_created")
    async def echo_handler(notification):
        try:
            text = notification.text()
            await notification.reply(f"**Echo:** {text}", "markdown")
        except Exception as e:
            log.error(f"Echo error: {e}")

    polling_task = asyncio.create_task(bot.start_polling())

    try:
        await polling_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        log.info("Bot stopped by user (KeyboardInterrupt)")


def setup_logger(debug: bool = False):
    if debug:
        renderer = structlog.dev.ConsoleRenderer(colors=True)
    else:
        renderer = structlog.processors.JSONRenderer()

    structlog.configure(
        processors=[
            structlog.stdlib.add_log_level,
            structlog.stdlib.add_logger_name,
            structlog.processors.TimeStamper(fmt="iso"),
            renderer,
        ],
        logger_factory=structlog.PrintLoggerFactory(),
    )
