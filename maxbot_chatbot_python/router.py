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
                print("Process message")
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

        match u_type:
            case "message_created":
                try:
                    text = notification.text()
                    if text and text.startswith("/"):
                        cmd = text.split(" ", 1)[0]
                        print(f"Received new command | chat_id: {chat_id}, user_id: {sender_id}, command: {cmd}")
                        if cmd in self.commands:
                            await self.commands[cmd](notification)
                            return
                    else:
                        print(f"Received new message | chat_id: {chat_id}, user_id: {sender_id}, text: {text}")
                except Exception:
                    pass

            case "message_callback":
                try:
                    payload = notification.text()
                    print(f"Received new callback | chat_id: {chat_id}, user_id: {sender_id}, callback: {payload}")
                    if payload in self.callbacks:
                        await self.callbacks[payload](notification)
                        return
                except Exception:
                    pass
        
            case "bot_added" | "bot_started" | "bot_stopped":
                print(f"Bot status updated | type: {u_type}, chat_id: {chat_id}")
                
            case "user_added" | "user_removed":
                print(f"User membership changed | type: {u_type}, chat_id: {chat_id}")
                
            case "dialog_muted" | "dialog_unmuted" | "dialog_cleared" | "dialog_removed":
                print(f"Dialog state updated | type: {u_type}, chat_id: {chat_id}")
                
            case "message_edited" | "message_removed":
                print(f"Message modified | type: {u_type}, chat_id: {chat_id}")
                
            case "chat_title_changed":
                print(f"Chat settings modified | type: {u_type}, chat_id: {chat_id}")

        if u_type in self.handlers:
            for func in self.handlers[u_type]:
                await func(notification)