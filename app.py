
from flask import Flask, request, redirect, url_for, session, render_template_string
from werkzeug.security import generate_password_hash, check_password_hash
import sqlite3
import random

app = Flask(__name__)
app.secret_key = "bilimdon_secret_key_2026"
DB = "bilimdon.db"


def connect_db():
    return sqlite3.connect(DB)


def init_db():
    with connect_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL
            )
        """)
        db.execute("""
            CREATE TABLE IF NOT EXISTS results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                grade INTEGER NOT NULL,
                subject TEXT NOT NULL,
                score INTEGER NOT NULL,
                total INTEGER NOT NULL
            )
        """)


SUBJECTS = {
    "Matematika": "math",
    "Ona tili": "uzbek",
    "O‘qish va adabiyot": "reading",
    "Ingliz tili": "english",
    "Tarix": "history",
    "Geografiya": "geography",
    "Informatika": "it",
    "Biologiya": "science",
    "Fizika": "science",
    "Kimyo": "science",
    "Tabiiy fanlar": "science"
}

GRADE_SUBJECTS = {
    1: ["Matematika", "Ona tili", "O‘qish va adabiyot",
        "Ingliz tili", "Tabiiy fanlar"],
    2: ["Matematika", "Ona tili", "O‘qish va adabiyot",
        "Ingliz tili", "Tabiiy fanlar"],
    3: ["Matematika", "Ona tili", "O‘qish va adabiyot",
        "Ingliz tili", "Tabiiy fanlar"],
    4: ["Matematika", "Ona tili", "O‘qish va adabiyot",
        "Ingliz tili", "Tabiiy fanlar"],
    5: ["Matematika", "Ona tili", "Adabiyot",
        "Ingliz tili", "Tarix", "Geografiya", "Informatika"],
    6: ["Matematika", "Ona tili", "Adabiyot",
        "Ingliz tili", "Tarix", "Geografiya", "Informatika"],
    7: ["Matematika", "Ona tili", "Adabiyot",
        "Ingliz tili", "Tarix", "Geografiya", "Biologiya",
        "Fizika", "Informatika"],
    8: ["Matematika", "Ona tili", "Adabiyot",
        "Ingliz tili", "Tarix", "Geografiya", "Biologiya",
        "Fizika", "Kimyo", "Informatika"],
    9: ["Matematika", "Ona tili", "Adabiyot",
        "Ingliz tili", "Tarix", "Geografiya", "Biologiya",
        "Fizika", "Kimyo", "Informatika"],
    10: ["Matematika", "Ona tili", "Adabiyot",
         "Ingliz tili", "Tarix", "Geografiya", "Biologiya",
         "Fizika", "Kimyo", "Informatika"],
    11: ["Matematika", "Ona tili", "Adabiyot",
         "Ingliz tili", "Tarix", "Geografiya", "Biologiya",
         "Fizika", "Kimyo", "Informatika"]
}

LESSONS = {
    "Matematika": {
        "topic": "Sonlar va matematik amallar",
        "explanation": (
            "Matematika sonlar, shakllar, o‘lchovlar va ular orasidagi "
            "munosabatlarni o‘rganadi. Qo‘shish sonlarni birlashtiradi, "
            "ayirish esa farqni topishga yordam beradi. Ko‘paytirish "
            "bir xil sonlarni takroran qo‘shishning qulay usulidir. "
            "Yuqori sinflarda kasrlar, tenglamalar va funksiyalar ham o‘rganiladi."
        ),
        "example": "Masalan: 8 + 7 = 15. Agar x + 3 = 10 bo‘lsa, x = 7.",
        "task": "3 ta qalamga yana 4 ta qalam qo‘shildi. Jami nechta qalam bo‘ldi?"
    },
    "Ona tili": {
        "topic": "So‘z turkumlari va gap tuzilishi",
        "explanation": (
            "Ona tili fikrimizni to‘g‘ri va ravon ifodalashga yordam beradi. "
            "Ot shaxs, narsa yoki joy nomini bildiradi; sifat belgini, "
            "fe’l esa harakat yoki holatni bildiradi. Gap tugallangan fikrni "
            "ifodalaydi. Gap bosh harf bilan boshlanadi va tegishli tinish "
            "belgisi bilan yakunlanadi."
        ),
        "example": "«Aqlli bola kitob o‘qidi» gapida «bola» — ot, «aqlli» — sifat.",
        "task": "«Qushlar osmonda uchadi» gapidan fe’lni toping."
    },
    "O‘qish va adabiyot": {
        "topic": "Matnni tushunish va badiiy asar",
        "explanation": (
            "Matnni o‘qishda uning mavzusi, asosiy g‘oyasi va qahramonlariga "
            "e’tibor beriladi. Badiiy asarlar insoniylik, do‘stlik, mehnatsevarlik "
            "va halollik kabi fazilatlarni yoritishi mumkin. Asar mazmunini "
            "tushunish uchun voqealar ketma-ketligini aniqlash muhim."
        ),
        "example": "Hikoyadagi qahramonning qarorlari uning xarakterini ochib beradi.",
        "task": "O‘qigan hikoyangizning asosiy g‘oyasini bir jumlada yozing."
    },
    "Adabiyot": {
        "topic": "Badiiy asar va uning g‘oyasi",
        "explanation": (
            "Adabiyot she’r, hikoya, qissa va roman kabi janrlarni o‘rganadi. "
            "Asarning mavzusi unda nima haqida so‘z yuritilishini, g‘oyasi "
            "esa muallif qanday fikrni yetkazmoqchi ekanini ko‘rsatadi. "
            "Obrazlar va badiiy tasvir vositalari asarning ta’sirini kuchaytiradi."
        ),
        "example": "She’rda o‘xshatish va jonlantirish tasvirni ta’sirchan qiladi.",
        "task": "O‘zingiz bilgan bir asarning mavzusi va g‘oyasini yozing."
    },
    "Ingliz tili": {
        "topic": "Basic English grammar",
        "explanation": (
            "Ingliz tilida oddiy gap ko‘pincha ega va kesimdan tuziladi. "
            "Masalan, «I read a book» — «Men kitob o‘qiyman». "
            "Present Simple odatlar va muntazam bajariladigan ishlarni "
            "ifodalaydi. Yangi so‘zlarni gap ichida ishlatib o‘rganish foydali."
        ),
        "example": "I go to school every day. — Men har kuni maktabga boraman.",
        "task": "«Men kitob o‘qiyman» jumlasini ingliz tiliga tarjima qiling."
    },
    "Tarix": {
        "topic": "Tarixiy manbalar va o‘tmish",
        "explanation": (
            "Tarix insoniyatning o‘tmishi, davlatlar, jamiyatlar va "
            "muhim voqealarni o‘rganadi. Tarixchilar yozma manbalar, "
            "arxeologik topilmalar va boshqa dalillardan foydalanadilar. "
            "Tarixiy voqealarni sanalar bilan birga ularning sabablari "
            "va oqibatlarini tushunib o‘rganish kerak."
        ),
        "example": "Arxeologik qazishmalarda topilgan buyumlar qadimgi hayot haqida ma’lumot beradi.",
        "task": "Tarixiy manbaning ikkita turini yozing."
    },
    "Geografiya": {
        "topic": "Yer va uning tabiiy xususiyatlari",
        "explanation": (
            "Geografiya Yer yuzasi, tabiat, aholi va xo‘jalik faoliyatini "
            "o‘rganadi. Xaritalar joylarning o‘rnini aniqlashga yordam beradi. "
            "Ekvator Yer sharini Shimoliy va Janubiy yarimsharlarga ajratadi. "
            "Iqlim, relyef, suvlar va tabiiy resurslar geografiyaning muhim "
            "mavzularidir."
        ),
        "example": "Globus Yerning kichraytirilgan sharsimon modelidir.",
        "task": "Xarita va globusning bir-biridan farqini tushuntiring."
    },
    "Informatika": {
        "topic": "Kompyuter va algoritmlar",
        "explanation": (
            "Informatika axborot, kompyuterlar va algoritmlarni o‘rganadi. "
            "Algoritm — vazifani bajarish uchun ketma-ket berilgan aniq "
            "ko‘rsatmalar. Dasturlash tillari yordamida kompyuterga "
            "buyruqlar beriladi. Fayllarni tartibli saqlash va xavfsiz "
            "parollardan foydalanish ham muhim ko‘nikmalardir."
        ),
        "example": "Algoritm: sonni kiritish → uni 2 ga ko‘paytirish → natijani chiqarish.",
        "task": "Ertalab maktabga tayyorlanish uchun 4 bosqichli algoritm yozing."
    },
    "Biologiya": {
        "topic": "Tirik organizmlar",
        "explanation": (
            "Biologiya tirik organizmlar, ularning tuzilishi va hayot faoliyatini "
            "o‘rganadi. Hujayra tirik organizmlarning asosiy tuzilish birligidir. "
            "O‘simliklar fotosintez jarayonida yorug‘likdan foydalanib oziq "
            "moddalar hosil qiladi. Hayvonlar, o‘simliklar va mikroorganizmlar "
            "tabiatdagi muhim guruhlardir."
        ),
        "example": "O‘simlik ildizi suv va mineral moddalarni shimishga yordam beradi.",
        "task": "Tirik organizmlarga xos uchta belgini yozing."
    },
    "Fizika": {
        "topic": "Harakat, kuch va energiya",
        "explanation": (
            "Fizika tabiat hodisalari, harakat, kuch, energiya, issiqlik, "
            "yorug‘lik va elektrni o‘rganadi. Tezlik bosib o‘tilgan masofaning "
            "vaqtga nisbatidir. Kuch jismlarning harakatini yoki shaklini "
            "o‘zgartirishi mumkin. Fizik kattaliklar o‘lchov birliklari bilan "
            "ifodalanadi."
        ),
        "example": "Tezlik formulasi: v = s / t. Masofa 100 m, vaqt 20 s bo‘lsa, v = 5 m/s.",
        "task": "Masofa 60 metr, vaqt 10 soniya. Tezlikni hisoblang."
    },
    "Kimyo": {
        "topic": "Moddalar va ularning xossalari",
        "explanation": (
            "Kimyo moddalar, ularning tarkibi, xossalari va o‘zgarishlarini "
            "o‘rganadi. Moddalar atom va molekulalardan tashkil topishi mumkin. "
            "Kimyoviy element atom yadrosidagi protonlar soni bilan belgilanadi. "
            "Kimyoviy reaksiya jarayonida moddalar boshqa moddalarga aylanadi."
        ),
        "example": "Suvning kimyoviy formulasi H₂O.",
        "task": "Kundalik hayotda uchraydigan uchta moddani yozing."
    },
    "Tabiiy fanlar": {
        "topic": "Tabiat va atrof-muhit",
        "explanation": (
            "Tabiiy fanlar tirik tabiat, jonsiz tabiat, Yer va koinot haqidagi "
            "bilimlarni birlashtiradi. Suv, havo, tuproq va quyosh nuri hayot "
            "uchun muhim. Kuzatish, tajriba va taqqoslash orqali tabiat "
            "hodisalarini tushunish mumkin."
        ),
        "example": "Suv tabiatda qattiq, suyuq va gaz holatlarida uchraydi.",
        "task": "Suvning uchta holatiga misollar yozing."
    }
}


QUESTION_BANK = {
    "math": [
        ("7 + 5 nechaga teng?", ["10", "11", "12", "13"], 2),
        ("9 × 3 nechaga teng?", ["18", "27", "21", "24"], 1),
        ("20 − 8 nechaga teng?", ["10", "12", "14", "16"], 1),
        ("36 ÷ 6 nechaga teng?", ["5", "6", "7", "8"], 1),
        ("Kvadratning nechta tomoni bor?", ["3", "4", "5", "6"], 1),
        ("100 ning yarmi nechaga teng?", ["25", "40", "50", "60"], 2),
        ("1 metr necha santimetr?", ["10", "100", "1000", "50"], 1),
        ("5² nechaga teng?", ["10", "15", "20", "25"], 3),
        ("Uchburchakning nechta burchagi bor?", ["2", "3", "4", "5"], 1),
        ("12 + 18 nechaga teng?", ["28", "30", "32", "36"], 1)
    ],
    "uzbek": [
        ("Ot nimani bildiradi?", ["Harakatni", "Belgini", "Shaxs yoki narsa nomini", "Miqdorni"], 2),
        ("Fe’l nimani bildiradi?", ["Harakat yoki holatni", "Rangni", "Sonni", "Joy nomini"], 0),
        ("Gap qanday harf bilan boshlanadi?", ["Kichik", "Bosh", "Istalgan", "Raqam bilan"], 1),
        ("Qaysi biri sifat?", ["Yugurdi", "Kitob", "Chiroyli", "Beshta"], 2),
        ("Qaysi biri ot?", ["O‘qidi", "Daraxt", "Tez", "Yashil"], 1),
        ("So‘roq gap oxiriga nima qo‘yiladi?", ["Nuqta", "Vergul", "So‘roq belgisi", "Ikki nuqta"], 2),
        ("«Bolalar o‘ynadi» gapidagi fe’l qaysi?", ["Bolalar", "O‘ynadi", "Gap", "Qaysi"], 1),
        ("«Katta uy» birikmasida sifat qaysi?", ["Uy", "Katta", "Birikma", "Yo‘q"], 1),
        ("Ma’nosi bir-biriga yaqin so‘zlar nima deyiladi?", ["Antonim", "Sinonim", "Omonim", "Undov"], 1),
        ("Qaysi biri qarama-qarshi ma’noli juftlik?", ["Go‘zal-chiroyli", "Katta-ulkan", "Oq-qora", "Tez-chaqqon"], 2)
    ],
    "reading": [
        ("Ertakda ko‘pincha nima uchraydi?", ["Faqat formulalar", "Sehrli va xayoliy voqealar", "Xaritalar", "Hisob-kitoblar"], 1),
        ("Matnning asosiy g‘oyasi nimani bildiradi?", ["Harflar sonini", "Asosiy fikrni", "Sahifalar sonini", "Muallif yoshini"], 1),
        ("She’r satrlari ko‘pincha nima deb ataladi?", ["Band yoki misra", "Formula", "Jadval", "Xarita"], 0),
        ("Asar qahramoni kim?", ["Voqeada qatnashuvchi obraz", "Kitob muqovasi", "Nashriyot", "Sahifa raqami"], 0),
        ("Kitob o‘qish nimaga yordam beradi?", ["Bilimni oshirishga", "Faqat yugurishga", "Uyquni kamaytirishga", "Hech narsaga"], 0),
        ("Hikoyada voqealar nima orqali bayon qilinadi?", ["Matn orqali", "Faqat sonlar bilan", "Faqat xarita bilan", "Formulalar bilan"], 0),
        ("Maqol odatda qanday fikr beradi?", ["Hayotiy xulosa", "Matematik formula", "Manzil", "Harorat"], 0),
        ("Muallif kim?", ["Asarni yaratgan kishi", "O‘quvchi stoli", "Kitob javoni", "Qahramonning do‘sti bo‘lishi shart"], 0),
        ("Matnni tushunish uchun nima qilish kerak?", ["Faqat sarlavhani ko‘rish", "Diqqat bilan o‘qish", "Kitobni yopish", "Rasmlarni sanash"], 1),
        ("Kutubxonaning asosiy vazifasi nima?", ["Kitob va axborotdan foydalanish imkonini berish", "Ovqat tayyorlash", "Mashina tuzatish", "Sport o‘tkazish"], 0)
    ],
    "english": [
        ("What is the English word for «kitob»?", ["Pen", "Book", "Table", "Door"], 1),
        ("«Apple» so‘zining tarjimasi qaysi?", ["Olma", "Nok", "Uzum", "Shaftoli"], 0),
        ("Choose the correct phrase:", ["I am a student", "I is a student", "I are student", "I be student"], 0),
        ("What is the plural of «cat»?", ["Cates", "Cats", "Caties", "Cat"], 1),
        ("«Good morning» qachon ishlatiladi?", ["Ertalab", "Faqat tunda", "Xayrlashganda", "Kechirasiz deganda"], 0),
        ("What is the opposite of «big»?", ["Tall", "Small", "Long", "Wide"], 1),
        ("«Dog» nimani anglatadi?", ["Mushuk", "Qush", "It", "Ot"], 2),
        ("Choose the correct form: She ___ happy.", ["am", "are", "is", "be"], 2),
        ("What is the English word for «suv»?", ["Fire", "Water", "Earth", "Air"], 1),
        ("«Thank you» nimani anglatadi?", ["Salom", "Rahmat", "Xayr", "Iltimos"], 1)
    ],
    "history": [
        ("Tarix nimani o‘rganadi?", ["Faqat kelajakni", "Insoniyat o‘tmishini", "Faqat matematikani", "Faqat ob-havoni"], 1),
        ("Arxeolog nimani o‘rganadi?", ["Qadimgi topilmalarni", "Faqat yulduzlarni", "Musiqani", "Sportni"], 0),
        ("Tarixiy manba qaysi?", ["Qadimiy yozuv", "Plastik o‘yinchoqning o‘zi", "Bo‘sh daftar", "Hisob mashinasi"], 0),
        ("Amir Temur qaysi tarixiy shaxs?", ["Sarkarda va davlat arbobi", "Astronavt", "Kimyogar", "Dengizchi"], 0),
        ("O‘zbekiston mustaqilligi qachon e’lon qilingan?", ["1991-yil 1-sentabr", "1990-yil 1-yanvar", "2000-yil 1-sentabr", "1989-yil 8-dekabr"], 0),
        ("Tarixiy voqealarni o‘rganishda nima muhim?", ["Dalillar va manbalar", "Taxminni dalilsiz qabul qilish", "Faqat ranglar", "Faqat rasmlar"], 0),
        ("Qadimgi buyumlar qayerdan topilishi mumkin?", ["Arxeologik qazishmalardan", "Faqat do‘kondan", "Faqat maktabdan", "Faqat aeroportdan"], 0),
        ("Xronologiya nimani o‘rganadi?", ["Voqealarning vaqt tartibini", "O‘simlik rangini", "Matematik shakllarni", "Tovush balandligini"], 0),
        ("Muzeyda odatda nima saqlanadi?", ["Tarixiy va madaniy eksponatlar", "Faqat oziq-ovqat", "Faqat kiyim yuvish vositalari", "Faqat sport to‘plari"], 0),
        ("Tarixni bilish nimaga yordam beradi?", ["O‘tmishni tushunishga", "Faqat tez yugurishga", "Faqat rasm chizishga", "Ob-havoni boshqarishga"], 0)
    ],
    "geography": [
        ("Yerning modeli nima deb ataladi?", ["Globus", "Termometr", "Kompasning o‘zi", "Mikroskop"], 0),
        ("Yer yuzasining katta suv havzasi nima?", ["Okean", "Cho‘l", "Tog‘", "Vodiy"], 0),
        ("Kompas nimani aniqlashga yordam beradi?", ["Tomonlarni", "Haroratni", "Og‘irlikni", "Vaqtni"], 0),
        ("Ekvator Yerni qaysi yarimsharlarga ajratadi?", ["Sharqiy va G‘arbiy", "Shimoliy va Janubiy", "Quruqlik va suv", "Tog‘ va tekislik"], 1),
        ("O‘zbekiston poytaxti qaysi shahar?", ["Samarqand", "Buxoro", "Toshkent", "Xiva"], 2),
        ("Xarita nima?", ["Yer yuzasining kichraytirilgan tasviri", "Faqat surat", "O‘lchov asbobi", "Tirik organizm"], 0),
        ("Cho‘lga xos belgi qaysi?", ["Yog‘in ko‘p bo‘lishi shart", "Qurg‘oqchilik", "Doimiy muzlik", "Faqat o‘rmonlar"], 1),
        ("Daryo nima?", ["Tabiiy oqadigan suv oqimi", "Tog‘ cho‘qqisi", "Quruq tekislik", "Shamol turi"], 0),
        ("Ob-havo nimani anglatadi?", ["Atmosferaning muayyan vaqtdagi holatini", "Yerning yoshini", "Daryo uzunligini", "Tog‘ balandligini"], 0),
        ("Qaysi biri materik?", ["Afrika", "O‘rta yer dengizi", "Amudaryo", "Kaspiy dengizi"], 0)
    ],
    "it": [
        ("Kompyuterga ma’lumot kiritish qurilmasi qaysi?", ["Klaviatura", "Monitor", "Karnay", "Proyektor"], 0),
        ("Algoritm nima?", ["Amallar ketma-ketligi", "Faqat rasm", "Kompyuter ekrani", "Internet kabeli"], 0),
        ("Matn yozish uchun qaysi qurilmadan foydalaniladi?", ["Klaviatura", "Karnay", "Printer qog‘ozi", "Skaner oynasi"], 0),
        ("Internet nima?", ["O‘zaro ulangan tarmoqlar tizimi", "Faqat bitta kompyuter", "Elektr chirog‘i", "Matn muharriri"], 0),
        ("Kuchli parol qanday bo‘lishi kerak?", ["Faqat 12345", "Ismning o‘zi", "Turli belgilar aralashmasi", "Hamma bilan ulashiladigan"], 2),
        ("Fayl nima?", ["Saqlangan ma’lumot", "Faqat klaviatura", "Elektr rozetkasi", "Monitor oyog‘i"], 0),
        ("Python nima?", ["Dasturlash tili", "Printer turi", "Operatsion xotira", "Internet brauzeri"], 0),
        ("Kompyuter natijani qaysi qurilmada ko‘rsatadi?", ["Monitor", "Sichqoncha", "Klaviatura", "Mikrofon"], 0),
        ("Ma’lumotni uzoq muddat saqlash uchun nima kerak?", ["Saqlash qurilmasi", "Faqat mikrofon", "Karnay", "Veb-kamera"], 0),
        ("Shubhali havolaga duch kelsangiz nima qilish kerak?", ["Darhol ochish", "Parolni kiritish", "Tekshirmasdan yuklash", "Ochmasdan oldin ishonchliligini tekshirish"], 3)
    ],
    "science": [
        ("Suvning kimyoviy formulasi qaysi?", ["CO₂", "H₂O", "O₂", "NaCl"], 1),
        ("O‘simliklar fotosintez uchun nimadan foydalanadi?", ["Yorug‘likdan", "Faqat tovushdan", "Plastmassadan", "Temirdan"], 0),
        ("Inson nafas olish uchun qaysi gazdan foydalanadi?", ["Kislorod", "Geliy", "Vodorod", "Neon"], 0),
        ("Kuchning SI birligi qaysi?", ["Metr", "Nyuton", "Sekund", "Litr"], 1),
        ("Hujayra nima?", ["Tirik organizmning asosiy tuzilish birligi", "Tog‘ turi", "Kimyoviy idish", "Sayyora"], 0),
        ("Suvning muzlashi qanday o‘zgarish?", ["Fizik holat o‘zgarishi", "Yangi element paydo bo‘lishi", "Yonish", "Magnitlanish"], 0),
        ("Yerning tabiiy yo‘ldoshi nima?", ["Oy", "Mars", "Quyosh", "Venera"], 0),
        ("Atom yadrosida qaysi zarrachalar bo‘ladi?", ["Proton va neytron", "Faqat elektron", "Faqat foton", "Faqat molekula"], 0),
        ("Qon aylanish tizimining muhim a’zosi qaysi?", ["Yurak", "O‘pka sochi", "Tirnoq", "Soch"], 0),
        ("Tezlikni hisoblash formulasi qaysi?", ["v = s / t", "v = s + t", "v = t / s", "v = s × 0"], 0)
    ]
}


def get_bank(subject):
    key = SUBJECTS.get(subject, "reading")
    return QUESTION_BANK.get(key, QUESTION_BANK["reading"])


def page(title, body):
    return render_template_string("""
    <!doctype html>
    <html lang="uz">
    <head>
      <meta charset="utf-8">
      <meta name="viewport" content="width=device-width, initial-scale=1">
      <title>{{ title }} | Bilimdon</title>
      <style>
        * { box-sizing: border-box; }
        body {
          margin: 0; font-family: Arial, sans-serif; color: #202846;
          background: linear-gradient(135deg, #eef2ff, #f8faff);
        }
        header {
          background: #5146e5; color: white; padding: 18px 5%;
          display: flex; justify-content: space-between; align-items: center;
          gap: 12px; flex-wrap: wrap;
        }
        header a { color: white; text-decoration: none; margin-right: 12px; }
        main { max-width: 1000px; margin: 28px auto; padding: 0 16px; }
        .hero, .card, .lesson, .question, .result {
          background: white; border-radius: 18px; padding: 22px;
          margin-bottom: 18px; box-shadow: 0 6px 24px #25305b12;
        }
        .hero { background: linear-gradient(135deg,#5146e5,#8b5cf6); color:white; }
        .grid { display: grid; grid-template-columns: repeat(auto-fit,minmax(220px,1fr)); gap: 16px; }
        .card { border: 1px solid #e5e7eb; }
        .card h3 { margin-top: 0; }
        a.btn, button {
          display: inline-block; border: 0; border-radius: 10px;
          padding: 12px 16px; background: #5146e5; color: white;
          text-decoration: none; cursor: pointer; font-size: 15px;
        }
        .hero a.btn { background: white; color: #5146e5; }
        input, select {
          width: 100%; padding: 12px; margin: 8px 0 16px;
          border: 1px solid #ccd1e0; border-radius: 10px; font-size: 16px;
        }
        label { display: block; margin: 9px 0; }
        .muted { color: #65708a; }
        .correct { color: #14804a; font-weight: bold; }
        footer { text-align:center; color:#65708a; padding:24px; }
        @media(max-width:600px) {
          header { align-items:flex-start; }
          main { margin-top:18px; }
          .hero, .card, .lesson, .question, .result { padding:17px; }
        }
      </style>
    </head>
    <body>
      <header>
        <strong>📚 Bilimdon</strong>
        <nav>
          <a href="{{ url_for('home') }}">Bosh sahifa</a>
          {% if session.get('username') %}
            <a href="{{ url_for('results') }}">Natijalar</a>
            <a href="{{ url_for('logout') }}">Chiqish</a>
          {% else %}
            <a href="{{ url_for('login') }}">Kirish</a>
            <a href="{{ url_for('register') }}">Ro‘yxatdan o‘tish</a>
          {% endif %}
        </nav>
      </header>
      <main>{{ body|safe }}</main>
      <footer>Bilimdon — bilim sari bir qadam! ✨</footer>
    </body>
    </html>
    """, title=title, body=body)


@app.route("/")
def home():
    body = """
    <section class="hero">
      <h1>Bilimdon platformasiga xush kelibsiz! 🎓</h1>
      <p>1–11-sinflar uchun darslarni o‘rganing, testlarni ishlang
      va o‘z natijalaringizni kuzating.</p>
      <a class="btn" href="/classes">Sinfni tanlash →</a>
    </section>
    <section class="grid">
      <div class="card"><h3>📖 Darslar</h3><p>Mavzu, tushuntirish va misollar.</p></div>
      <div class="card"><h3>📝 Testlar</h3><p>Har bir testda 10 ta savol.</p></div>
      <div class="card"><h3>🏆 Natijalar</h3><p>Ballaringizni ko‘rib boring.</p></div>
    </section>
    """
    return page("Bosh sahifa", body)


@app.route("/register", methods=["GET", "POST"])
def register():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if len(username) < 3 or len(password) < 6:
            message = "Login kamida 3 ta, parol esa 6 ta belgidan iborat bo‘lsin."
        else:
            try:
                with connect_db() as db:
                    db.execute(
                        "INSERT INTO users(username,password) VALUES (?,?)",
                        (username, generate_password_hash(password))
                    )
                return redirect(url_for("login"))
            except sqlite3.IntegrityError:
                message = "Bu login band. Boshqasini tanlang."

    body = f"""
    <div class="card">
      <h1>Ro‘yxatdan o‘tish</h1>
      <p>{message}</p>
      <form method="post">
        <label>Login</label><input name="username" required minlength="3">
        <label>Parol</label><input type="password" name="password" required minlength="6">
        <button>Hisob yaratish</button>
      </form>
    </div>
    """
    return page("Ro‘yxatdan o‘tish", body)


@app.route("/login", methods=["GET", "POST"])
def login():
    message = ""
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        with connect_db() as db:
            user = db.execute(
                "SELECT password FROM users WHERE username=?", (username,)
            ).fetchone()
        if user and check_password_hash(user[0], password):
            session["username"] = username
            return redirect(url_for("classes"))
        message = "Login yoki parol noto‘g‘ri."

    body = f"""
    <div class="card">
      <h1>Tizimga kirish</h1><p>{message}</p>
      <form method="post">
        <label>Login</label><input name="username" required>
        <label>Parol</label><input type="password" name="password" required>
        <button>Kirish</button>
      </form>
    </div>
    """
    return page("Kirish", body)


@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("home"))


@app.route("/classes")
def classes():
    cards = "".join(
        f'<div class="card"><h3>🎒 {grade}-sinf</h3>'
        f'<p>Fanlarni tanlang va o‘rganishni boshlang.</p>'
        f'<a class="btn" href="/subjects/{grade}">Fanlarni ko‘rish</a></div>'
        for grade in range(1, 12)
    )
    return page("Sinflar", '<h1>Sinfingizni tanlang</h1><div class="grid">' + cards + '</div>')


@app.route("/subjects/<int:grade>")
def subjects(grade):
    if grade not in GRADE_SUBJECTS:
        return redirect(url_for("classes"))
    cards = "".join(
        f'<div class="card"><h3>📘 {subject}</h3>'
        f'<a class="btn" href="/lesson/{grade}/{subject}">Darsni o‘rganish</a> '
        f'<a class="btn" href="/quiz/{grade}/{subject}">Test ishlash</a></div>'
        for subject in GRADE_SUBJECTS[grade]
    )
    return page(f"{grade}-sinf fanlari",
                f'<h1>{grade}-sinf fanlari</h1><div class="grid">{cards}</div>')


@app.route("/lesson/<int:grade>/<path:subject>")
def lesson(grade, subject):
    if grade not in GRADE_SUBJECTS or subject not in GRADE_SUBJECTS[grade]:
        return redirect(url_for("classes"))

    info = LESSONS.get(subject, LESSONS["O‘qish va adabiyot"])
    body = f"""
    <div class="lesson">
      <p class="muted">{grade}-sinf • {subject}</p>
      <h1>{info['topic']}</h1>
      <h3>📖 Mavzu tushuntirishi</h3>
      <p>{info['explanation']}</p>
      <h3>💡 Misol</h3><p>{info['example']}</p>
      <h3>✏️ Mustaqil topshiriq</h3><p>{info['task']}</p>
      <a class="btn" href="/quiz/{grade}/{subject}">Testni boshlash →</a>
    </div>
    """
    return page(f"{subject} darsi", body)


@app.route("/quiz/<int:grade>/<path:subject>", methods=["GET", "POST"])
def quiz(grade, subject):
    if grade not in GRADE_SUBJECTS or subject not in GRADE_SUBJECTS[grade]:
        return redirect(url_for("classes"))

    bank = get_bank(subject)

    if request.method == "POST":
        score = 0
        review = []
        for i, (question, options, answer) in enumerate(bank):
            selected = request.form.get(f"q{i}")
            is_correct = selected is not None and int(selected) == answer
            if is_correct:
                score += 1
            review.append(
                f"<p>{i+1}. {question}<br>"
                f"<span class='{'correct' if is_correct else ''}'>"
                f"To‘g‘ri javob: {options[answer]}</span></p>"
            )

        if session.get("username"):
            with connect_db() as db:
                db.execute(
                    """INSERT INTO results(username,grade,subject,score,total)
                       VALUES (?,?,?,?,?)""",
                    (session["username"], grade, subject, score, len(bank))
                )

        percent = round(score / len(bank) * 100)
        body = f"""
        <div class="result">
          <h1>🏆 Test natijasi</h1>
          <h2>{score} / {len(bank)} ta to‘g‘ri javob</h2>
          <h2>{percent}%</h2>
          <p>{'Ajoyib natija!' if percent >= 80 else 'Yaxshi! Yana mashq qilib ko‘ring.'}</p>
          <hr><h3>Javoblarni tekshirish</h3>
          {''.join(review)}
          <a class="btn" href="/quiz/{grade}/{subject}">Qayta ishlash</a>
          <a class="btn" href="/subjects/{grade}">Fanlarga qaytish</a>
        </div>
        """
        return page("Test natijasi", body)

    questions = list(enumerate(bank))
    random.shuffle(questions)
    # Test har safar 10 ta savolni o‘z ichiga oladi.
    form = f'<h1>📝 {grade}-sinf — {subject} testi</h1>'
    form += '<p class="muted">10 ta savol. Har bir savolda bitta javobni tanlang.</p>'
    form += '<form method="post">'

    for i, (question, options, answer) in questions:
        form += f'<div class="question"><h3>{i+1}. {question}</h3>'
        for j, option in enumerate(options):
            form += (
                f'<label><input style="width:auto;margin:0 8px 0 0" '
                f'type="radio" name="q{i}" value="{j}" required> '
                f'{option}</label>'
            )
        form += '</div>'

    form += '<button type="submit">Natijani ko‘rish</button></form>'
    return page("Test", form)


@app.route("/results")
def results():
    if not session.get("username"):
        return redirect(url_for("login"))

    with connect_db() as db:
        rows = db.execute(
            """SELECT grade, subject, score, total
               FROM results WHERE username=? ORDER BY id DESC""",
            (session["username"],)
        ).fetchall()

    if not rows:
        body = '<div class="card"><h1>Natijalarim</h1><p>Hozircha test natijalari yo‘q.</p></div>'
    else:
        items = "".join(
            f'<div class="card"><h3>{grade}-sinf • {subject}</h3>'
            f'<p>Natija: {score}/{total} '
            f'({round(score / total * 100)}%)</p></div>'
            for grade, subject, score, total in rows
        )
        body = '<h1>🏆 Natijalarim</h1><div class="grid">' + items + '</div>'

    return page("Natijalarim", body)


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
