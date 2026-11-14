import asyncio
import logging
import json
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

TOKEN = "6711555669:AAEyZzSl_HX4qIJIkz7i0gc0g-HGmcoM8ps"
CHANNEL_USERNAME = "@pdflar_muhokama"
USERS_FILE = "users.json"

bot = Bot(token=TOKEN)
dp = Dispatcher()

# --- FOYDALANUVCHILAR BAZASINI BOSHQARISH FUNKSIYALARI ---
def load_users():
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_users(users_data):
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump(users_data, f, ensure_ascii=False, indent=4)
    except Exception as e:
        logging.error(f"Faylga saqlashda xatolik: {e}")

users_db = load_users()

# To'plangan barcha 55 ta kitob bazasi
BOOKS = [
    {
        "id": 1,
        "title": "Men — Fotih Duman, Bas qil ey nafs",
        "keywords": ["men", "fotih", "duman", "bas qil ey nafs", "bas qil"],
        "file_id": "BQACAgIAAxkBAAIHcWr4m1KBhT39ctmUykj8iwSok--uAAJ1MgACW214SfbO-jpLSTQ3PQQ",
        "caption": "📖 Men — Fotih Duman, Bas qil ey nafs (PDF)"
    },
    {
        "id": 2,
        "title": "Dor ostidagi odam — Amina Shenliko'g'li",
        "keywords": ["dor ostidagi odam", "amina", "shenliko'g'li", "дор остидаги одам", "амина"],
        "file_id": "BQACAgIAAxkBAAIHdWr4nAAB1ECmWhtNP4tLRk-6ldhI7QAC7BIAAlj24Urv24F3IketST0E",
        "caption": "📖 Dor ostidagi odam — Amina Shenliko'g'li (PDF)"
    },
    {
        "id": 3,
        "title": "Odam bo'lish qiyin — O'lmas Umarbekov",
        "keywords": ["o'lmas", "umarbekov", "odam bo'lish qiyin", "одам болиш кийин"],
        "file_id": "BQACAgIAAxkBAAIHeWr4nXeXAw5CzTS8YGHeubJCrs3iAAKhlwACVzdpSQXMEEZ6-M-NPQQ",
        "caption": "📖 Odam bo'lish qiyin — O'lmas Umarbekov (PDF)"
    },
    {
        "id": 4,
        "title": "Alvido bolalik — Tohir Malik",
        "keywords": ["alvido bolalik", "tohir malik", "alvido"],
        "file_id": "BQACAgIAAxkBAAIHfWr4nct3j5c5gFKU4pv4-GQQLj0kAAKjlwACVzdpScforY2gz5ntPQQ",
        "caption": "📖 Alvido bolalik — Tohir Malik (PDF)"
    },
    {
        "id": 5,
        "title": "1984 — Jorj Oruell",
        "keywords": ["1984", "jorj", "oruell", "george orwell"],
        "file_id": "BQACAgIAAxkBAAIHgWr4nh8tZtLXC1hO2FgupCWt-bcdAAKmlwACVzdpSZ-YlIiY7ndNPQQ",
        "caption": "📖 1984 — Jorj Oruell (PDF)"
    },
    {
        "id": 6,
        "title": "Ramazon kundaligi",
        "keywords": ["ramazon kundaligi", "ramazon"],
        "file_id": "BQACAgIAAxkBAAIHyWr4ovFecLmYPp3fYp-yWU99I-RFAAIiGAACEvupSc6ixijC_8CSPQQ",
        "caption": "📖 Ramazon kundaligi (PDF)"
    },
    {
        "id": 7,
        "title": "O'lik uydan maktublar",
        "keywords": ["olik uydan maktublar", "o'lik uydan maktublar"],
        "file_id": "BQACAgIAAxkBAAIHzWr4oxFFiTE_j80VkhJURHwbf_5bAALnZgACT99gSN1E1Yn_XiutPQQ",
        "caption": "📖 O'lik uydan maktublar (PDF)"
    },
    {
        "id": 8,
        "title": "Yashamoq sokinlik istar",
        "keywords": ["yashamoq sokinlik istar", "sokinlik istar"],
        "file_id": "BQACAgIAAxkBAAIH0Wr4ozJW3xhMndcQ2BXhB2h4fjB1AAJ5GwACyXS4SLQnuoHaECdhPQQ",
        "caption": "📖 Yashamoq sokinlik istar (PDF)"
    },
    {
        "id": 9,
        "title": "Mashaqqatli hayot soqmoqlari",
        "keywords": ["mashaqqatli hayot soqmoqlari", "mashaqqatli hayot"],
        "file_id": "BQACAgIAAxkBAAIH1Wr4o0U5-Kg17-DPDEHESv0cGLz0AAIkSQACJzeAS0nIfNMaUe5dPQQ",
        "caption": "📖 Mashaqqatli hayot soqmoqlari (PDF)"
    },
    {
        "id": 10,
        "title": "Kafansiz ko'milganlar",
        "keywords": ["kafansiz komilganlar", "kafansiz ko'milganlar"],
        "file_id": "BQACAgIAAxkBAAIH2Wr4o4iLDb66npG_eWyS6UeAYCRBAALuZQACv5gRS0neQd8nNr3MPQQ",
        "caption": "📖 Kafansiz ko'milganlar (PDF)"
    },
    {
        "id": 11,
        "title": "O'lsam kim yig'laydi",
        "keywords": ["olsam kim yiglaydi", "o'lsam kim yig'laydi"],
        "file_id": "BQACAgIAAxkBAAIH3Wr4o61rPu4TBGQ5y6AveZkqbLtdAAJOYgAC5KPpSoS_iQ_HDckpPQQ",
        "caption": "📖 O'lsam kim yig'laydi (PDF)"
    },
    {
        "id": 12,
        "title": "Liderlar kitobi",
        "keywords": ["liderlar kitobi", "лидерлар китоби", "liderlar"],
        "file_id": "BQACAgIAAxkBAAIH4Wr4o-OkrHx2hZtAsNG92aHtv5lnAAL4YwACF6_5S19BjlJEDrqVPQQ",
        "caption": "📖 Liderlar kitobi (PDF)"
    },
    {
        "id": 13,
        "title": "Muvaffaqiyat siri",
        "keywords": ["muvaffaqiyat siri", "муваффакият сири", "muvaffaqiyat"],
        "file_id": "BQACAgIAAxkBAAIH5Wr4pBsN5jFbbVQGd7GACUe3vjLJAALwAQACFtyoSLzGW5xy-HhPPQQ",
        "caption": "📖 Muvaffaqiyat siri (PDF)"
    },
    {
        "id": 14,
        "title": "Iymon zaiflashuvi",
        "keywords": ["iymon zaiflashuvi", "иймон заифлашуви", "iymon"],
        "file_id": "BQACAgIAAxkBAAIH6Wr4pFRFNdr9pbGGyc8mZfK5nMZcAAKKGQACRMoZSt26VPtypr-hPQQ",
        "caption": "📖 Iymon zaiflashuvi (PDF)"
    },
    {
        "id": 15,
        "title": "Shahzoda va gado — Mark Tven",
        "keywords": ["shaxzoda va gado", "mark tven", "shahzoda"],
        "file_id": "BQACAgIAAxkBAAIH7Wr4pH6y30tjeNbwnzaakZNGnXBmAAKmFAACmHHgSmVtN1tyxGZePQQ",
        "caption": "📖 Shahzoda va gado — Mark Tven (PDF)"
    },
    {
        "id": 16,
        "title": "Kuchsizlar kuchi",
        "keywords": ["kuchsizlar kuchi", "kuchsizlar"],
        "file_id": "BQACAgQAAxkBAAIH8Wr4pKDOJOgf0adH3U6gCLj7bEkJAAL3CQACPXi4UM5i-TK5Ru5HPQQ",
        "caption": "📖 Kuchsizlar kuchi (PDF)"
    },
    {
        "id": 17,
        "title": "Til ofatlari",
        "keywords": ["til ofatlari", "тил офатлари", "til"],
        "file_id": "BQACAgQAAxkBAAIH9Wr4pMEO4gABO7RneFBMNbiopM7vMwAC9AgAAkMeuFNT0ODdbPz6NT0E",
        "caption": "📖 Til ofatlari (PDF)"
    },
    {
        "id": 18,
        "title": "Ta'sir psixologiyasi",
        "keywords": ["tasir psixologiyasi", "ta'sir psixologiyasi", "psixologiya"],
        "file_id": "BQACAgIAAxkBAAIH-Wr4pNvPlBP7tvOsDCe2-Ln2gI49AAJEDwACwoswSAw37gwTKp2ZPQQ",
        "caption": "📖 Ta'sir psixologiyasi (PDF)"
    },
    {
        "id": 19,
        "title": "Mahzun bo'lma — Oiz Qarniy",
        "keywords": ["maxzun bolma", "mahzun bo'lma", "oiz qarniy", "махзун болма"],
        "file_id": "BQACAgIAAxkBAAIH_Wr4pPTXJ27Bikqk5bPy1lEuMeGpAALlGAACeRCwSRcylLybOCpIPQQ",
        "caption": "📖 Mahzun bo'lma — Oiz Qarniy (PDF)"
    },
    {
        "id": 20,
        "title": "Oishada roziyallohu anhu",
        "keywords": ["oishar roziyallohu anhu", "oisha", "onamiz"],
        "file_id": "BQACAgIAAxkBAAIIAWr4pSSQ3da5HOJKV7oibimP9CLBAAI9AwACCxiRSAONQPBmf_x5PQQ",
        "caption": "📖 Oishada roziyallohu anhu (PDF)"
    },
    {
        "id": 21,
        "title": "Dangasalikni yengish",
        "keywords": ["dangasalikni yengish", "дангасаликни енгиш", "dangasalik"],
        "file_id": "BQACAgIAAxkBAAIIBWr4pUXCYgPzllqysH7zYnx_U48yAAJaCAACQjvQSBd0omDL-sSxPQQ",
        "caption": "📖 Dangasalikni yengish (PDF)"
    },
    {
        "id": 22,
        "title": "Aso, 1 — Fotih Duman",
        "keywords": ["aso 1", "fotih duman", "асо 1", "фотих думан"],
        "file_id": "BQACAgIAAxkBAAIICWr4pZrlgcybxe3WiFxcM3Emrz0pAAJ0aAACeBpwSotxPZlv5KJpPQQ",
        "caption": "📖 Aso, 1 — Fotih Duman (PDF)"
    },
    {
        "id": 23,
        "title": "Aso, 2 — Fotih Duman",
        "keywords": ["aso 2", "fotih duman", "асо 2", "фотих думан"],
        "file_id": "BQACAgIAAxkBAAIIDWr4pdBHm9U7bAUokdB0YoYJdWUPAAKSWQACnRJ5SvHJfxxI7Ox6PQQ",
        "caption": "📖 Aso, 2 — Fotih Duman (PDF)"
    },
    {
        "id": 24,
        "title": "Aso, 3 — Fotih Duman",
        "keywords": ["aso 3", "fotih duman", "асо 3", "фотих думан"],
        "file_id": "BQACAgIAAxkBAAIIEWr4pd05xgRG-4EJoQeKU0_wg4VIAALnYwADIgABS6I0G-CO0WjVPQQ",
        "caption": "📖 Aso, 3 — Fotih Duman (PDF)"
    },
    {
        "id": 25,
        "title": "Ikki eshik orasi",
        "keywords": ["ikki eshik orasi"],
        "file_id": "BQACAgIAAxkBAAIIFWr4pfmKI0pRVWmyqmxIxoT_WXiVAAI-CAACa75ASOgMG_karOxQPQQ",
        "caption": "📖 Ikki eshik orasi (PDF)"
    },
    {
        "id": 26,
        "title": "Hayrlisi",
        "keywords": ["hayrlisi", "хайрлиси"],
        "file_id": "BQACAgIAAxkBAAIIGWr4pgsAAYrNbCRvCJSFKoAeLX3mwAACrDgAAr8YOUtG4caO92d8Zz0E",
        "caption": "📖 Hayrlisi (PDF)"
    },
    {
        "id": 27,
        "title": "O'gay ona — Ahmad Lutfiy",
        "keywords": ["ogay ona", "o'gay ona", "ahmad lutfiy", "огай она"],
        "file_id": "BQACAgIAAxkBAAIIHWr4pip2xJoCCV4QdSzJPOoX7LnoAAI4AgACzpyASPrT8iY5lQABZj0E",
        "caption": "📖 O'gay ona — Ahmad Lutfiy (PDF)"
    },
    {
        "id": 28,
        "title": "Bolalar uchun 40 hadis",
        "keywords": ["bolalar uchun 40 hadis", "40 hadis", "hadis"],
        "file_id": "BQACAgIAAxkBAAIIIWr4pk9nTecX7bDv6VPy0KITeLTtAALXWQACSl8xSeqMcmyih5rlPQQ",
        "caption": "📖 Bolalar uchun 40 hadis (PDF)"
    },
    {
        "id": 29,
        "title": "Odam bo'lish qiyin",
        "keywords": ["odam bo'lish qiyin", "одам болиш кийин"],
        "file_id": "BQACAgIAAxkBAAIIJWr4pnQuThgRHUCUtzbbQmuc4LRBAAKYDgACJiohSN5nyvyYHtyxPQQ",
        "caption": "📖 Odam bo'lish qiyin (PDF)"
    },
    {
        "id": 30,
        "title": "Notiqlik sanati",
        "keywords": ["notiqlik sanati", "нотиклик санати", "notiqlik"],
        "file_id": "BQACAgIAAxkBAAIIKWr4po8QQYJghKZlGIfeqpu67Nt0AAITCgADL9FJhYYo9t7nZzU9BA",
        "caption": "📖 Notiqlik sanati (PDF)"
    },
    {
        "id": 31,
        "title": "Mariya / Omina",
        "keywords": ["mariya", "omina", "мария"],
        "file_id": "BQACAgIAAxkBAAIILWr4prwyCN_i2iLEKb4aGL4bHpmtAAK5EQAChAJpSgXl1HqXNUvnPQQ",
        "caption": "📖 Mariya / Omina (PDF)"
    },
    {
        "id": 32,
        "title": "Alloh suygan bandalar",
        "keywords": ["alloh suygan bandalar", "alloh suygan"],
        "file_id": "BQACAgIAAxkBAAIIMWr4pvVuYNOcJXjY36I7UnHs5mSpAAIkPgACfqS5S8WYk80TDyRYPQQ",
        "caption": "📖 Alloh suygan bandalar (PDF)"
    },
    {
        "id": 33,
        "title": "To'ydan keyin ham muhabbat",
        "keywords": ["to'ydan keyin ham muhabbat", "to'y", "muhabbat"],
        "file_id": "BQACAgIAAxkBAAIINWr4pwpSaYyRX3wexFpoTbn4IRwFAAJKGQACyG7ZSIL17eg20U07PQQ",
        "caption": "📖 To'ydan keyin ham muhabbat (PDF)"
    },
    {
        "id": 34,
        "title": "Dunyodagi eng baxtli ayol — Oiz Qorniy",
        "keywords": ["dunyodagi eng baxtli ayol", "oiz qorniy"],
        "file_id": "BQACAgQAAxkBAAIIOWr4pzI5zPvve62zh8Lkqo0Zf1hTAAJuFwACXZpwUwwaJUdQCGLAPQQ",
        "caption": "📖 Dunyodagi eng baxtli ayol — Oiz Qorniy (PDF)"
    },
    {
        "id": 35,
        "title": "Zehn va xotira",
        "keywords": ["zehn", "xotira"],
        "file_id": "BQACAgIAAxkBAAIIP2r4p4inB69qLPzsOr3Uc1-Az9EAA70HAAKmSNhLkrPhJwpsvzU9BA",
        "caption": "📖 Zehn va xotira (PDF)"
    },
    {
        "id": 36,
        "title": "Halol luqma",
        "keywords": ["halol luqma", "halol"],
        "file_id": "BQACAgIAAxkBAAIIQ2r4p5_b61zjw-fv97aDXHVcReyvAAJ5IAAC1wOxSCk8XK-A-y1mPQQ",
        "caption": "📖 Halol luqma (PDF)"
    },
    {
        "id": 37,
        "title": "Musulmon qo'rg'oni",
        "keywords": ["musulmon qo'rg'oni", "мусулмон кургони", "musulmon"],
        "file_id": "BQACAgQAAxkBAAIIR2r4p7T4jL1LnsOJ4yHrSO7cTgXAAAL-CQACQPy4UL7FwMA9QD-yPQQ",
        "caption": "📖 Musulmon qo'rg'oni (PDF)"
    },
    {
        "id": 38,
        "title": "Gunohning rangi",
        "keywords": ["gunohning rangi", "gunoh"],
        "file_id": "BQACAgIAAxkBAAIITGr4p972kFvIIRUV3AUVVfxJn2elAAKnOgACWMvYSEi_X5-gqGXUPQQ",
        "caption": "📖 Gunohning rangi (PDF)"
    },
    {
        "id": 39,
        "title": "Iymon va huzun",
        "keywords": ["iymon va huzun", "iymon", "huzun"],
        "file_id": "BQACAgIAAxkBAAIIUGr4qAHhrMlsBZjq6rtOjAABPqwmkAAC2zoAApRsiEviu-OxRWM3UD0E",
        "caption": "📖 Iymon va huzun (PDF)"
    },
    {
        "id": 40,
        "title": "Yolvoraman xiyonat qilma — Amina",
        "keywords": ["yolvoraman xiyonat qilma", "amina", "амина", "้นлвораман хийонат килма"],
        "file_id": "BQACAgIAAxkBAAIIVGr4qBoXylyPMIPRZkp6g2hlP_n4AAIJIAACmoOoSDa2FEzeEyOhPQQ",
        "caption": "📖 Yolvoraman xiyonat qilma — Amina (PDF)"
    },
    {
        "id": 41,
        "title": "Muhabbat masofasi",
        "keywords": ["muhabbat masofasi", "мухаббат масофаси"],
        "file_id": "BQACAgIAAxkBAAIIWmr4qIs0JycJb3v2a63VQIiAcUeqAALfDQACKb1pS50R3M0bwHcwPQQ",
        "caption": "📖 Muhabbat masofasi (PDF)"
    },
    {
        "id": 42,
        "title": "Allohga bo'lgan sevgim",
        "keywords": ["allohga bolgan sevgim", "allohga bo'lgan sevgim"],
        "file_id": "BQACAgIAAxkBAAIIXmr4qLFjYiFElrchLvNmLYKOa1icAAKFFQACB45YS88b27NZ6PYhPQQ",
        "caption": "📖 Allohga bo'lgan sevgim (PDF)"
    },
    {
        "id": 43,
        "title": "Yo nasib",
        "keywords": ["yo nasib", "nasib"],
        "file_id": "BQACAgIAAxkBAAIIYmr4qNXDQQZWiZde2AaYBvXSPC9eAAI-NwACLiaYSsRHhrN-0N4RPQQ",
        "caption": "📖 Yo nasib (PDF)"
    },
    {
        "id": 44,
        "title": "Yosh qizning kundaligi",
        "keywords": ["yosh qizning kundaligi", "yosh qiz"],
        "file_id": "BQACAgIAAxkBAAIIZmr4qODTilxrQ-KWnf0pCMNQ-Nf0AAI3OQAC8p8pSbIakpGKPLRwPQQ",
        "caption": "📖 Yosh qizning kundaligi (PDF)"
    },
    {
        "id": 45,
        "title": "Bu ummatning qizi",
        "keywords": ["bu ummatning qizi", "бу умматнинг кизи", "ummat"],
        "file_id": "BQACAgIAAxkBAAIIamr4qPOG7_7DoV_VlRYQkpxJiEBcAAKZFAACoDHhS9oeoEIaDKRaPQQ",
        "caption": "📖 Bu ummatning qizi (PDF)"
    },
    {
        "id": 46,
        "title": "Kelmasang ham kutaman",
        "keywords": ["kelmasang ham kutaman", "келмасанг хам кутаман"],
        "file_id": "BQACAgIAAxkBAAIIbmr4qRUw9w0MFgbdOsihTOQX9yn5AAInEwACKvpBSWLifvPkfJMTPQQ",
        "caption": "📖 Kelmasang ham kutaman (PDF)"
    },
    {
        "id": 47,
        "title": "Tanishishni unutibmiz",
        "keywords": ["tanishishni unutibmiz"],
        "file_id": "BQACAgIAAxkBAAIIcmr4qT-UgkYblq9sXX7NZDSSmM6eAAKiPgACs1WAS8XYo0pJmD9FPQQ",
        "caption": "📖 Tanishishni unutibmiz (PDF)"
    },
    {
        "id": 48,
        "title": "Alfido, 1",
        "keywords": ["alfido 1", "алфидо 1"],
        "file_id": "BQACAgQAAxkBAAIIdmr4qWBelkefBJXKzlriSSR-Np-SAAJcCgACnhTAU-HqZKkcA9S6PQQ",
        "caption": "📖 Alfido, 1 (PDF)"
    },
    {
        "id": 49,
        "title": "Alfido, 2",
        "keywords": ["alfido 2", "алфидо 2"],
        "file_id": "BQACAgQAAxkBAAIIemr4qXT3usICqBh3nDLezfkkEAGRAAJeCgACnhTAUxfHAfQIxw4wPQQ",
        "caption": "📖 Alfido, 2 (PDF)"
    },
    {
        "id": 50,
        "title": "Oila saodat maskani",
        "keywords": ["oila saodat maskani", "oila"],
        "file_id": "BQACAgIAAxkBAAIIfmr4qZWPGE5i5Di9d5qB4Zk51kVvAAJ6SQACwsVwS-AcGpodrTmEPQQ",
        "caption": "📖 Oila saodat maskani (PDF)"
    },
    {
        "id": 51,
        "title": "Jannatga taklifnoma",
        "keywords": ["jannatga taklifnoma", "jannatga"],
        "file_id": "BQACAgIAAxkBAAIHTmr4mHly51ioz-x1PtvQXwlPxOZZAAIyGQACFrlxSSlOTvqx6-iaPQQ",
        "caption": "📖 Jannatga taklifnoma (PDF)"
    },
    {
        "id": 52,
        "title": "Bugun bomdod o'qidingizmi",
        "keywords": ["bugun bomdod oqidingizmi", "bomdod"],
        "file_id": "BQACAgIAAxkBAAIHTWr4mHkAAV4CvGZ7d0887CgPfFhkDQACp0MAAoSb2EiDXBLCQudLiT0E",
        "caption": "📖 Bugun bomdod o'qidingizmi (PDF)"
    },
    {
        "id": 53,
        "title": "Dengiz haqida so'zlab ber menga",
        "keywords": ["dengiz haqida sozlab ber menga", "dengiz"],
        "file_id": "BQACAgIAAxkBAAIHY2r4mQ4P7MPR3hbs9ApjWt0KCMdWAAImKwACA0ghSml5BExp8XBMPQQ",
        "caption": "📖 Dengiz haqida so'zlab ber menga (PDF)"
    },
    {
        "id": 54,
        "title": "Izlash — Mehmet Yildiz",
        "keywords": ["izlash", "mehmet yildiz"],
        "file_id": "BQACAgIAAxkBAAIjmr4qiCbugEecln1trLdNnSa7OPDAAJhGwACNUdpSQiQNokqd1yyPQQ",
        "caption": "📖 Izlash — Mehmet Yildiz (PDF)"
    },
    {
        "id": 55,
        "title": "Jannat vasfi",
        "keywords": ["jannat vasfi", "jannat"],
        "file_id": "BQACAgUAAxkBAAIIkmr4qj5TlrELF67Csi3ixjuu9YNiAAIdBQAC7YqxVWnlVs1kZhFaPQQ",
        "caption": "📖 Jannat vasfi (PDF)"
    },
]

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
    save_users(users_db)
    
    is_subbed = await check_subscription(user_id)
    
    if not is_subbed:
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
    total_users = len(users_db)
    await message.answer(f"📊 <b>Bot foydalanuvchilari statistikasi:</b>\n\nJami obunachilar: <b>{total_users}</b> ta", parse_mode="HTML")

@dp.callback_query(F.data == "check_sub")
async def process_check_sub(callback: types.CallbackQuery):
    user_id = callback.from_user.id
    is_subbed = await check_subscription(user_id)
    
    if is_subbed:
        await callback.message.delete()
        await callback.message.answer("Rahmat! Obuna tasdiqlandi. Endi izlamoqchi bo'lgan kitobingiz nomini yozib yuboring:")
    else:
        await callback.answer("❌ Siz hali guruhga a'zo bo'lmadingiz!", show_alert=True)

async def show_main_menu(message: types.Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📚 Kitob qidirish", callback_data="search_book_prompt")
    
    text = (
        "<b>Xush kelibsiz! ✨</b>\n\n"
        "Kitob qidirish uchun quyidagi tugmani bosing yoki to'g'ridan-to'g'ri kitob nomini yozib yuboring:"
    )
    await message.answer(text, reply_markup=builder.as_markup(), parse_mode="HTML")

@dp.callback_query(F.data == "search_book_prompt")
async def search_prompt(callback: types.CallbackQuery):
    await callback.message.answer("Marhamat, izlamoqchi bo'lgan kitobingiz nomini yozib yuboring:")
    await callback.answer()

@dp.callback_query(F.data.startswith("get_book_"))
async def send_selected_book(callback: types.CallbackQuery):
    book_id = int(callback.data.split("_")[2])
    book = next((b for b in BOOKS if b["id"] == book_id), None)
    
    if book:
        await bot.send_document(
            chat_id=callback.message.chat.id,
            document=book["file_id"],
            caption=book["caption"]
        )
        await callback.answer("Kitob yuborildi! 📂")
    else:
        await callback.answer("Kechirasiz, kitob topilmadi.", show_alert=True)

@dp.message(F.text)
async def search_book_handler(message: types.Message):
    user_id = message.from_user.id
    
    if str(user_id) not in users_db:
        users_db[str(user_id)] = {
            "name": message.from_user.full_name,
            "username": message.from_user.username
        }
        save_users(users_db)

    is_subbed = await check_subscription(user_id)
    if not is_subbed:
        await start_handler(message)
        return

    query = message.text.lower().strip()
    
    matched_books = []
    for book in BOOKS:
        if any(kw in query for kw in book["keywords"]) or query in book["title"].lower():
            matched_books.append(book)
            
    if matched_books:
        response_text = f"🔍 <b>{len(matched_books)} ta natija topildi:</b>\n\n"
        builder = InlineKeyboardBuilder()
        
        for i, book in enumerate(matched_books, 1):
            response_text += f"{i}. 📄 {book['title']}\n"
            builder.button(text=f"📥 {i}-kitobni olish", callback_data=f"get_book_{book['id']}")
            
        builder.adjust(1)
        await message.answer(response_text, reply_markup=builder.as_markup(), parse_mode="HTML")
    else:
        await message.answer(
            "❌ Kechirasiz, bu nomdagi kitob topilmadi.\n\n"
            "Botimiz yaqinda ochilgani tufayli kitoblar qo'shish ustida ishlayapmiz. Uzr! 🙏"
        )

async def main():
    logging.basicConfig(level=logging.INFO)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
