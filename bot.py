import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os

# ---------------------- AYARLAR ----------------------
TOKEN = os.environ.get("BOT_TOKEN")  # Render Environment Variable
KANAL = "@bedavainternetorg"         # Katılım kontrol kanalı ve referans linki
GRUP = "@vipgrubum" # Katılım kontrol grubu
# ------------------------------------------------------

bot = telebot.TeleBot(TOKEN)

# Veritabanı
conn = sqlite3.connect("refbot.db", check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    ref_by INTEGER,
    refs INTEGER DEFAULT 0
)""")
conn.commit()

# ---------------------- ANA MENÜ ----------------------
def send_main_menu(user_id):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Referansım", callback_data="ref"))
    markup.add(InlineKeyboardButton("🔗 Linkim", callback_data="link"))
    markup.add(InlineKeyboardButton("🎁 Ödüller", callback_data="odul"))
    markup.add(InlineKeyboardButton("📢 Kanal", url=f"https://t.me/{KANAL[1:]}"))
    markup.add(InlineKeyboardButton("💬 Grup", url=f"https://t.me/{GRUP[1:]}"))
    bot.send_message(user_id, "🎯 Referans sistemine katıldın!", reply_markup=markup)

# ---------------------- /START ----------------------
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()

    # Katılım kontrolü
    try:
        kanal_durum = bot.get_chat_member(KANAL, user_id).status
    except:
        kanal_durum = None

    try:
        grup_durum = bot.get_chat_member(GRUP, user_id).status
    except:
        grup_durum = None

    if kanal_durum not in ['member', 'creator', 'administrator'] or grup_durum not in ['member', 'creator', 'administrator']:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Kanal", url=f"https://t.me/{KANAL[1:]}"))
        markup.add(InlineKeyboardButton("💬 Grup", url=f"https://t.me/{GRUP[1:]}"))
        markup.add(InlineKeyboardButton("✅ Katıldım", callback_data="katildim"))
        bot.send_message(user_id,
            "🖐️ Merhaba! Botu kullanmak için aşağıdaki kanal ve gruba katılmalısınız!\n\nKanal       Grup",
            reply_markup=markup)
        return

    # Kullanıcıyı ekle / referans arttır
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        ref_by = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        cursor.execute("INSERT INTO users (user_id, ref_by) VALUES (?,?)", (user_id, ref_by))
        conn.commit()

        if ref_by and ref_by != user_id:
            cursor.execute("UPDATE users SET refs = refs + 1 WHERE user_id=?", (ref_by,))
            conn.commit()

    send_main_menu(user_id)

# ---------------------- "Katıldım" Butonu ----------------------
@bot.callback_query_handler(func=lambda call: call.data == "katildim")
def check_membership(call):
    user_id = call.from_user.id

    try:
        kanal_durum = bot.get_chat_member(KANAL, user_id).status
    except:
        kanal_durum = None

    try:
        grup_durum = bot.get_chat_member(GRUP, user_id).status
    except:
        grup_durum = None

    if kanal_durum in ['member','creator','administrator'] and grup_durum in ['member','creator','administrator']:
        bot.answer_callback_query(call.id, "✅ Katılım doğrulandı! Referans sistemi aktif.")
        start(call.message)  # Ana menüyü gönder
    else:
        bot.answer_callback_query(call.id, "❌ Önce kanal ve gruba katılmalısın.")

# ---------------------- Buton İşlemleri ----------------------
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    if call.data == "ref":
        cursor.execute("SELECT refs FROM users WHERE user_id=?", (user_id,))
        refs = cursor.fetchone()
        refs = refs[0] if refs else 0
        bot.answer_callback_query(call.id, f"Referans sayın: {refs}")

    elif call.data == "link":
        # Sabit referans linki senin kanal üzerinden
        link = f"https://t.me/bedavainternetorg?start={user_id}"
        bot.send_message(call.message.chat.id,
            f"🔗 Referans linkin (kanal üzerinden):\n{link}")

    elif call.data == "odul":
        bot.send_message(call.message.chat.id,
            "🎁 ÖDÜLLER TABLOSU 🎁\n\n"
            "15 Referans → Boş yok\n"
            "20 Referans → Kapak\n"
            "30 Referans → Telegram Premium APK")

# ---------------------- BOTU ÇALIŞTIR ----------------------
bot.infinity_polling()
