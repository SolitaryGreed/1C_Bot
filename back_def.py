from re import sub
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


# Отмена регистрации
async def cancel_registration(message: Message, state: FSMContext) -> None:
    # Получаем текущее состояние регистрации
    current_state = await state.get_state()
    if current_state is None:
        return
    # Очищаем все полученные данные и выводим сообщение об отмене регистрации
    await state.clear()
    await message.answer("Регистрация отменена\n\n/schedule - Расписание \n/registration - "
                         "Регистрация\n/cancel_schedule - Отмена записи")


# Отмена отмены записи
async def schedule_cancel(message: Message, state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state is None:
        return
    # Очищаем все полученные данные и выводим сообщение об отмене регистрации
    await state.clear()
    await message.answer("Вы вернулись на главную\n\n/schedule - Расписание \n/registration - "
                         "Регистрация\n/cancel_schedule - Отмена записи")


# Форматируем строку для пользователя
async def format_string(json_text: str) -> str:
    split_string = json_text[10:].split("||")
    result_string = "У вас есть запись"
    for i in split_string:
        current_data = i.split("//")
        # Проверяем есть ли все данные для ответа пользователю
        if len(current_data) == 4:
            result_string += (
                f'\nНомер записи {current_data[0]}:'
                f'\nВ клуб {current_data[1]}'
                f'\nК тренеру: {current_data[2]}'
                f'\nВремя: {current_data[3][:-3]}'
                f'\n'
            )
        # Если данные не полные, то сообщим об этом пользователю
        else:
            result_string += (
                f'\nНомер записи {current_data[0]}:'
                f'\nДанные о записи не полные обратитесь в поддержку'
                f'\n'
            )
    return result_string
