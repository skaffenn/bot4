import os
from aiogram.types import FSInputFile
from aiogram import types, Bot
from data import config
from openai import AsyncOpenAI
from aiogram.fsm.context import FSMContext
from models import UsersThreadIds


client = AsyncOpenAI(api_key=config.openai_api_token)
bot = Bot(token=config.bot_token)
assistant_id = config.assistant_id
vector_store_id = config.vector_store_id


async def answer_voice(message: types.Message, state: FSMContext):
    chat_id = message.from_user.id
    ivoice_path = f"ivoice_{str(chat_id)}.ogg"
    await download_voice(message, ivoice_path)
    transcription_model = "whisper-1"
    transcription = await get_transcription(ivoice_path, transcription_model)
    role = get_role("user")
    text_answer, thread_id = await get_answer(transcription, assistant_id)
    print(text_answer)
    ovoice_path = f"ovoice_{str(chat_id)}.ogg"
    voice_over_model = "tts-1"
    voice_model = get_voice_model("alloy")
    await voice_over(text_answer, ovoice_path, voice_over_model, voice_model)
    await send_voice(message, ovoice_path)
    await state.update_data(thread_id=thread_id)
    await state.set_state(UsersThreadIds.thread_id)


async def download_voice(message: types.Message, ivoice_path: str):
    voice_id = message.voice.file_id
    voice_file = await bot.get_file(voice_id)
    voice_file_path = voice_file.file_path
    await bot.download_file(voice_file_path, ivoice_path)


async def get_transcription(ivoice_path: str, model: str):
    with open(ivoice_path, "rb") as audio_file:
        transcription = await client.audio.transcriptions.create(model=model, file=audio_file, response_format="text")
    return transcription


async def get_answer(transcription: str, assistant_id:str):
    thread = await client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": transcription,

            }
        ]
    )
    run = await client.beta.threads.runs.create_and_poll(
        thread_id=thread.id, assistant_id=assistant_id
    )
    if run.status == "completed":
        messages = await client.beta.threads.messages.list(thread_id=thread.id)
        message_content = messages.data[0].content[0].text
        annotations = message_content.annotations
        for index, annotation in enumerate(annotations):
            if file_citation := getattr(annotation, "file_citation", None):
                cited_file = await client.files.retrieve(file_citation.file_id)
                message_content.value = message_content.value.replace(annotation.text, f"[{cited_file.filename}]")
        return message_content.value, thread.id


async def voice_over(text_input: str, path: str, voice_over_model: str, voice_model):
    response = await client.audio.speech.create(model=voice_over_model, voice=voice_model, input=text_input)
    response.stream_to_file(path)


async def send_voice(message: types.Message, path: str):
    vc = FSInputFile(path)
    await message.answer_voice(vc)


def get_role(role: str):
    if role in ["user", "assistant"]:
        return role
    else:
        raise ValueError


def get_voice_model(model: str):
    if model in ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]:
        return model
    else:
        raise ValueError


def clear_cache(path_list: list[str]):
    for path in path_list:
        os.remove(path)
