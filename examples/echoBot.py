import asyncio

from maxbot_api_client_python import API, Config
from maxbot_chatbot_python import Bot, MapStateManager

async def main():
    
    api_client = API(cfg = Config(
        base_url="https://platform-api.max.ru/",  # Base url for MAX API requests
        token="YOUR_BOT_TOKEN",                  # Max bot token
        ratelimiter=25
    ))

    bot = Bot(api_client)
    bot.state_manager = MapStateManager(init_data={})

    @bot.router.register("message_created")
    async def echo_handler(notification):
        try:
            text = notification.text()
            await notification.reply(f"**Echo:** {text}", "markdown")
        except Exception as e:
            print(f"Error receiving updates:", str(e))

    polling_task = asyncio.create_task(bot.start_polling())

    try:
        await polling_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped by user (KeyboardInterrupt)")
