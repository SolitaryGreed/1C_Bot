import asyncio
import logging
import sys
import config

from aiogram.client.session import aiohttp
from aiogram import Bot, Dispatcher, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message

# Bot token
TOKEN = config.TOKEN

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Приветствуем вас в нашем боте! Тут вы можете получить расписание своих занятий.")


@dp.message(F.text, Command("schedule"))
async def text_handler(message: Message) -> None:

    if not message.from_user.is_bot:
        url = config.URL
        headers = {'Content-Type': 'application/json'}
        data = {
            "message": message.text,
            "user_id": message.from_user.id,
            "username": message.from_user.username,
            "chat_id": message.chat.id
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data, headers=headers) as response:
                if response.status == 200:
                    await message.reply(str(response.headers["Text"]))
                else:
                    await message.reply("Failed to forward message to 1C.")
    else:
        return


async def main() -> None:
    # Initialize Bot instance with default bot properties which will be passed to all API calls
    bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))

    # We delete all accumulated messages when the bot is turned on
    await bot.delete_webhook(drop_pending_updates=True)

    # And the run events dispatching
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, stream=sys.stdout)
    asyncio.run(main())
