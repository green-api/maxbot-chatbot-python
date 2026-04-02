import asyncio, structlog
from .router import Router
from .notification import Notification
from maxbot_api_client_python.types.models import GetUpdatesReq

log = structlog.get_logger(__name__)

class Bot:
    def __init__(self, api_client):
        self.api = api_client
        self.router = Router()
        self.state_manager = None
        self.marker = 0

    async def start_polling(self):
        log.info("Bot is running. Start polling...")

        while True:
            try:
                resp = await self.api.subscriptions.GetUpdatesAsync(GetUpdatesReq(
                    marker=self.marker,
                    timeout=25
                ))

                if getattr(resp, 'marker', 0) != 0:
                    self.marker = resp.marker

                updates = getattr(resp, 'updates', [])
                for update in updates:
                    asyncio.create_task(self.process_update(update))

            except asyncio.CancelledError:
                log.info("Stop polling...")
                break
            except Exception as e:
                log.error("Error receiving updates", error=str(e))
                await asyncio.sleep(2)

    async def process_update(self, update):
        notif = Notification(
            update=update, 
            bot_api=self.api, 
            state_manager=self.state_manager
        )
        await self.router.publish(notif)