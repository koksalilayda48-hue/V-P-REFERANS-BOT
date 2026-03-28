import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import sqlite3
import os

TOKEN = os.environ.get("BOT_TOKEN")
KANAL_LINK = "https://t.me/+z_FJxG6hk4MyNDk0"

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

# /start komutu
@bot.message_handler(commands=['start'])
def start(message):
    args = message.text.split()
    user_id = message.from_user.id

    # Kullanıcıyı ekle
    cursor.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    if not cursor.fetchone():
        ref_by = int(args[1]) if len(args) > 1 and args[1].isdigit() else None
        cursor.execute("INSERT INTO users (user_id, ref_by) VALUES (?,?)", (user_id, ref_by))
        conn.commit()

        # Referansı arttır
        if ref_by and ref_by != user_id:
            cursor.execute("UPDATE users SET refs = refs + 1 WHERE user_id=?", (ref_by,))
            conn.commit()

    # Butonlu menü
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("📊 Referansım", callback_data="ref"))
    markup.add(InlineKeyboardButton("🔗 Linkim", callback_data="link"))
    markup.add(InlineKeyboardButton("🎁 Ödüller", callback_data="odul"))
    markup.add(InlineKeyboardButton("📢 Kanal", url=KANAL_LINK))

    bot.send_message(user_id, "Hoş geldin! 🎯 Referans sistemine katıldın sıra sende üye davet et kazan", reply_markup=markup)

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
        bot.send_message(call.message.chat.id, f"Referans linkin:\n{link}")

    elif call.data == "odul":
        cursor.execute("SELECT refs FROM users WHERE user_id=?", (user_id,))
        refs = cursor.fetchone()[0]
        if refs >= 30:
            bot.send_message(call.message.chat.id, "💎 Tebrikler! Telegram Premium (MOD) kazandın yaz🇹🇷 @Weghrumi2")
        elif refs >= 20:
            bot.send_message(call.message.chat.id, "🎁 Tebrikler! KAZANDIRİO ✅️Kapak kazandın!yaz @Weghrumi2")
        elif refs >= 15:
            bot.send_message(call.message.chat.id, "🚫 Boş yok kapak kazandın! yaz @Weghrumi2")
        else:
            bot.send_message(call.message.chat.id, f"Referans sayın: {refs}. Ödül almak için daha çok kişi getir!")

bot.infinity_polling()
