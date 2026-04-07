import asyncio, logging

from maxbot_api_client_python import utils
from maxbot_api_client_python.types.models import Attachment, KeyboardButton

logger = logging.getLogger(__name__)

class Notification:
    def __init__(self, update, bot_api, state_manager=None):
        self.update = update
        self.bot_api = bot_api
        self.state_manager = state_manager
        self.state_id = "global"
        self.create_state_id()

    async def send(self, **kwargs):
        """
        Internal method to send a constructed message request to the chat and log it.
        """
        if "chat_id" not in kwargs or kwargs["chat_id"] == 0:
            kwargs["chat_id"] = self.chat_id()

        try:
            await self.bot_api.messages.SendMessageAsync(**kwargs)
            logger.info(f"Reply sent to {kwargs['chat_id']}")
        except Exception as e:
            logger.error(f"Sending reply error: {e}, target_id: {kwargs['chat_id']}")
            raise

    def type(self) -> str:
        """Returns the type of the incoming update."""
        if hasattr(self.update, 'update_type'):
            return self.update.update_type
        elif isinstance(self.update, dict):
            return self.update.get('update_type')
        return "unknown"

    @property
    def _is_message(self) -> bool:
        return self.type() in ("message_created", "message_edited") and self.update.message is not None

    @property
    def _is_callback(self) -> bool:
        return self.type() == "message_callback" and self.update.callback is not None

    def text(self) -> str:
        if self._is_message and self.update.message.body:
            return self.update.message.body.text
        if self._is_callback:
            return self.update.callback.payload
        raise ValueError(f"Text is not applicable or missing for type: {self.type()}")

    def sender_name(self) -> str:
        if self._is_message and self.update.message.sender:
            return self.update.message.sender.first_name
        if self._is_callback and self.update.callback.user:
            return self.update.callback.user.first_name
        raise ValueError(f"Sender name not found for type: {self.type()}")

    def sender_id(self) -> int:
        if self._is_message and self.update.message.sender:
            return self.update.message.sender.user_id
        if self._is_callback and self.update.callback.user:
            return self.update.callback.user.user_id
        raise ValueError(f"Sender ID not found for type: {self.type()}")

    def chat_id(self) -> int:
        if self._is_message:
            chat_id = getattr(self.update.message.recipient, 'chat_id', 0) if self.update.message.recipient else 0
            return chat_id if chat_id != 0 else getattr(self.update.message.sender, 'user_id', 0)
            
        if self._is_callback:
            if getattr(self.update, 'chat_id', 0):
                return self.update.chat_id
            if getattr(self.update.callback, 'chat_id', 0):
                return getattr(self.update.callback, 'chat_id')
            if getattr(self.update, 'message', None) and getattr(self.update.message.recipient, 'chat_id', 0):
                return self.update.message.recipient.chat_id
            if self.update.callback.user:
                return self.update.callback.user.user_id
                
        raise ValueError(f"Chat ID not found for type: {self.type()}")

    async def reply(self, text: str, format_type: str | None = "markdown"):
        await self.send(
            chat_id=0,
            text=text,
            format=format_type if format_type else None,
            notify=True
        )

    async def reply_with_media(self, text: str, format_type: str | None, file_source: str, keyboard: list[list[KeyboardButton]] | None = None):
        target_id = self.chat_id()
        kwargs = {
            "chat_id": target_id,
            "text": text,
            "format": format_type if format_type else None,
            "file_source": file_source,
            "notify": True
        }
        
        if keyboard:
            kwargs["attachments"] = [utils.attach_keyboard(keyboard)]

        for i in range(5):
            try:
                await self.bot_api.helpers.SendFileAsync(**kwargs)
                logger.info(f"Media reply sent successfully to {target_id}")
                return
            except Exception as e:
                err_str = str(e)
                if "not.ready" in err_str or "not.found" in err_str:
                    logger.info(f"File is processing, attempt {i+1}/5")
                    await asyncio.sleep(3)
                    continue
                logger.error(f"Sending media reply error: {e}")
                raise e

    async def reply_with_contact(self, name: str, phone: str, contact_id: int | None = None):
        await self.send(
            chat_id=0,
            attachments=[utils.attach_contact(name, phone, contact_id)],
            notify=True
        )

    async def reply_with_location(self, lat: float, lon: float):
        await self.send(
            chat_id=0,
            attachments=[utils.attach_location(lat, lon)],
            notify=True
        )

    async def reply_with_keyboard(self, text: str, format_type: str | None, buttons: list[list[KeyboardButton]]):
        await self.send(
            chat_id=0,
            text=text,
            format=format_type if format_type else None,
            attachments=[utils.attach_keyboard(buttons)],
            notify=True
        )

    async def reply_with_sticker(self, url: str, code: str):
        await self.send(
            chat_id=0,
            attachments=[utils.attach_sticker(url, code)],
            notify=True
        )

    async def reply_with_share(self, text: str, url: str, title: str, desc: str):
        await self.send(
            chat_id=0,
            text=text,
            attachments=[utils.attach_share(url, title, desc)],
            notify=True
        )

    async def reply_with_attachments(self, text: str, format_type: str | None, attachments: list[Attachment]):
        await self.send(
            chat_id=0,
            text=text,
            format=format_type if format_type else None,
            attachments=attachments,
            notify=True
        )

    async def answer_callback(self, text: str = ""):
        if not self._is_callback:
            raise ValueError("cannot answer callback: update is not a callback")

        try:
            await self.bot_api.messages.AnswerCallbackAsync(
                callback_id=self.update.callback.callback_id,
                notification=text if text else " "
            )
        except Exception as e:
            logger.error(f"AnswerCallback error: {e}")
            raise

    async def show_action(self, action: str):
        try:
            chat_id = self.chat_id()
            if chat_id == 0:
                raise ValueError("missing chat ID")
                
            res = await self.bot_api.chats.SendActionAsync(
                chat_id=chat_id,
                action=action
            )
            
            if res and not getattr(res, 'success', True):
                logger.warning(f"API rejected the action {action}: {res}")
            else:
                logger.info(f"Action {action} sent successfully to {chat_id}")
                
        except Exception as e:
            logger.error(f"Failed to send action {action} due to API error {e}")
            raise

    def create_state_id(self):
        try:
            chat_id = self.chat_id()
            if chat_id:
                self.state_id = f"chat_{chat_id}"
        except ValueError:
            self.state_id = "global"

    def activate_next_scene(self, scene):
        if self.state_manager:
            self.state_manager.activate_next_scene(self.state_id, scene)

    def get_current_scene(self):
        if self.state_manager:
            return self.state_manager.get_current_scene(self.state_id)
        return None