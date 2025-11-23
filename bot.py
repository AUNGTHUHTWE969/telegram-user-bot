import os
from telegram.ext import Updater, CommandHandler
from flask import Flask
from threading import Thread

app = Flask(__name__)

@app.route('/')
def home():
    return "🤖 Bot is running on Render!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

def start(update, context):
    user = update.message.from_user
    update.message.reply_text(f"""
🤖 **မြန်မာ User Info Bot**

မင်္ဂလာပါ {user.first_name}!

**Commands:**
/start - Bot စသုံးရန်
/info - User info ကြည့်ရန်
/myid - User ID ကြည့်ရန်
/chatid - Chat ID ကြည့်ရန်

Hosted on Render.com
24/7 Online
    """, parse_mode='Markdown')

def info(update, context):
    user = update.message.from_user
    update.message.reply_text(f"""
👤 **User Info:**

🆔 **ID:** `{user.id}`
📛 **Name:** {user.first_name}
👤 **Username:** @{user.username or 'N/A'}
🤖 **Bot:** {'Yes' if user.is_bot else 'No'}
    """, parse_mode='Markdown')

def myid(update, context):
    user = update.message.from_user
    update.message.reply_text(f"🆔 **Your ID:** `{user.id}`", parse_mode='Markdown')

def chatid(update, context):
    chat = update.message.chat
    update.message.reply_text(f"💬 **Chat ID:** `{chat.id}`", parse_mode='Markdown')

def main():
    keep_alive()
    
    BOT_TOKEN = os.environ.get('BOT_TOKEN')
    if not BOT_TOKEN:
        print("❌ BOT_TOKEN not found")
        return
    
    updater = Updater(BOT_TOKEN, use_context=True)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("info", info))
    dp.add_handler(CommandHandler("myid", myid))
    dp.add_handler(CommandHandler("chatid", chatid))
    
    print("🚀 Bot starting successfully!")
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
