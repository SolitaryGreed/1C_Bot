from aiogram.fsm.state import StatesGroup, State


class Form(StatesGroup):
    name = State()
    surname = State()
    phone_number = State()
    gender = State()
    user_id = State()

    async def create_data(self: dict) -> dict:
        return {
            "message": "/registration",
            "name": self["name"],
            "surname": self["surname"],
            "phone_number": self["phone_number"],
            "gender": self["gender"],
            "user_id": self["user_id"]
        }
