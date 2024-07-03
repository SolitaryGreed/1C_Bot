from aiogram.fsm.state import StatesGroup, State


# FMS состояние для сохранения ответа пользователя
class Form(StatesGroup):
    # Данные для регистрации
    name = State()
    surname = State()
    phone_number = State()
    gender = State()
    user_id = State()
    # Данные для отмены записи
    number_record = State()

    # Метод для создания словаря для отправки в 1С для регистрации нового пользователя
    async def create_data(self: dict) -> dict:
        return {
            "message": "/registration",
            "name": self["name"],
            "surname": self["surname"],
            "phone_number": self["phone_number"],
            "gender": self["gender"],
            "user_id": self["user_id"]
        }

    # Метод для создания словаря для отправки в 1С для отмены записи к тренеру
    async def create_data_cancel(self: dict) -> dict:
        return {
            "message": "/cancel_schedule",
            "user_id": self["user_id"],
            "number_record": self["number_record"]
        }
