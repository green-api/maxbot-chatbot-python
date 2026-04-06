import asyncio
from typing import List, Optional

from maxbot_api_client_python import utils
from maxbot_api_client_python.types.models import AnswerCallbackReq, Attachment, KeyboardButton, SendActionReq, SendFileReq, SendMessageReq
class Notification:
    def __init__(self, update, bot_api, state_manager=None):
        self.update = update
        self.bot_api = bot_api
        self.state_manager = state_manager
        self.state_id = "global"
        self.create_state_id()

    async def send(self, req: SendMessageReq, log_prefix: str):
        """
        Internal method to send a constructed message request to the chat and log it.
        """
        req.chat_id = self.chat_id()

        try:
            await self.bot_api.messages.SendMessageAsync(req)
            print(f"{log_prefix} reply sent to {req.chat_id}")
        except Exception as e:
            print(f"Sending {log_prefix} reply error: {e}, target_id: {req.chat_id}")
            raise

    def type(self) -> str:
        """
        Returns the type of the incoming update.

        Example:
            u_type = notification.type()
        """
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

    async def reply(self, text: str, format_type: Optional[str] = "markdown"):
        """
        Sends a text message back to the current chat.

        Example:
            await notification.reply("Hello, World!", format_type="markdown")
        """
        await self.send(SendMessageReq(
            chat_id=0,
            text=text,
            format=format_type if format_type else None,
            notify=True
        ), "Text")

    async def reply_with_media(self, text: str, format_type: Optional[str], file_source: str, keyboard: Optional[List[List[KeyboardButton]]] = None):
        """
        Sends a media file (image, video, document) with optional text and keyboard.

        Example:
            await notification.reply_with_media(
                text="Look at this!",
                format_type="markdown",
                file_source="https://example.com/image.jpg"
            )
        """
        target_id = self.chat_id()
        req = SendFileReq(
            chat_id=target_id,
            text=text,
            format=format_type if format_type else None,
            file_source=file_source,
            notify=True
        )
        
        if keyboard:
            req.attachments = [utils.attach_keyboard(keyboard)]

        for i in range(5):
            try:
                await self.bot_api.helpers.SendFileAsync(req)
                print("Media reply sent successfully to {target_id}")
                return
            except Exception as e:
                err_str = str(e)
                if "not.ready" in err_str or "not.found" in err_str:
                    print("File is processing", attempt=i+1, max_attempts=5)
                    await asyncio.sleep(3)
                    continue
                print("Sending media reply error: {e}")
                raise e

    async def reply_with_contact(self, name: str, phone: str, contact_id: Optional[int] = None):
        """
        Sends a contact card to the chat.

        Example:
            await notification.reply_with_contact(name="John Doe", phone="79876543210")
        """
        await self.send(SendMessageReq(
            chat_id=0,
            attachments=[utils.attach_contact(name, phone, contact_id)],
            notify=True
        ), "Contact")

    async def reply_with_location(self, lat: float, lon: float):
        """
        Sends geographical coordinates to the chat.

        Example:
            await notification.reply_with_location(lat=51.5074, lon=-0.1278)
        """
        await self.send(SendMessageReq(
            chat_id=0,
            attachments=[utils.attach_location(lat, lon)],
            notify=True
        ), "Location")

    async def reply_with_keyboard(self, text: str, format_type: Optional[str], buttons: List[List[KeyboardButton]]):
        """
        Sends a text message with an inline or reply keyboard attached.

        Example:
            buttons = [[KeyboardButton(text="Yes"), KeyboardButton(text="No")]]
            await notification.reply_with_keyboard("Are you sure?", "markdown", buttons)
        """
        await self.send(SendMessageReq(
            chat_id=0,
            text=text,
            format=format_type if format_type else None,
            attachments=[utils.attach_keyboard(buttons)],
            notify=True
        ), "Keyboard")

    async def reply_with_sticker(self, url: str, code: str):
        """
        Sends a sticker to the chat.

        Example:
            await notification.reply_with_sticker("https://example.com/sticker.webp", "")
        """
        await self.send(SendMessageReq(
            chat_id=0,
            attachments=[utils.attach_sticker(url, code)],
            notify=True
        ), "Sticker")

    async def reply_with_share(self, text: str, url: str, title: str, desc: str):
        """
        Sends a rich link preview/share attachment.

        Example:
            await notification.reply_with_share("Check this out!", "https://max.ru", "MAX API", "Awesome API")
        """
        await self.send(SendMessageReq(
            chat_id=0,
            text=text,
            attachments=[utils.attach_share(url, title, desc)],
            notify=True
        ), "Share")

    async def reply_with_attachments(self, text: str, format_type: Optional[str], attachments: List[Attachment]):
        """
        Sends a text message with a custom list of attachments.

        Example:
            attachment = [Attachment.AttachLocation(10.0, 20.0)]
            await notification.reply_with_attachments("Here is the place:", "markdown", attachment)
        """
        await self.send(SendMessageReq(
            chat_id=0,
            text=text,
            format=format_type if format_type else None,
            attachments=attachments,
            notify=True
        ), "Attachments")

    async def answer_callback(self, text: str = ""):
        """
        Acknowledges a user's click on an inline button, optionally showing a toast notification.

        Example:
            await notification.answer_callback("Action confirmed!")
        """
        if not self._is_callback:
            raise ValueError("cannot answer callback: update is not a callback")

        try:
            await self.bot_api.messages.AnswerCallbackAsync(AnswerCallbackReq(
            callback_id=self.update.callback.callback_id,
            notification=text if text else " "
        ))
        except Exception as e:
            print("AnswerCallback error: {e}")
            raise

    async def show_action(self, action: str):
        """
        Broadcasts a temporary status action (e.g., "typing_on") to the chat participants.

        Example:
            await notification.show_action("typing_on")
        """
        try:
            chat_id = self.chat_id()
            if chat_id == 0:
                raise ValueError("missing chat ID")
                
            res = await self.bot_api.chats.SendActionAsync(SendActionReq(
                chat_id=chat_id,
                action=action
            ))
            
            if res and not getattr(res, 'success', True):
                print("API rejected the action {action}: {res}")
            else:
                print("Action {action} sent successfully to {chat_id}")
                
        except Exception as e:
            print("Failed to send action {action} due to API error {e}")
            raise

    def create_state_id(self):
        """
        Generates a unique state identifier based on the chat ID.
        """
        try:
            chat_id = self.chat_id()
            if chat_id:
                self.state_id = f"chat_{chat_id}"
        except ValueError:
            self.state_id = "global"

    def activate_next_scene(self, scene):
        """
        Transitions the user to a new scene in the state manager.

        Example:
            notification.activate_next_scene(MyNextScene())
        """
        if self.state_manager:
            self.state_manager.activate_next_scene(self.state_id, scene)

    def get_current_scene(self):
        """
        Retrieves the current scene for the user from the state manager.

        Example:
            current_scene = notification.get_current_scene()
        """
        if self.state_manager:
            return self.state_manager.get_current_scene(self.state_id)
        return None