import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from difflib import SequenceMatcher

TOKEN = "6711555669:AAEyZzSl_HX4qIJIkz7i0gc0g-HGmcoM8ps"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Kitoblar bazasi (shu yerga o'z kitoblaringizni qo'shib qo'yasiz)
BOOKS = [
    {
        "name": "adabiyot", 
        "file_id": "BQACAgIAAxkBAAI...", # Shu yerga haqiqiy PDF fayl ID sini yozasiz
        "caption": "📖 Adabiyot kitobi (PDF)"
    },
]

def similar(a, b):
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Kitob qidirish", callback_data="search_book")
    
    text = (
        "Assalomu alaykum! Botimizga xush kelibsiz. ✨\n\n"
        "Kitob qidirish uchun pastdagi tugmani bosing:"
    )
    await message.answer(text, reply_markup=builder.as_markup())

@dp.callback_query(F.data == "search_book")
async def process_search_button(callback: types.CallbackQuery):
    await callback.message.answer("Marhamat, izlamoqchi bo'lgan kitobingiz nomini yozib yuboring:", parse_mode="Markdown")
    await callback.answer()

# Botga istalgan PDF faylni tashlasangiz, uning ID sini chiqarib beradi
@dp.message(F.document)
async def get_file_id(message: types.Message):
    await message.answer(
        f"<b>Fayl qabul qilindi!</b>\n\n"
        f"Nomi: <code>{message.document.file_name}</code>\n"
        f"File ID: <code>{message.document.file_id}</code>",
        parse_mode="HTML"
    )

@dp.message(F.text)
async def search_book_handler(message: types.Message):
    query = message.text.lower().strip()
    
    found = False
    for book in BOOKS:
        if query in book["name"].lower() or similar(query, book["name"].lower()) > 0.4:
            await bot.send_document(
                chat_id=message.chat.id,
                document=book["file_id"],
                caption=book["caption"]
            )
            found = True
            break
            
    if not found:
        await message.answer("❌ Kechirasiz, bu nomdagi kitob topilmadi. Avval botga PDF tashlab fayl ID oling!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.main(main()) if hasattr(asyncio, 'main') else asyncio.run(main())
