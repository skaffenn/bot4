from aiogram import types, F, Router
from aiogram.filters import CommandStart
from functions import answer_voice
from aiogram.fsm.context import FSMContext


router = Router()


@router.message(CommandStart())
async def starting(message: types.Message):
    await message.answer("Привет. Для общения со мной отправь голосовое сообщение, а я на него отвечу")


@router.message(F.voice)
async def handle_voice(message: types.Message, state: FSMContext):
    await answer_voice(message, state)


