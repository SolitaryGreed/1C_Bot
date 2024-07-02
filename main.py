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
from from_state import Form
from love_metod.love_block import return_compliment, random_stickers, random_postcard
from back_def import create_data, format_number_phone, cancel_registration
from aiogram.fsm.context import FSMContext


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
                         "\n\n/schedule - Расписание \n/registration - Регистрация")


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
                await message.answer("Ой, что-то пошло не так")


# Регистрация в боте по номеру телефона
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
            elif response.status == 200 and str(response.headers["Text"]) == "The user is not in the database":
                await message.answer("Если вы новый пользователь нашего клуба тогда отправьте команду /registration")
            else:
                await message.answer("Ой, что-то пошло не так")


# Регистрация нового пользователя в нашем клубе
@dp.message(Command("registration"))
async def command_start(message: Message, state: FSMContext) -> None:
    await state.set_state(Form.name)
    await message.answer_document(document=types.FSInputFile("content/Agreement.pdf"), caption="Продолжая регистрацию "
                                                                                               "вы соглашаетесь с "
                                                                                               "правилами обработки "
                                                                                               "персональных "
                                                                                               "данных.\nВведи ваше "
                                                                                               "имя.\nЕсли вы передумали"
                                                                                               " введи слово 'Отмена'.")


# Ввод имени
@dp.message(Form.name)
async def process_name(message: Message, state: FSMContext) -> None:
    # Отмена регистрации
    if message.text == "Отмена":
        await cancel_registration(message, state)
    else:
        if set(".,:;!_*-+()/#¤%&)1234567890").isdisjoint(message.text):
            await state.update_data(name=message.text)
            await state.set_state(Form.surname)
            await message.answer("Введите вашу фамилию")
        else:
            await message.answer("Имя может содержать только буквы")


@dp.message(Form.surname)
async def process_name(message: Message, state: FSMContext) -> None:
    # Отмена регистрации
    if message.text == "Отмена":
        await cancel_registration(message, state)
    else:
        if set(".,:;!_*-+()/#¤%&)1234567890").isdisjoint(message.text):
            await state.update_data(surname=message.text)
            await state.set_state(Form.phone_number)
            await message.answer("Введите ваш номер телефона в формате: +7 (999) 999-99-99")
        else:
            await message.answer("Фамилия может содержать только буквы")


@dp.message(Form.phone_number)
async def process_name(message: Message, state: FSMContext) -> None:
    # Отмена регистрации
    if message.text == "Отмена":
        await cancel_registration(message, state)
    else:
        if not set("+-()1234567890").isdisjoint(message.text):
            data = await state.update_data(phone_number=message.text)
            await state.set_state(Form.gender)
            await message.answer("Введите ваш пол М или Ж")
        else:
            await message.answer("Номер телефона должен содержать только цифры и формат")


@dp.message(Form.gender)
async def process_name(message: Message, state: FSMContext) -> None:
    # Отмена регистрации
    if message.text == "Отмена":
        await cancel_registration(message, state)
    else:
        if message.text == "М" or message.text == "Ж":
            await state.update_data(gender=message.text)
            await state.update_data(user_id=message.from_user.id)
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=await Form.create_data(await state.get_data()), headers=headers) as response:
                    if response.status == 200 and str(response.headers["Text"]) == "New user registered":
                        await message.answer("Поздравляем с успешной регистрацией регистрацией")
                    elif response.status == 200 and str(response.headers["Text"]) == "Registered":
                        await message.answer("Вы уже являетесь клиентом нашего клуба")
                    elif response.status == 500:
                        await message.answer("Ой, что-то пошло не так")
        else:
            await message.answer("Введите М или Ж")


# Пасхалка для Тани
@dp.message(lambda message: message.text and message.text.lower() in ['/love_text', '/love_sticker', '/love_postcard'])
async def easter_egg(message: Message) -> None:
    if message.text == "/love_text":
        await message.answer(await return_compliment())
    elif message.text == "/love_sticker":
        await message.answer_sticker(await random_stickers())
    elif message.text == "/love_postcard":
        path, caption = await random_postcard()
        await message.answer_photo(photo=types.FSInputFile(path=path), caption=caption)


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
