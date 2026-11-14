import asyncio
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command

# TOKENINGIZNI SHU YERGA YOZASIZ (qo'shtirnoq ichiga)
TOKEN = "6711555669:AAEyZzSl_HX4qIJIkz7i0gc0g-HGmcoM8ps"

bot = Bot(token=TOKEN)
dp = Dispatcher()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    await message.answer("Salom! Botimiz Render'da muvaffaqiyatli ishlayapti! 🚀")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
