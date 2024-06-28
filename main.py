import asyncio
from redis.asyncio import Redis
from data import config
from handlers import router
from aiogram.fsm.storage.redis import RedisStorage
from aiogram import Bot, Dispatcher


r = Redis(host='localhost', port=6379, decode_responses=True)
storage = RedisStorage(redis=r)
bot = Bot(token=config.bot_token)
dp = Dispatcher(storage=storage)


async def main():
    dp.include_router(router)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
