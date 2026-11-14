import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from difflib import SequenceMatcher

TOKEN = "6711555669:AAEyZzSl_HX4qIJIkz7i0gc0g-HGmcoM8ps"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# Guruh ID raqami (rasmda ko'rsatilgan ID: 4433974944, guruhlar uchun oldiga -100 qo'shiladi)
GROUP_CHAT_ID = -1004433974944

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

@dp.message(F.text)
async def search_book_handler(message: types.Message):
    query = message.text.lower().strip()
    await message.answer("🔍 Qidirilmoqda...")
    
    found = False
    try:
        # Guruh tarixidan xabarlarni o'qiymiz
        async for msg in bot.get_chat_history(chat_id=GROUP_CHAT_ID, limit=100):
            if msg.document and msg.document.file_name:
                file_name = msg.document.file_name.lower()
                # Agar to'g'ridan-to'g'ri ichida bo'lsa yoki o'xshashlik 40% dan yuqori bo'lsa
                if query in file_name or similar(query, file_name) > 0.4:
                    await bot.send_document(
                        chat_id=message.chat.id,
                        document=msg.document.file_id,
                        caption=f"✅ Mana siz izlagan kitob: <b>{msg.document.file_name}</b>",
                        parse_mode="HTML"
                    )
                    found = True
                    break
        
        if not found:
            await message.answer("❌ Kechirasiz, bu nomdagi kitob guruhdan topilmadi.")
            
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("⚠️ Qidirishda xatolik yuz berdi. Bot guruhda admin ekanligini va ID to'g'riligini tekshiring.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
