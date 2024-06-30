import asyncio
import logging
import sys
import config

from aiogram.client.session import aiohttp
from aiogram import Bot, Dispatcher, F, types
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from love_metod.love_block import return_compliment, random_stickers, random_postcard
from back_def import create_data, format_number_phone

# Токен для бота
TOKEN = config.TOKEN
url = config.URL
headers = config.CONTENT_TYPE

# All handlers should be attached to the Router (or Dispatcher)
dp = Dispatcher()


# Повествование бота и команды для отправки
@dp.message(CommandStart())
async def command_start_handler(message: Message) -> None:
    await message.answer("Приветствуем вас в нашем боте! Тут вы можете получить расписание своих занятий."
                         "\n\n/schedule - Расписание")


# Расписание занятий
@dp.message(Command("schedule"))
async def text_handler(message: Message) -> None:
    # Создаем словарь с нужными нам значениями для отправки
    data = await create_data(message)
    # Отправляем данные через POST и получаем ответ
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200 and str(response.headers["Text"]) == "No register":
                await message.answer("Вам нужно зарегистрироваться в нашем боте для этого отправьте номер телефона в "
                                     "формате: +7 (999) 999-99-99")
            else:
                await message.answer("Ой что-то пошло не так")


# Получения номера телефона
@dp.message(F.text.regexp(r'\+7\s*\(?985\)?[\s-]*\d{3}[\s-]*\d{2}[\s-]*\d{2}'))
async def text_handler(message: Message) -> None:
    # Создаем словарь с нужными нам значениями для отправки
    data = await format_number_phone(await create_data(message))
    # Отправляем данные через POST и получаем ответ
    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=data, headers=headers) as response:
            if response.status == 200 and str(response.headers["Text"]) == "Registered":
                await message.answer("Вы уже зарегистрированы в нашем боте")
            elif response.status == 200 and str(response.headers["Text"]) == "User is registered":
                await message.answer("Поздравлю вы зарегистрированы в нашем боте")
            else:
                await message.answer("Ой что-то пошло не так")


# Пасхалка для женщины
@dp.message(lambda message: message.text and message.text.lower() in ['/love_text', '/love_sticker', '/love_postcard'])
async def easter_egg(message: Message) -> None:
    if message.text == "/love_text":
        await message.answer(await return_compliment())
    elif message.text == "/love_sticker":
        await message.answer_sticker(await random_stickers())
    elif message.text == "/love_postcard":
        path, caption = await random_postcard()
        await message.answer_photo(photo=types.FSInputFile(path=path), caption=caption)


# Узнать что пишет
@dp.message(F.text)
async def easter_egg(message: Message) -> None:
    await message.forward(config.CHAT_ID)


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
