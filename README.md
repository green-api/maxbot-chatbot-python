# maxbot-chatbot-python

`maxbot-chatbot-python` — это асинхронный фреймворк для создания масштабируемых ботов для MAX Bot API на языке Python. 
Построенная на основе [`maxbot_api_client_python`](https://github.com/green-api/maxbot-api-client-python), эта библиотека предоставляет чистый маршрутизатор, автоматическое получение обновлений (Long Polling) и надежный менеджер состояний (FSM) для построения многошаговых диалоговых сценариев.

Для использования библиотеки требуется получить токен бота в консоли разработчика MAX API.

## API

Документацию по REST API MAX можно найти по ссылке [https://dev.max.ru/docs-api](https://dev.max.ru/docs-api). Библиотека является оберткой для REST API, поэтому документация по указанной выше ссылке также применима к используемым здесь моделям.

## Поддержка

[![Support](https://img.shields.io/badge/support@green--api.com-D14836?style=for-the-badge&logo=gmail&logoColor=white)](mailto:support@green-api.com)
[![Support](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/greenapi_support_ru_bot)
[![Support](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://wa.me/77780739095)

## Руководства и новости

[![Guides](https://img.shields.io/badge/YouTube-%23FF0000.svg?style=for-the-badge&logo=YouTube&logoColor=white)](https://www.youtube.com/@green-api)
[![News](https://img.shields.io/badge/Telegram-2CA5E0?style=for-the-badge&logo=telegram&logoColor=white)](https://t.me/green_api)
[![News](https://img.shields.io/badge/WhatsApp-25D366?style=for-the-badge&logo=whatsapp&logoColor=white)](https://whatsapp.com/channel/0029VaHUM5TBA1f7cG29nO1C)

## Установка

**Убедитесь, что у вас установлен Python версии 3.9 или выше.**

```bash
python --version
```

**Установите библиотеку:**
```bash
pip install github.com/green-api/maxbot-chatbot-python
```

---

## Использование и примеры

### Инициализация бота

Чтобы начать получать и отвечать на сообщения, настройте бота, используя ваш `BaseURL` и `Token`, затем запустите механизм опроса.

```python
import asyncio, logging

from maxbot_api_client_python import API, Config
from maxbot_chatbot_python import Bot, MapStateManager

async def main():
    api_client = API(cfg=Config(
        base_url="https://platform-api.max.ru/", 
        token="YOUR_MAXBOT_TOKEN", 
        timeout=35
    ))

    bot = Bot(api_client)
    bot.state_manager = MapStateManager(init_data={})

    polling_task = asyncio.create_task(bot.start_polling())

    try:
        await polling_task
    except asyncio.CancelledError:
        pass

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Bot stopped by user")
```

### Маршрутизация команд, сообщений и коллбэков

Встроенный **маршрутизатор** (`Router`) позволяет легко обрабатывать конкретные команды (начинающиеся со слэша `/`) и нажатия на **inline-кнопки** (коллбэки).

```python
@bot.router.command("/start")
async def start_command(notification):
    await notification.reply("Hello! Welcome to the MAX Bot.")

@bot.router.register("message_created")
async def ping_handler(notification):
    try:
        if notification.text() == "ping":
            await notification.reply("pong")
    except ValueError:
        pass

@bot.router.callback("accept_rules")
async def rules_callback(notification):
    await notification.reply("*Thank you for accepting the rules!*", format_type="markdown")
    await notification.answer_callback("Success!")
```

### Управление состояниями и Сцены (FSM)

Для сложных многошаговых диалогов (например, регистрация или анкетирование) используйте **Менеджер состояний** (`StateManager`) и **Сцены** (`Scene`).

```python
from maxbot_chatbot_python import Scene

class RegistrationScene(Scene):
    async def start(self, notification):
        try:
            text = notification.text()
        except ValueError:
            return

        if text == "/start":
            await notification.reply("Let's register! What is your *login*?", "markdown")
            return 
        
        if len(text) >= 4:
            if notification.state_manager:
                notification.state_manager.update_state_data(notification.state_id, {"login": text})
            
            await notification.reply(f"**Login** `{text}` accepted. Now enter your **password**:", "markdown")
            notification.activate_next_scene(PasswordScene())
        else:
            await notification.reply("Login must be **at least 4 characters long**.", "markdown")

class PasswordScene(Scene):
    async def start(self, notification):
        try:
            password = notification.text()
        except ValueError:
            return

        state_data = notification.state_manager.get_state_data(notification.state_id)
        login = state_data.get("login", "Unknown")

        await notification.reply(f"Success! Profile created.\nLogin: `{login}`\nPass: `{password}`", "markdown")

        notification.activate_next_scene(RegistrationScene())


bot.state_manager = MapStateManager(init_data={"step": "start"})
bot.state_manager.set_start_scene(RegistrationScene())

@bot.router.register("message_created")
async def fsm_handler(notification):
    current_scene = notification.get_current_scene()
    if current_scene:
        await current_scene.start(notification)
```

### Ответ с медиафайлами

Обертка `Notification` содержит готовые асинхронные методы для отправки файлов, геолокаций, стикеров и статусов набора текста.

```python
@bot.router.command("/photo")
async def send_photo(notification):
    await notification.show_action("upload_photo")

    await notification.reply_with_media(
        text="Check out this image!", 
        format_type="markdown", 
        file_source="[https://example.com/image.png](https://example.com/image.png)"
    )
```

### Эхо-бот 

```python
import asyncio

from maxbot_api_client_python import API, Config
from maxbot_chatbot_python import Bot, MapStateManager

async def main():
    api_client = API(cfg = Config(
        base_url="https://platform-api.max.ru/", 
        token="YOUR_MAXBOT_TOKEN"
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

```
