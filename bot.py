import os
import logging
from telegram.ext import Updater, CommandHandler
from flask import Flask
from threading import Thread
import sqlite3
from datetime import datetime
import time

# Flask app for keep alive
app = Flask(__name__)

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Telegram User Info Bot</title>
    <meta charset="utf-8">
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f0f2f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; text-align: center; }
        .status { background: #27ae60; color: white; padding: 15px; border-radius: 8px; margin: 20px 0; text-align: center; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Telegram User Info Bot</h1>
        <div class="status">
            <strong>Bot is running successfully on Render!</strong>
        </div>
        <p><strong>Status:</strong> 🟢 Online</p>
        <p><strong>Host:</strong> Render.com</p>
        <p><strong>Uptime:</strong> 24/7</p>
        <p><strong>Start Time:</strong> %s</p>
    </div>
</body>
</html>
""" % datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

class TelegramBot:
    def __init__(self):
        self.start_time = datetime.now()
        self.setup_database()
    
    def setup_database(self):
        """Database setup"""
        self.conn = sqlite3.connect('user_info.db', check_same_thread=False)
        self.cursor = self.conn.cursor()
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                first_name TEXT,
                last_name TEXT,
                username TEXT,
                language_code TEXT,
                is_bot INTEGER,
                created_at TEXT
            )
        ''')
        self.conn.commit()
        print("✅ Database setup completed")
    
    def save_user(self, user):
        """Save user to database"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, first_name, last_name, username, language_code, is_bot, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user.id,
                user.first_name,
                user.last_name,
                user.username,
                user.language_code,
                1 if user.is_bot else 0,
                datetime.now().isoformat()
            ))
            self.conn.commit()
            print(f"✅ User saved: {user.first_name}")
        except Exception as e:
            print(f"❌ Error saving user: {e}")

    def start(self, update, context):
        """START COMMAND"""
        user = update.message.from_user
        self.save_user(user)
        
        welcome_text = f"""
🤖 **မြန်မာ User Info Bot** 

**မင်္ဂလာပါ {user.first_name or 'User'}!** 

ဒီ Bot ကနေ Telegram User တွေရဲ့ အချက်အလက်တွေကို လွယ်လွယ်ကူကူ ကြည့်ရှုနိုင်ပါတယ်။

**သုံးလို့ရတဲ့ Commands များ:**
/start - Bot ကိုစတင်အသုံးပြုရန်
/info - User အချက်အလက်များ ကြည့်ရှုရန်
/myid - ကိုယ့်ရဲ့ User ID ကြည့်ရှုရန်  
/chatid - Chat ID ကြည့်ရှုရန်
/help - အကူအညီရယူရန်

**Server Information:**
🚀 Hosted on: Render.com
⏰ Uptime: 24/7 Always Online
🔧 Status: Active

Bot ကိုအသုံးပြုပေးတဲ့အတွက် ကျေးဇူးတင်ပါတယ်!
        """
        
        update.message.reply_text(welcome_text, parse_mode='Markdown')
        print(f"✅ Start command executed for user: {user.first_name}")

    def help(self, update, context):
        """Help command"""
        help_text = """
🆘 **အကူအညီ စင်တာ**

**Commands List:**
/start - Bot ကိုစတင်အသုံးပြုရန်
/info - User အချက်အလက်များကြည့်ရှုရန်  
/myid - ကိုယ့်ရဲ့ User ID ကြည့်ရှုရန်
/chatid - Chat ID ကြည့်ရှုရန်
/help - ဒီအကူအညီစာမျက်နှာကြည့်ရှုရန်

**User Info ကြည့်နည်းများ:**
1. ကိုယ်တိုင် /info ရိုက်ပါ
2. သူများ message ကို reply လုပ်ပြီး /info ရိုက်ပါ

**Hosting Info:**
🤖 Bot is hosted on Render.com
⏰ 24/7 Always Online
        """
        update.message.reply_text(help_text, parse_mode='Markdown')

    def info(self, update, context):
        """Info command"""
        try:
            if update.message.reply_to_message:
                user = update.message.reply_to_message.from_user
            else:
                user = update.message.from_user
            
            self.save_user(user)
            
            info_text = f"""
👤 **User အချက်အလက်**

**အခြေခံ အချက်အလက်:**
🆔 **User ID:** `{user.id}`
📛 **နာမည်:** {user.first_name or "မရှိပါ"}
📛 **မျိုးရိုးနာမည်:** {user.last_name or "မရှိပါ"} 
👤 **Username:** @{user.username or "မရှိပါ"}
🌐 **ဘာသာစကား:** {user.language_code or "မရှိပါ"}
🤖 **Bot လား:** {"✅ ဟုတ်ပါတယ်" if user.is_bot else "❌ မဟုတ်ပါ"}

**Chat အချက်အလက်:**
💬 **Chat ID:** `{update.message.chat.id}`
🏷️ **Chat Type:** {update.message.chat.type}

**Server Info:**
🚀 **Host:** Render.com
⏰ **Status:** 24/7 Online
            """
            
            update.message.reply_text(info_text, parse_mode='Markdown')
            
        except Exception as e:
            error_msg = "❌ အချက်အလက်ရယူရာတွင် အမှားတစ်ခုဖြစ်နေပါသည်"
            update.message.reply_text(error_msg)
            print(f"Error in info command: {e}")

    def myid(self, update, context):
        """MyID command"""
        user = update.message.from_user
        self.save_user(user)
        update.message.reply_text(f"🆔 **မင်းရဲ့ User ID:** `{user.id}`", parse_mode='Markdown')

    def chatid(self, update, context):
        """ChatID command"""
        chat = update.message.chat
        update.message.reply_text(
            f"💬 **Chat ID:** `{chat.id}`\n"
            f"🏷️ **Chat Type:** {chat.type}", 
            parse_mode='Markdown'
        )

    def run(self):
        """Run the bot"""
        # Start keep-alive server
        keep_alive()
        
        # Get bot token from environment variable
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
        
        if not BOT_TOKEN:
            print("❌ ERROR: BOT_TOKEN environment variable မတွေ့ပါ")
            print("✅ Render dashboard မှာ Environment Variables ထည့်ပါ")
            return
        
        # Create updater with older style (compatible with python-telegram-bot 20.7)
        updater = Updater(token=BOT_TOKEN, use_context=True)
        dispatcher = updater.dispatcher
        
        # Add command handlers
        dispatcher.add_handler(CommandHandler("start", self.start))
        dispatcher.add_handler(CommandHandler("help", self.help))
        dispatcher.add_handler(CommandHandler("info", self.info))
        dispatcher.add_handler(CommandHandler("myid", self.myid))
        dispatcher.add_handler(CommandHandler("chatid", self.chatid))
        
        # Start the bot
        print("🤖 ====================================")
        print("🚀 Myanmar User Info Bot Starting...")
        print("📡 Host: Render.com")
        print("⏰ Uptime: 24/7 Always Online")
        print("🔧 Version: FINAL FIX")
        print("✅ Start Command: READY")
        print("✅ Bot Token: LOADED")
        print("✅ Database: INITIALIZED")
        print("🤖 ====================================")
        print("📍 Web Server: http://0.0.0.0:8080")
        print("⏰ Start Time:", self.start_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("🤖 ====================================")
        
        try:
            updater.start_polling()
            print("✅ Bot started polling successfully!")
            updater.idle()
        except Exception as e:
            print(f"❌ Bot stopped: {e}")
            print("🔄 Restarting in 10 seconds...")
            time.sleep(10)
            self.run()  # Restart

# Run the bot
if __name__ == '__main__':
    bot = TelegramBot()
    bot.run()
