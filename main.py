import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

TOKEN = "6711555669:AAEyZzSl_HX4qIJIkz7i0gc0g-HGmcoM8ps"
CHANNEL_USERNAME = "@pdflar_muhokama"
ADMIN_USERNAMES = ["irifq", "meyaq"]

os.makedirs("/app/data", exist_ok=True)
BOOKS_FILE = "/app/data/books.json"
USERS_FILE = "/app/data/users.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

class AdminBookState(StatesGroup):
    waiting_for_caption = State()

def load_json(filename, default_value):
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return default_value
    return default_value

def save_json(filename, data):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Xatolik ({filename}): {e}")

users_db = load_json(USERS_FILE, {})

def transliterate(text: str) -> str:
    latin = ('sh', 'ch', 'g\'', 'o\'', 'ya', 'yu', 'ye', 'yo', 'a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z')
    cyrillic = ('ш', 'ч', 'ғ', 'ў', 'я', 'ю', 'е', 'ё', 'а', 'б', 'д', 'э', 'ф', 'г', 'ҳ', 'и', 'ж', 'к', 'л', 'м', 'н', 'о', 'п', 'қ', 'р', 'с', 'т', 'у', 'в', 'х', 'й', 'з')
    text_lower = text.lower()
    for l, c in zip(latin, cyrillic):
        text_lower = text_lower.replace(l, c)
    return text_lower

async def check_subscription(user_id: int) -> bool:
    try:
        member = await bot.get_chat_member(chat_id=CHANNEL_USERNAME, user_id=user_id)
        if member.status in ["creator", "administrator", "member"]:
            return True
    except Exception:
        pass
    return False

@dp.message(Command("start"))
async def start_handler(message: types.Message):
    user_id = message.from_user.id
    users_db[str(user_id)] = {"name": message.from_user.full_name}
    save_json(USERS_FILE, users_db)
    
    if not await check_subscription(user_id):
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 Guruhga a'zo bo'lish", url=f"https://t.me/pdflar_muhokama")
        builder.button(text="✅ Obunani tekshirish", callback_data="check_sub")
        builder.adjust(1)
        await message.answer(
            f"<b>✨ Assalomu alaykum!</b>\n\nBotdan foydalanish uchun quyidagi guruhga a'zo bo'ling:\n👉 {CHANNEL_USERNAME}",
            reply_markup=builder.as_markup(), parse_mode="HTML"
        )
    else:
        await show_main_menu(message)

@dp.message(Command("backup"))
async def backup_handler(message: types.Message):
    if message.from_user.username and message.from_user.username.lower() in ADMIN_USERNAMES:
        if os.path.exists(BOOKS_FILE):
            await message.answer_document(document=types.FSInputFile(BOOKS_FILE), caption="📦 <b>Base (`books.json`)</b>", parse_mode="HTML")

@dp.message(Command("stat"))
async def stat_handler(message: types.Message):
    if message.from_user.username and message.from_user.username.lower() in ADMIN_USERNAMES:
        books_db = load_json(BOOKS_FILE, [])
        await message.answer(f"📊 Jami kitoblar: <b>{len(books_db)} ta</b>", parse_mode="HTML")

@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: types.CallbackQuery):
    if await check_subscription(callback.from_user.id):
        try:
            await callback.message.delete()
        except Exception:
            pass
        await show_main_menu(callback.message)
    else:
        await callback.answer("❌ Guruhga a'zo bo'lmadingiz!", show_alert=True)

async def show_main_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Kitob qidirishni boshlash", callback_data="search_prompt")
    text = "<b>✨ Xush kelibsiz!</b>\n\nKitob nomini shu yerga yozib yuboring:"
    if isinstance(message, types.CallbackQuery):
        await message.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "search_prompt")
async def search_prompt(callback: types.CallbackQuery):
    await callback.message.answer("✍️ Qidirmoqchi bo'lgan kitob nomini yozing:")
    await callback.answer()

@dp.callback_query(F.data.startswith("get_"))
async def send_book(callback: types.CallbackQuery):
    try:
        book_id = int(callback.data.split("_")[1])
    except Exception:
        await callback.answer("Xatolik!", show_alert=True)
        return

    books_db = load_json(BOOKS_FILE, [])
    book = next((b for b in books_db if b["id"] == book_id), None)
    if book:
        await bot.send_document(
            chat_id=callback.message.chat.id,
            document=book["file_id"],
            caption=book.get("caption", f"📖 {book['title']}\n\n📥 Bot: @Pdflarbot"),
            parse_mode="HTML"
        )
        await callback.answer("📂 Yuborildi!")
    else:
        await callback.answer("❌ Kitob topilmadi.", show_alert=True)

@dp.message(F.document)
async def handle_docs(message: types.Message, state: FSMContext):
    if not message.from_user.username or message.from_user.username.lower() not in ADMIN_USERNAMES:
        return
    
    doc = message.document
    if doc.file_name.lower() == "books.json":
        file_info = await bot.get_file(doc.file_id)
        await bot.download(file_info, destination=BOOKS_FILE)
        books_db = load_json(BOOKS_FILE, [])
        await message.answer(f"✅ Baza yangilandi! Jami: {len(books_db)} ta")
        return
        
    if not doc.file_name.lower().endswith(".pdf"):
        await message.answer("⚠️ Faqat PDF yuboring!")
        return
        
    books_db = load_json(BOOKS_FILE, [])
    if any(b["file_id"] == doc.file_id for b in books_db):
        await message.answer("⚠️ Bu PDF allaqachon bazada bor!")
        return

    await state.update_data(file_id=doc.file_id)
    await state.set_state(AdminBookState.waiting_for_caption)
    await message.answer("✍️ Kitob nomini yozing:")

@dp.message(AdminBookState.waiting_for_caption, F.text)
async def save_book(message: types.Message, state: FSMContext):
    title = message.text.strip()
    data = await state.get_data()
    file_id = data.get("file_id")
    
    if not file_id:
        await state.clear()
        return

    books_db = load_json(BOOKS_FILE, [])
    new_id = (max([b.get("id", 0) for b in books_db]) + 1) if books_db else 1
    
    words = [w for w in title.lower().split() if len(w) > 0]
    cyr_words = [transliterate(w) for w in words]
    keywords = list(set([title.lower(), transliterate(title.lower())] + words + cyr_words))

    new_book = {
        "id": new_id,
        "title": title,
        "keywords": keywords,
        "file_id": file_id,
        "caption": f"📖 <b>{title}</b>\n\n📥 Bot: @Pdflarbot"
    }
    books_db.append(new_book)
    save_json(BOOKS_FILE, books_db)
    await state.clear()
    
    await message.answer(f"✅ Qo'shildi!\n📚 Nomi: <b>{title}</b>\n🆔 ID: <b>{new_id}</b>", parse_mode="HTML")

@dp.message(F.text)
async def search_books(message: types.Message):
    if not await check_subscription(message.from_user.id):
        await start_handler(message)
        return
    
    books_db = load_json(BOOKS_FILE, [])
    query = message.text.strip().lower()
    is_admin = message.from_user.username and message.from_user.username.lower() in ADMIN_USERNAMES
    
    matched = []
    clean_q = query.replace("id", "").strip()
    if is_admin and clean_q.isdigit():
        matched = [b for b in books_db if b["id"] == int(clean_q)]
    else:
        q_cyr = transliterate(query)
        for b in books_db:
            t = b["title"].lower()
            if query in t or q_cyr in transliterate(t) or any(query in kw for kw in b.get("keywords", [])):
                if b not in matched:
                    matched.append(b)
                    
    if matched:
        text = f"📚 <b>Topildi:</b> {len(matched)} ta\n\n"
        builder = InlineKeyboardBuilder()
        for b in matched[:20]:
            builder.button(text=f"📥 {b['title'][:30]}", callback_data=f"get_{b['id']}")
        builder.adjust(1)
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer("🔍 Hech narsa topilmadi.")

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.get_updates(offset=-1)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
