import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "6711555669:AAEyZzSl_HX4qIJIkz7i0gc0g-HGmcoM8ps"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Kitoblar bazasi
BOOKS = [
    {
        "title": "Adabiyot 11-sinf",
        "keywords": ["adabiyot", "11-sinf", "adabiyot 11"], 
        "file_id": "BQACAgIAAxkBAAIG4Wr4EB2J8TNihqGA956YRd319vXwAAJyHgAKPDAU1jxCIG0lX1APQQ", 
        "caption": "📖 Adabiyot 11-sinf (PDF)"
    },
    {
        "title": "Yangi kitob",
        "keywords": ["yangi", "kitob"], 
        "file_id": "BQACAgQAAxkBAAIHBWr4evkjAS1Fkz8H4HzYfch7fmlOAALsHgACKPDAU3VPXoo5QPOFPQQ", 
        "caption": "📖 Yangi kitob (PDF)"
    },
]

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
    await callback.message.answer("Marhamat, izlamoqchi bo'lgan kitobingiz nomini yozib yuboring:")
    await callback.answer()

@dp.message(F.document)
async def get_file_id(message: types.Message):
    await message.answer(
        f"<b>Fayl qabul qilindi! Nomi va IDsi:</b>\n\n"
        f"<code>{message.document.file_id}</code>",
        parse_mode="HTML"
    )

@dp.message(F.text)
async def search_book_handler(message: types.Message):
    query = message.text.lower().strip()
    
    matched_books = []
    for book in BOOKS:
        # Xatolik bermaydigan to'g'ri qidiruv sharti
        if any(kw in query for kw in book["keywords"]) or query in book["title"].lower():
            matched_books.append(book)
            
    if matched_books:
        response_text = f"🔍 <b>{len(matched_books)} ta natija topildi:</b>\n\n"
        for i, book in enumerate(matched_books, 1):
            response_text += f"{i}. 📄 {book['title']}\n"
            
        await message.answer(response_text, parse_mode="HTML")
        
        for book in matched_books:
            await bot.send_document(
                chat_id=message.chat.id,
                document=book["file_id"],
                caption=book["caption"]
            )
    else:
        await message.answer("❌ Kechirasiz, bu nomdagi kitob topilmadi.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
