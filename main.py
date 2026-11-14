import asyncio
import logging
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# 1. BOT TOKENINGIZNI YOZING
TOKEN = "6711555669:AAEyZzSl_HX4qIJIkz7i0gc0g-HGmcoM8ps"

# 2. KANAL USERNAME'INI YOZING (Masalan: "@kitoblar_kanali")
# Eslatma: Bot ushbu kanalga admin bo'lishi kerak!
CHANNEL_USERNAME = "@Pdfbazam"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# /start buyrug'i
@dp.message(Command("start"))
async def start_handler(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Kitob qidirish", callback_data="search_book")
    
    text = (
        "Assalomu alaykum! Botimizga xush kelibsiz. ✨\n\n"
        "Kitob qidirish uchun pastdagi tugmani bosing:"
    )
    await message.answer(text, reply_markup=builder.as_markup())

# Tugma bosilganda
@dp.callback_query(F.data == "search_book")
async def process_search_button(callback: types.CallbackQuery):
    await callback.message.answer("Marhamat, izlamoqchi bo'lgan kitobingiz nomini yozib yuboring (masalan: *1984*):", parse_mode="Markdown")
    await callback.answer()

# Foydalanuvchi kitob nomini yozganda kanaldan qidirish
@dp.message(F.text)
async def search_book_handler(message: types.Message):
    query = message.text.lower()
    await message.answer("🔍 Kitob qidirilmoqda, iltimos kuting...")
    
    found = False
    
    try:
        # Kanal oxirgi xabarlaridan qidirish (oddiy qidiruv usuli)
        # Eslatma: Kanalda bot admin bo'lishi va xabarlarni o'qiy olishi kerak.
        # Kanaldan oxirgi 100 ta xabarni tekshiramiz:
        # (Real loyihalarda bazada saqlanadi, lekin kichik bot uchun bu ham ishlaydi)
        
        # Hozircha oddiy namuna sifatida foydalanuvchiga kanalni ko'rsatamiz 
        # yoki kanaldagi fayllar nomini solishtiramiz.
        await message.answer(
            f"Siz <b>{message.text}</b> deb yozdingiz.\n"
            f"Hozircha kanalimizdan ushbu nomdagi PDF fayllarni qidirish funksiyasi sozlanmoqda. "
            f"Iltimos, kanalga admin huquqini berganingizni tekshiring!",
            parse_mode="HTML"
        )
        
    except Exception as e:
        logging.error(f"Xatolik: {e}")
        await message.answer("Qidirish vaqtida xatolik yuz berdi.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
