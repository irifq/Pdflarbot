import asyncio
import json
import logging
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
HISTORY_FILE = "/app/data/history.json"

if not os.path.exists(BOOKS_FILE):
    with open(BOOKS_FILE, "w", encoding="utf-8") as f:
        json.dump([], f, ensure_ascii=False, indent=4)

if not os.path.exists(USERS_FILE):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

if not os.path.exists(HISTORY_FILE):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump({}, f, ensure_ascii=False, indent=4)

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

def transliterate(text: str) -> str:
    latin = ('sh', 'ch', 'g\'', 'o\'', 'ya', 'yu', 'ye', 'yo', 'a', 'b', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u', 'v', 'x', 'y', 'z')
    cyrillic = ('ш', 'ч', 'ғ', 'ў', 'я', 'ю', 'е', 'ё', 'а', 'б', 'д', 'э', 'ф', 'г', 'ҳ', 'и', 'ж', 'к', 'л', 'м', 'н', 'о', 'п', 'қ', 'р', 'с', 'т', 'у', 'в', 'х', 'й', 'з')
    text_lower = text.lower()
    for l, c in zip(latin, cyrillic):
        text_lower = text_lower.replace(l, c)
    return text_lower

def generate_keywords(title: str):
    raw_name = title.lower()
    words = [w for w in raw_name.replace("—", " ").replace("-", " ").split() if len(w) > 0]
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
    users_db = load_json(USERS_FILE, {})
    users_db[str(user_id)] = {
        "name": message.from_user.full_name,
        "username": message.from_user.username,
        "id": user_id
    }
    save_json(USERS_FILE, users_db)
    
    if not await check_subscription(user_id):
        builder = InlineKeyboardBuilder()
        builder.button(text="📢 Guruhga a'zo bo'lish", url=f"https://t.me/pdflar_muhokama")
        builder.button(text="✅ Obunani tekshirish", callback_data="check_sub")
        builder.adjust(1)
        text = (
            "<b>✨ Assalomu alaykum!</b>\n\n"
            "Botimizdan to'liq foydalanish uchun oldin quyidagi guruhimizga a'zo bo'ling:\n"
            f"👉 {CHANNEL_USERNAME}\n\n"
            "A'zo bo'lgach, pastdagi <b>«✅ Obunani tekshirish»</b> tugmasini bosing:"
        )
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await show_main_menu(message)

@dp.message(Command("users"))
async def users_list_handler(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
    
    users_db = load_json(USERS_FILE, {})
    if not users_db:
        await message.answer("👥 Hozircha foydalanuvchilar yo'q.")
        return

    text = "👥 <b>Foydalanuvchilar ro'yxati:</b>\n━━━━━━━━━━━━━━━━━━━━━\n\n"
    for i, (uid, udata) in enumerate(users_db.items(), 1):
        name = udata.get("name", "Noma'lum")
        uname = f"@{udata.get('username')}" if udata.get("username") else "Username yo'q"
        text += f"<b>{i}.</b> {name} ({uname}) — <code>ID: {uid}</code>\n"
        
        if len(text) > 3500:
            await message.answer(text, parse_mode="HTML")
            text = ""
            
    if text:
        await message.answer(text, parse_mode="HTML")

@dp.message(Command("view"))
async def view_user_history(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
        
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("⚠️ <b>Xato format!</b>\nIshlatish: <code>/view [raqam]</code> (Masalan: <code>/view 1</code>)", parse_mode="HTML")
        return
        
    index = int(parts[1]) - 1
    users_db = load_json(USERS_FILE, {})
    user_items = list(users_db.items())
    
    if index < 0 or index >= len(user_items):
        await message.answer("❌ Bunday raqamli foydalanuvchi topilmadi!")
        return
        
    uid, udata = user_items[index]
    history_db = load_json(HISTORY_FILE, {})
    user_queries = history_db.get(str(uid), [])
    
    name = udata.get("name", "Noma'lum")
    uname = f"@{udata.get('username')}" if udata.get("username") else "Yo'q"
    profile_link = f"<a href='tg://user?id={uid}'>{name} profili</a>"
    
    text = f"👤 <b>Foydalanuvchi #{index + 1}:</b> {name} ({uname})\n🆔 ID: <code>{uid}</code>\n🔗 Profil: {profile_link}\n\n💬 <b>Hamma yozganlari tarixi:</b>\n"
    
    if user_queries:
        for idx, q in enumerate(user_queries, 1):
            text += f"<b>{idx}.</b> {q}\n"
    else:
        text += "<i>Hozircha hech narsa yozmagan.</i>"
        
    if len(text) > 4000:
        for x in range(0, len(text), 4000):
            await message.answer(text[x:x+4000], parse_mode="HTML", disable_web_page_preview=True)
    else:
        await message.answer(text, parse_mode="HTML", disable_web_page_preview=True)

@dp.message(Command("text"))
async def send_text_to_user(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
        
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3 or not parts[1].isdigit():
        await message.answer("⚠️ <b>Xato format!</b>\nIshlatish: <code>/text [raqam] [xabar]</code>\nMasalan: <code>/text 1 Salom, kitobingiz tayyor!</code>", parse_mode="HTML")
        return
        
    index = int(parts[1]) - 1
    text_to_send = parts[2]
    
    users_db = load_json(USERS_FILE, {})
    user_items = list(users_db.items())
    
    if index < 0 or index >= len(user_items):
        await message.answer("❌ Bunday raqamli foydalanuvchi topilmadi!")
        return
        
    uid, udata = user_items[index]
    name = udata.get("name", "Foydalanuvchi")
    
    try:
        await bot.send_message(chat_id=int(uid), text=f"💬 <b>Admin xabari:</b>\n\n{text_to_send}", parse_mode="HTML")
        profile_link = f"<a href='tg://user?id={uid}'>{name} profili</a>"
        
        await message.answer(
            f"✅ <b>Xabar muvaffaqiyatli yuborildi!</b>\n\n"
            f"👤 Qabul qiluvchi: {name}\n"
            f"🔗 Profilga kirish: {profile_link}",
            parse_mode="HTML",
            disable_web_page_preview=True
        )
    except Exception as e:
        await message.answer(f"❌ Xabar yuborib bo'lmadi: {e}")

@dp.message(Command("delete"))
async def delete_book_handler(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
        
    parts = message.text.split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("⚠️ <b>Xato format!</b>\nIshlatish: <code>/delete [ID]</code> (Masalan: <code>/delete 5</code>)", parse_mode="HTML")
        return
        
    book_id = int(parts[1])
    books_db = load_json(BOOKS_FILE, [])
    
    initial_count = len(books_db)
    books_db = [b for b in books_db if b["id"] != book_id]
    
    if len(books_db) < initial_count:
        save_json(BOOKS_FILE, books_db)
        await message.answer(f"✅ <b>{book_id}-ID</b> raqamli kitob bazadan muvaffaqiyatli o'chirildi!", parse_mode="HTML")
    else:
        await message.answer(f"❌ <b>{book_id}-ID</b> raqamli kitob topilmadi!", parse_mode="HTML")

@dp.message(Command("backup"))
async def backup_handler(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
    try:
        if os.path.exists(BOOKS_FILE):
            await message.answer_document(
                document=types.FSInputFile(BOOKS_FILE),
                caption="📦 <b>Mana sizning bazangiz (`books.json`)!</b>\n\n📥 Bot: @Pdflarbot",
                parse_mode="HTML"
            )
        else:
            await message.answer("⚠️ Hozircha `books.json` fayli topilmadi.")
    except Exception as e:
        await message.answer(f"❌ Xatolik yuz berdi: {e}")

@dp.message(Command("stat"))
async def stat_handler(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
    users_db = load_json(USERS_FILE, {})
    books_db = load_json(BOOKS_FILE, [])
    
    stat_text = (
        "📊 <b>Bot Statistikasi:</b>\n\n"
        f"👥 Foydalanuvchilar: <b>{len(users_db)}</b> ta\n"
        f"📚 Kitoblar bazasi: <b>{len(books_db)}</b> ta\n\n"
        "📥 Bot: @Pdflarbot"
    )
    await message.answer(stat_text, parse_mode="HTML")

@dp.message(Command("rename"))
async def rename_book_handler(message: types.Message):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        return
    parts = message.text.split(maxsplit=2)
    if len(parts) < 3:
        await message.answer("⚠️ <b>Xato format!</b>\nIshlatish tartibi: <code>/rename [ID] [Yangi nom]</code>", parse_mode="HTML")
        return
    try:
        book_id = int(parts[1])
        new_title = parts[2].strip()
    except ValueError:
        await message.answer("⚠️ ID raqam faqat sondan iborat bo'lishi kerak!")
        return
    
    books_db = load_json(BOOKS_FILE, [])
    book = next((b for b in books_db if b["id"] == book_id), None)
    if book:
        book["title"] = new_title
        book["keywords"] = generate_keywords(new_title)
        book["caption"] = f"📖 <b>{new_title}</b>\n\n📥 Bot: @Pdflarbot"
        save_json(BOOKS_FILE, books_db)
        await message.answer(f"✅ <b>{book_id}-ID</b> dagi kitob nomi o'zgartirildi:\n\n📚 <b>{new_title}</b>", parse_mode="HTML")
    else:
        await message.answer(f"❌ {book_id}-ID raqamli kitob topilmadi!")

@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    if await check_subscription(user_id):
        try:
            await callback.message.delete()
        except Exception:
            pass
        await show_main_menu(callback.message)
    else:
        await callback.answer("❌ Siz hali guruhga a'zo bo'lmadingiz!", show_alert=True)

async def show_main_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="🔍 Kitob qidirishni boshlash", callback_data="search_book_prompt")
    text = (
        "<b>✨ Xush kelibsiz!</b>\n\n"
        "Kerakli kitobni topish uchun shunchaki nomini yoki ID raqamini yozib yuboring:"
    )
    if isinstance(message, types.CallbackQuery):
        await message.message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "search_book_prompt")
async def search_prompt(callback: types.CallbackQuery):
    await callback.message.answer("✍️ Marhamat, izlamoqchi bo'lgan kitobingiz nomini yoki ID raqamini yozib yuboring:")
    await callback.answer()

@dp.callback_query(F.data.startswith("get_book_"))
async def send_selected_book(callback: types.CallbackQuery):
    try:
        book_id = int(callback.data.split("_")[2])
    except Exception:
        await callback.answer("❌ Xatolik!", show_alert=True)
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
        await callback.answer("📂 Kitob yuborildi!")
    else:
        await callback.answer("❌ Kechirasiz, bu kitob topilmadi.", show_alert=True)

@dp.message(F.document)
async def handle_documents(message: types.Message, state: FSMContext):
    username = message.from_user.username
    if not username or username.lower() not in ADMIN_USERNAMES:
        await message.answer("❌ Kechirasiz, bu botga faqat adminlar fayl yuborishi mumkin.")
        return
        
    document = message.document
    file_name = document.file_name.lower()
    
    if file_name == "books.json":
        file_info = await bot.get_file(document.file_id)
        await bot.download(file_info, destination=BOOKS_FILE)
        books_db = load_json(BOOKS_FILE, [])
        await message.answer(f"✅ <b>Baza muvaffaqiyatli yangilandi!</b>\n\nJami kitoblar: <b>{len(books_db)} ta</b>", parse_mode="HTML")
        return
        
    if not file_name.endswith(".pdf"):
        await message.answer("⚠️ Iltimos, faqat PDF formatidagi fayl yoki <code>books.json</code> yuboring!", parse_mode="HTML")
        return
        
    books_db = load_json(BOOKS_FILE, [])
    existing_book = next((b for b in books_db if b["file_id"] == document.file_id), None)
    if existing_book:
        await message.answer(f"⚠️ <b>Bu PDF allaqachon bazada mavjud!</b>\n\nNomi: {existing_book['title']} (ID: {existing_book['id']})", parse_mode="HTML")
        return

    await state.update_data(file_id=document.file_id)
    await state.set_state(AdminBookState.waiting_for_caption)
    await message.answer("✍️ <b>Ushbu kitob uchun chiroyli nom (sarlavha) yozib yuboring:</b>", parse_mode="HTML")

@dp.message(AdminBookState.waiting_for_caption, F.text)
async def save_book_with_caption(message: types.Message, state: FSMContext):
    book_title = message.text.strip()
    data = await state.get_data()
    file_id = data.get("file_id")
    
    if not file_id:
        await message.answer("⚠️ Xatolik yuz berdi. Iltimos, PDF faylni qaytadan tashlang.")
        await state.clear()
        return

    books_db = load_json(BOOKS_FILE, [])
    
    if books_db:
        max_id = max([int(b.get("id", 0)) for b in books_db if str(b.get("id", 0)).isdigit()])
        new_id = max_id + 1
    else:
        new_id = 1

    keywords = generate_keywords(book_title)
    formatted_caption = f"📖 <b>{book_title}</b>\n\n📥 Bot: @Pdflarbot"
    
    new_book = {
        "id": new_id,
        "title": book_title,
        "keywords": keywords,
        "file_id": file_id,
        "caption": formatted_caption
    }
    books_db.append(new_book)
    save_json(BOOKS_FILE, books_db)
    await state.clear()
    
    success_text = (
        "✅ <b>Kitob bazaga qo'shildi!</b>\n\n"
        f"📚 Nomi: <b>{book_title}</b>\n"
        f"🆔 ID raqami: <b>{new_id}</b>\n"
        f"📊 Jami kitoblar: <b>{len(books_db)} ta</b>"
    )
    await message.answer(success_text, parse_mode="HTML")

@dp.message(F.text)
async def search_book_handler(message: types.Message):
    user_id = message.from_user.id
    username = message.from_user.username
    is_admin = username and username.lower() in ADMIN_USERNAMES

    users_db = load_json(USERS_FILE, {})
    users_db[str(user_id)] = {
        "name": message.from_user.full_name,
        "username": username,
        "id": user_id
    }
    save_json(USERS_FILE, users_db)

    user_text = message.text.strip()

    history_db = load_json(HISTORY_FILE, {})
    if str(user_id) not in history_db:
        history_db[str(user_id)] = []
    history_db[str(user_id)].append(user_text)
    save_json(HISTORY_FILE, history_db)

    if not await check_subscription(user_id):
        await start_handler(message)
        return
    
    
