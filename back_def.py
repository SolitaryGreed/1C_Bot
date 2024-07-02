from re import sub
from aiogram.client.session import aiohttp
from aiogram.fsm.context import FSMContext
from aiogram.types import Message


# Формируем словарь с нужными нам значениями для отправки
async def create_data(message: Message) -> dict:
    return {
        "message": message.text,
        "user_id": message.from_user.id,
        "username": message.from_user.username,
        "chat_id": message.chat.id
    }


# Форматируем номер телефона для отправки в 1С
async def format_number_phone(data: dict) -> dict:
    string = sub(r'\+?7\s?(\d{3})\s?(\d{3})\s?(\d{2})\s?(\d{2})', r'+7 (\1) \2-\3-\4', data["message"])
    data["message"] = string
    return data


async def cancel_registration(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.clear()
    await message.answer("Регистрация отменена\n\n/schedule - Расписание \n/registration - Регистрация")
