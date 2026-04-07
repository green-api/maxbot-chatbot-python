import asyncio
from maxbot_chatbot_python.router import Router
from maxbot_chatbot_python.notification import Notification

class Bot:
    def __init__(self, api_client):
        self.api = api_client
        self.router = Router()
        self.state_manager = None
        self.marker = 0

    async def start_polling(self):
        print("Bot is running. Start polling...")

        while True:
            try:
                resp = await self.api.subscriptions.GetUpdatesAsync(
                    marker=self.marker,
                    timeout=25
                )

                if getattr(resp, 'marker', 0) != 0:
                    self.marker = resp.marker

                updates = getattr(resp, 'updates', [])
                for update in updates:
                    asyncio.create_task(self.process_update(update))

            except asyncio.CancelledError:
                print("Stop polling...")
                break
            except Exception as e:
                print(f"Error receiving updates: {e}")
                await asyncio.sleep(2)

    async def process_update(self, update):
        notif = Notification(
            update=update, 
            bot_api=self.api, 
            state_manager=self.state_manager
        )
        await self.router.publish(notif)