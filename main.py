import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from difflib import SequenceMatcher

TOKEN = "6711555669:AAEyZzSl_HX4qIJIkz7i0gc0g-HGmcoM8ps"
CHANNEL_USERNAME = "@Pdfbazam"

bot = Bot(token=TOKEN)
dp = Dispatcher()

def similar(a, b):
    # Ikki matn qanchalik o'xshashligini 0 dan 1 gacha tekshiradi
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
    await callback.message.answer("Marhamat, izlamoqchi bo'lgan kitobingiz nomini yozib yuboring (harfi biroz xato bo'lsa ham topib beraman):", parse_mode="Markdown")
    await callback.answer()

@dp.message(F.text)
async def search_book_handler(message: types.Message):
    query = message.text.lower().strip()
    await message.answer("🔍 Qidirilmoqda...")
    
    found = False
    
    try:
        # Kanaldagi oxirgi xabarlarni tekshiramiz
        async for message_item in bot.get_chat_history(chat_id=CHANNEL_USERNAME, limit=100):
            if message_item.document and message_item.document.file_name:
                doc_name = message_item.document.file_name.lower()
                
                # Agar to'g'ridan-to'g'ri ichida bo'lsa yoki o'xshashlik 40% dan yuqori bo'lsa
                if query in doc_name or similar(query, doc_name) > 0.4:
                    await bot.send_document(
                        chat_id=message.chat.id,
                        document=message_item.document.file_id,
                        caption=f"✅ Mana, siz izlagan kitob: <b>{message_item.document.file_name}</b>",
                        parse_mode="HTML"
                    )
                    found = True
                    break
        
        if not found:
            await message.answer("❌ Kechirasiz, bu nomga o'xshash kitob kanaldan topilmadi. Iltimos, boshqacharoq yozib ko'ring.")
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("⚠️ Qidirishda xatolik yuz berdi. Bot kanalga to'liq admin qilinganligini tekshiring!")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
