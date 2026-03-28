import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os

TOKEN = os.environ.get("BOT_TOKEN")
KANAL = "@z_FJxG6hk4MyNDk0"
GRUP = "@vipgrubum"

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

# /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    args = message.text.split()
    
    # Kanal kontrol
    try:
        kanal_durum = bot.get_chat_member(KANAL, user_id).status
    except:
        kanal_durum = None

    try:
        grup_durum = bot.get_chat_member(GRUP, user_id).status
    except:
        grup_durum = None

    if kanal_durum in ['left', 'kicked', None] or grup_durum in ['left', 'kicked', None]:
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("📢 Kanal", url=f"https://t.me/{KANAL[1:]}"))
        markup.add(InlineKeyboardButton("💬 Grup", url=f"https://t.me/{GRUP[1:]}"))
        bot.send_message(user_id, 
            "Önce aşağıdaki kanala ve gruba katılmalısın!", 
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

    # Butonlu menü
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Referansım", callback_data="ref"))
    markup.add(InlineKeyboardButton("🔗 Linkim", callback_data="link"))
    markup.add(InlineKeyboardButton("🎁 Ödüller", callback_data="odul"))
    markup.add(InlineKeyboardButton("📢 Kanal", url=f"https://t.me/{KANAL[1:]}"))
    markup.add(InlineKeyboardButton("💬 Grup", url=f"https://t.me/{GRUP[1:]}"))

    bot.send_message(user_id, "Hoş geldin! 🎯 Referans sistemine katıldın", reply_markup=markup)

# Butonlar
@bot.callback_query_handler(func=lambda call: True)
def callback(call):
    user_id = call.from_user.id
    if call.data == "ref":
        cursor.execute("SELECT refs FROM users WHERE user_id=?", (user_id,))
        refs = cursor.fetchone()[0]
        bot.answer_callback_query(call.id, f"Referans sayın: {refs}")

    elif call.data == "link":
        link = f"https://t.me/{bot.get_me().username}?start={user_id}"
        bot.send_message(call.message.chat.id, f"Referans linkin (kanal üzerinden):\n{link}")

    elif call.data == "odul":
        bot.send_message(call.message.chat.id, 
            "🎁 ÖDÜLLER TABLOSU 🎁\n\n"
            "15 Referans → Boş yok\n"
            "20 Referans → Kapak\n"
            "30 Referans → Telegram Premium APK")

bot.infinity_polling()
