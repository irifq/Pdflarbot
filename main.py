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
ARCHIVE_CHANNEL = "@pdfbazam"  # Kitoblar turgan kanal
ADMIN_USERNAMES = ["irifq", "meyaq"]
BOOKS_FILE = "books.json"
USERS_FILE = "users.json"

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
        logging.error(f"Faylga saqlashda xatolik ({filename}): {e}")

users_db = load_json(USERS_FILE, {})
books_db = load_json(BOOKS_FILE, [])

def transliterate(text: str) -> str:
    latin = ('sh', 'ch', 'g\'', 'o\'', 'ya', 'yu', 'ye', 'yo', 'a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z')
    cyrillic = ('ш', 'ч', 'ғ', 'ў', 'я', 'ю', 'е', 'ё', 'а', 'б', 'д', 'э', 'ф', 'г', 'ҳ', 'и', 'ж', 'к', 'л', 'м', 'н', 'о', 'п', 'қ', 'р', 'с', 'т', 'у', 'в', 'х', 'й', 'з')
    
    text_lower = text.lower()
    for l, c in zip(latin, cyrillic):
        text_lower = text_lower.replace(l, c)
    return text_lower

def generate_keywords(title: str):
    raw_name = title.lower()
    words = [w for w in raw_name.replace("—", " ").replace("-", " ").split() if len(w) > 1]
    cyr_words = [transliterate(w) for w in words]
    lat_cyr_title = transliterate(raw_name)
    return list(set([raw_name, lat_cyr_title] + words + cyr_words))

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
    users_db[str(user_id)] = {
        "name": message.from_user.full_name,
        "username": message.from_user.username
    }
    save_json(USERS_FILE, users_db)
    
    if not await check_subscription(user_id):
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 Guruhga a'zo bo'lish", url=f"https://t.me/pdflar_muhokama")
        builder.button(text="✅ Obunani tekshirish", callback_data="check_sub")
        builder.adjust(1)
        
        text = (
            "<b>Assalomu alaykum!</b> Botimizdan foydalanish uchun oldin quyidagi guruhimizga a'zo bo'ling:\n\n"
            f"👉 {CHANNEL_USERNAME}\n\n"
            "A'zo bo'lgach, <b>«✅ Obunani tekshirish»</b> tugmasini bosing:"
        )
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await show_main_menu(message)

@dp.message(Command("stat"))
async def stat_handler(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
    
    total_users = len(users_db)
    total_books = len(books_db)
    await message.answer(f"📊 <b>Statistika:</b>\n\nFoydalanuvchilar: <b>{total_users}</b> ta\nKitoblar bazasi: <b>{total_books}</b> ta", parse_mode="HTML")

# --- KANALdagi barcha kitoblarni avtomatik o'qib olish (/sync) ---
@dp.message(Command("sync"))
async def sync_channel_books(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
    
    msg = await message.answer("🔄 Kanal skaner qilinmoqda, iltimos kuting...")
    
    try:
        global books_db
        synced_count = 0
        
        # Telegram kanaldagi so'nggi xabarlarni o'qib chiqamiz
        # (Bot kanalga admin bo'lishi va kanal xabarlarini o'qiy olishi kerak)
        async for history_msg in bot.get_chat_history(chat_id=ARCHIVE_CHANNEL, limit=100):
            if history_msg.document:
                file_id = history_msg.document.file_id
                caption = history_msg.caption
                
                if caption:
                    # Captiondan "📖 " yoki "(PDF)" kabi ortiqcha narsalarni tozalab olamiz
                    clean_title = caption.replace("📖", "").replace("(PDF)", "").strip()
                else:
                    # Agar caption bo'lmasa fayl nomidan olamiz
                    file_name = history_msg.document.file_name or "Noma'lum kitob"
                    clean_title = file_name[:-4] if file_name.endswith(".pdf") else file_name
                    clean_title = clean_title.replace("_", " ").replace("-", " ")

                # Agar bu file_id bazada hali bo'lmasa, qo'shamiz
                if not any(b["file_id"] == file_id for b in books_db):
                    new_id = max([b["id"] for b in books_db], default=0) + 1
                    keywords = generate_keywords(clean_title)
                    
                    books_db.append({
                        "id": new_id,
                        "title": clean_title,
                        "keywords": keywords,
                        "file_id": file_id,
                        "caption": f"📖 {clean_title} (PDF)"
                    })
                    synced_count += 1

        save_json(BOOKS_FILE, books_db)
        await msg.edit_text(f"✅ <b>Sinxronizatsiya muvaffaqiyatli yakunlandi!</b>\n\nKanal这样做dan <b>{synced_count} ta</b> yangi kitob bazaga qo'shildi.\nJami kitoblar: <b>{len(books_db)} ta</b>", parse_mode="HTML")
        
    except Exception as e:
        await msg.edit_text(f"❌ Xatolik yuz berdi: <code>{e}</code>\n\n<i>Eslatma: Bot @pdfbazam kanalida admin bo'lishi shart!</i>", parse_mode="HTML")

@dp.message(Command("id"))
async def get_book_by_id_command(message: types.Message):
    parts = message.text.split()
    if len(parts) < 2:
        await message.answer("⚠️ Iltimos, ID raqamini yozing. Masalan: <code>/id 1</code>", parse_mode="HTML")
        return
    
    try:
        book_id = int(parts[1])
    except ValueError:
        await message.answer("⚠️ ID raqam faqat sondan iborat bo'lishi kerak!")
        return
    
    book = next((b for b in books_db if b["id"] == book_id), None)
    if book:
        await bot.send_document(
            chat_id=message.chat.id,
            document=book["file_id"],
            caption=book["caption"]
        )
    else:
        await message.answer(f"❌ <b>{book_id}-ID</b> raqamli kitob topilmadi!", parse_mode="HTML")

@dp.message(Command("rename"))
async def rename_book_handler(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
    
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("⚠️ Xato format! Ishlatish: <code>/rename [ID] [Yangi nom]</code>", parse_mode="HTML")
        return
    
    try:
        book_id = int(parts[1])
        new_title = parts[2].strip()
    except ValueError:
        await message.answer("⚠️ ID raqam faqat sondan iborat bo'lishi kerak!")
        return
    
    book = next((b for b in books_db if b["id"] == book_id), None)
    if book:
        book["title"] = new_title
        book["keywords"] = generate_keywords(new_title)
        book["caption"] = f"📖 {new_title} (PDF)"
        save_json(BOOKS_FILE, books_db)
        await message.answer(f"✅ <b>{book_id}-ID</b> dagi kitob nomi o'zgartirildi:\n\n📚 <b>{new_title}</b>", parse_mode="HTML")
    else:
        await message.answer(f"❌ {book_id}-ID raqamli kitob topilmadi!")

@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id):
        await callback.message.delete()
        await callback.message.answer("Rahmat! Obuna tasdiqlandi. Endi izlamoqchi bo'lgan kitobingiz nomini yozib yuboring:")
    else:
        await callback.answer("❌ Siz hali guruhga a'zo bo'lmadingiz!", show_alert=True)

async def show_main_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Kitob qidirish", callback_data="search_book_prompt")
    text = "<b>Xush kelibsiz! ✨</b>\n\nKitob qidirish uchun quyidagi tugmani bosing yoki to'g'ridan-to'g'ri nomini yozib yuboring:"
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "search_book_prompt")
async def search_prompt(callback: types.CallbackQuery):
    await callback.message.answer("Marhamat, izlamoqchi bo'lgan kitobingiz nomini yozib yuboring:")
    await callback.answer()

@dp.callback_query(F.data.startswith("get_book_"))
async def send_selected_book(callback: types.CallbackQuery):
    book_id = int(callback.data.split("_")[2])
    book = next((b for b in books_db if b["id"] == book_id), None)
    
    if book:
        await bot.send_document(
            chat_id=callback.message.chat.id,
            document=book["file_id"],
            caption=book["caption"]
        )
        await callback.answer("Kitob yuborildi! 📂")
    else:
        await callback.answer("Kechirasiz, kitob topilmadi.", show_alert=True)

@dp.message(F.document)
async def handle_new_pdf(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        await message.answer("❌ Kechirasiz, bu botga faqat adminlar kitob qo'shishi mumkin.")
        return
    
    document = message.document
    if not document.file_name.lower().endswith(".pdf"):
        await message.answer("⚠️ Iltimos, faqat PDF formatidagi fayl tashlang!")
        return
    
    await state.update_data(file_id=document.file_id)
    await state.set_state(AdminBookState.waiting_for_caption)
    
    await message.answer(
        "✍️ <b>Ushbu kitobning nomini (sarlavhasini) yozib yuboring:</b>\n"
        "(Masalan: <i>Men — Fotih Duman</i>)",
        parse_mode="HTML"
    )

@dp.message(AdminBookState.waiting_for_caption, F.text)
async def save_book_with_caption(message: types.Message, state: FSMContext):
    book_title = message.text.strip()
    data = await state.get_data()
    file_id = data.get("file_id")
    
    try:
        sent_msg = await bot.send_document(
            chat_id=ARCHIVE_CHANNEL,
            document=file_id,
            caption=f"📖 {book_title} (PDF)"
        )
        file_id = sent_msg.document.file_id
    except Exception as e:
        logging.error(f"Kanalga yuborishda xatolik: {e}")
    
    new_id = max([b["id"] for b in books_db], default=0) + 1
    keywords = generate_keywords(book_title)
    
    new_book = {
        "id": new_id,
        "title": book_title,
        "keywords": keywords,
        "file_id": file_id,
        "caption": f"📖 {book_title} (PDF)"
    }
    
    books_db.append(new_book)
    save_json(BOOKS_FILE, books_db)
    
    await state.clear()
    
    await message.answer(
        f"✅ <b>Kitob muvaffaqiyatli saqlandi va @pdfbazam kanaliga tashlandi!</b>\n\n"
        f"📚 Nomi: <b>{book_title}</b>\n"
        f"🆔 ID raqami: <b>{new_id}</b>\n"
        f"📂 Jami kitoblar: <b>{len(books_db)} ta</b>",
        parse_mode="HTML"
    )

@dp.message(F.text)
async def search_book_handler(message: types.Message):
    user_id = message.from_user.id
    
    if str(user_id) not in users_db:
        users_db[str(user_id)] = {
            "name": message.from_user.full_name,
            "username": message.from_user.username
        }
        save_json(USERS_FILE, users_db)

    if not await check_subscription(user_id):
        await start_handler(message)
        return

    query = message.text.lower().strip()
    query_cyr = transliterate(query)
    
    matched_books = []
    for book in books_db:
        title_lower = book["title"].lower()
        title_cyr = transliterate(title_lower)
        
        if (query in title_lower or query_cyr in title_cyr or 
            any(query in kw or query_cyr in transliterate(kw) for kw in book["keywords"])):
            matched_books.append(book)
            
    if matched_books:
        response_text = f"🔍 <b>{len(matched_books)} ta natija topildi:</b>\n\n"
        builder = InlineKeyboardBuilder()
        
        display_books = matched_books[:35]
        for i, book in enumerate(display_books, 1):
            response_text += f"{i}. 📄 {book['title']} (ID: {book['id']})\n"
            builder.button(text=f"📥 {book['id']}-kitob: {book['title'][:25]}...", callback_data=f"get_book_{book['id']}")
            
        if len(matched_books) > 35:
            response_text += f"\n<i>⚠️ Qolgan {len(matched_books) - 35} ta natija ko'rsatilmadi.</i>"
            
        builder.adjust(1)
        await message.answer(response_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(
            "❌ Kechirasiz, bu nomdagi kitob topilmadi.\n\n"
            "Iltimos, nomini to'g'ri yozganingizni tekshiring yoki boshqa so'z bilan qidiring."
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
