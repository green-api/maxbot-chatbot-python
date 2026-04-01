import structlog

log = structlog.get_logger(__name__)

class Router:
    def __init__(self):
        self.handlers = {}
        self.commands = {}
        self.callbacks = {}

    def command(self, cmd: str):
        """
        Decorator to register a handler for a specific text command (e.g., /start).

        Example:
            @router.command("/help")
            async def handle_help(notification):
                await notification.reply("Commands list...")
        """
        def decorator(func):
            self.commands[cmd] = func
            return func
        return decorator

    def callback(self, payload: str):
        """
        Decorator to register a handler for a specific callback payload from buttons.

        Example:
            @router.callback("settings_press")
            async def handle_settings(notification):
                await notification.answer_callback("Opening settings...")
        """
        def decorator(func):
            self.callbacks[payload] = func
            return func
        return decorator

    def register(self, update_type: str):
        """
        Decorator to register a generic handler for a specific update type.

        Example:
            @router.register("message_created")
            async def on_message(notification):
                log.info("Process message")
        """
        def decorator(func):
            if update_type not in self.handlers:
                self.handlers[update_type] = []
            self.handlers[update_type].append(func)
            return func
        return decorator

    async def publish(self, notification):
        """
        Processes an incoming notification and routes it to the first matching handler.
        Order: Commands -> Callbacks -> Update Type Handlers.
        """
        u_type = notification.type()
        try:
            chat_id = notification.chat_id()
            sender_id = notification.sender_id()
        except ValueError:
            chat_id, sender_id = 0, 0

        if u_type == "message_created":
            try:
                text = notification.text()
                if text and text.startswith("/"):
                    cmd = text.split(" ", 1)[0]
                    log.info("Received new command", chat_id=chat_id, user_id=sender_id, command=cmd)
                    if cmd in self.commands:
                        await self.commands[cmd](notification)
                        return
                else:
                    log.info("Received new message", chat_id=chat_id, user_id=sender_id, text=text)
            except Exception:
                pass

        elif u_type == "message_callback":
            try:
                payload = notification.text()
                log.info("Received new callback", chat_id=chat_id, user_id=sender_id, callback=payload)
                if payload in self.callbacks:
                    await self.callbacks[payload](notification)
                    return
            except Exception:
                pass
        
        elif u_type in ("bot_added", "bot_started", "bot_stopped"):
            log.info("Bot status updated", type=u_type, chat_id=chat_id)
            
        elif u_type in ("user_added", "user_removed"):
            log.info("User membership changed", type=u_type, chat_id=chat_id)
            
        elif u_type in ("dialog_muted", "dialog_unmuted", "dialog_cleared", "dialog_removed"):
            log.info("Dialog state updated", type=u_type, chat_id=chat_id)
            
        elif u_type in ("message_edited", "message_removed"):
            log.info("Message modified", type=u_type, chat_id=chat_id)
            
        elif u_type == "chat_title_changed":
            log.info("Chat settings modified", type=u_type, chat_id=chat_id)

        if u_type in self.handlers:
            for func in self.handlers[u_type]:
                await func(notification)