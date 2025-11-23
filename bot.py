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
        body { 
            font-family: Arial, sans-serif; 
            margin: 40px; 
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: #333;
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: white; 
            padding: 30px; 
            border-radius: 15px; 
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
        }
        h1 { 
            color: #2c3e50; 
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }
        .status { 
            background: #27ae60; 
            color: white; 
            padding: 15px; 
            border-radius: 8px; 
            margin: 20px 0; 
            text-align: center;
            font-size: 18px;
        }
        .info-box {
            background: #f8f9fa;
            padding: 20px;
            margin: 15px 0;
            border-radius: 8px;
            border-left: 4px solid #3498db;
        }
        .command-list {
            background: #e8f4fd;
            padding: 15px;
            border-radius: 8px;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Telegram User Info Bot</h1>
        
        <div class="status">
            <strong>Bot is running successfully on Render!</strong>
        </div>

        <div class="info-box">
            <h3>🚀 Start Command Ready</h3>
            <p>Telegram bot is now running 24/7 on Render.com</p>
            <p>Use <strong>/start</strong> command in Telegram to begin</p>
        </div>

        <div class="info-box">
            <h3>📋 Available Commands</h3>
            <div class="command-list">
                <p><strong>/start</strong> - Start the bot</p>
                <p><strong>/info</strong> - Get user information</p>
                <p><strong>/myid</strong> - Get your user ID</p>
                <p><strong>/chatid</strong> - Get chat ID</p>
                <p><strong>/help</strong> - Get help</p>
            </div>
        </div>

        <div class="info-box">
            <h3>🔧 Technical Information</h3>
            <p><strong>Host:</strong> Render.com</p>
            <p><strong>Python Version:</strong> 3.11</p>
            <p><strong>Uptime:</strong> 24/7 Always Online</p>
            <p><strong>Start Time:</strong> %s</p>
            <p><strong>Status:</strong> <span style="color: #27ae60;">● Running</span></p>
        </div>
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

print("🔧 Initializing Telegram Bot...")

class TelegramBot:
    def __init__(self):
        self.start_time = datetime.now()
        print("✅ Bot class initialized")
        self.setup_database()
    
    def setup_database(self):
        """Database setup"""
        try:
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
        except Exception as e:
            print(f"❌ Database setup error: {e}")

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
                getattr(user, 'language_code', None),
                1 if user.is_bot else 0,
                datetime.now().isoformat()
            ))
            self.conn.commit()
            print(f"✅ User saved: {user.first_name} (ID: {user.id})")
        except Exception as e:
            print(f"❌ Error saving user: {e}")

    def start_command(self, update, context):
        """START COMMAND - ဒါက အဓိက command"""
        user = update.message.from_user
        self.save_user(user)
        
        welcome_text = f"""
🤖 **မြန်မာ User Info Bot** 

**မင်္ဂလာပါ {user.first_name or 'User'}!** 

ကျွန်တော့် Bot ကို အသုံးပြုတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။ 
ဒီ Bot ကနေ Telegram User တွေရဲ့ အချက်အလက်တွေကို လွယ်လွယ်ကူကူ ကြည့်ရှုနိုင်ပါတယ်။

**သုံးလို့ရတဲ့ Commands များ:**
/start - Bot ကိုစတင်အသုံးပြုရန် (ဒီမက်ဆေ့)
/info - User အချက်အလက်များ ကြည့်ရှုရန်
/myid - ကိုယ့်ရဲ့ User ID ကြည့်ရှုရန်  
/chatid - Chat ID ကြည့်ရှုရန်
/help - အကူအညီရယူရန်

**အသုံးပြုနည်းများ:**
• ကိုယ့်အချက်အလက် ကြည့်ချင်ရင် /info ရိုက်ပါ
• သူများအချက်အလက် ကြည့်ချင်ရင် သူတို့ message ကို reply လုပ်ပြီး /info ရိုက်ပါ
• Group ထဲမှာ /chatid ရိုက်ပြီး Group ID ကြည့်လို့ရတယ်

**Server Information:**
🚀 Hosted on: Render.com
⏰ Uptime: 24/7 Always Online
🔧 Status: Active
📅 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}

ကျေးဇူးပြုပြီး Bot ကိုအသုံးပြုပေးတဲ့အတွက် ကျေးဇူးအထူးတင်ပါတယ်! 
        """
        
        update.message.reply_text(welcome_text, parse_mode='Markdown')
        print(f"✅ Start command executed for user: {user.first_name} (ID: {user.id})")

    def help_command(self, update, context):
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

**Support:**
ပြဿနာတစ်စုံတစ်ရာရှိပါက Bot Developer ဆီဆက်သွယ်ပါ။

**Hosting Info:**
🤖 Bot is hosted on Render.com
⏰ 24/7 Always Online
        """
        update.message.reply_text(help_text, parse_mode='Markdown')
        print("✅ Help command executed")

    def info_command(self, update, context):
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
🌐 **ဘာသာစကား:** {getattr(user, 'language_code', 'မရှိပါ')}
🤖 **Bot လား:** {"✅ ဟုတ်ပါတယ်" if user.is_bot else "❌ မဟုတ်ပါ"}

**Chat အချက်အလက်:**
💬 **Chat ID:** `{update.message.chat.id}`
🏷️ **Chat Type:** {update.message.chat.type}

**Server Info:**
🚀 **Host:** Render.com
⏰ **Status:** 24/7 Online
🔧 **Uptime:** {(datetime.now() - self.start_time).days} days
            """
            
            update.message.reply_text(info_text, parse_mode='Markdown')
            print(f"✅ Info command executed for user: {user.first_name}")
            
        except Exception as e:
            error_msg = "❌ အချက်အလက်ရယူရာတွင် အမှားတစ်ခုဖြစ်နေပါသည်"
            update.message.reply_text(error_msg)
            print(f"❌ Info command error: {e}")

    def myid_command(self, update, context):
        """MyID command"""
        user = update.message.from_user
        self.save_user(user)
        update.message.reply_text(f"🆔 **မင်းရဲ့ User ID:** `{user.id}`", parse_mode='Markdown')
        print(f"✅ MyID command executed for user: {user.first_name}")

    def chatid_command(self, update, context):
        """ChatID command"""
        chat = update.message.chat
        update.message.reply_text(
            f"💬 **Chat ID:** `{chat.id}`\n"
            f"🏷️ **Chat Type:** {chat.type}", 
            parse_mode='Markdown'
        )
        print(f"✅ ChatID command executed in chat: {chat.id}")

    def run_bot(self):
        """Run the bot"""
        print("🤖 Starting Telegram Bot...")
        
        # Start keep-alive server
        keep_alive()
        print("✅ Flask keep-alive server started")
        
        # Get bot token from environment variable
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
        
        if not BOT_TOKEN:
            print("❌ ERROR: BOT_TOKEN environment variable မတွေ့ပါ")
            print("✅ Render dashboard မှာ Environment Variables ထည့်ပါ")
            print("✅ Key: BOT_TOKEN")
            print("✅ Value: your_actual_bot_token")
            return
        
        print(f"✅ Bot Token loaded: {BOT_TOKEN[:10]}...")
        
        try:
            # Create updater
            updater = Updater(token=BOT_TOKEN, use_context=True)
            dispatcher = updater.dispatcher
            
            # Add command handlers
            dispatcher.add_handler(CommandHandler("start", self.start_command))
            dispatcher.add_handler(CommandHandler("help", self.help_command))
            dispatcher.add_handler(CommandHandler("info", self.info_command))
            dispatcher.add_handler(CommandHandler("myid", self.myid_command))
            dispatcher.add_handler(CommandHandler("chatid", self.chatid_command))
            
            # Start the bot
            print("🤖 ====================================")
            print("🚀 Myanmar User Info Bot Starting...")
            print("📡 Host: Render.com")
            print("⏰ Uptime: 24/7 Always Online")
            print("🔧 Version: 3.0 - FINAL FIX")
            print("✅ Start Command: READY")
            print("✅ Bot Token: LOADED")
            print("✅ Database: INITIALIZED")
            print("✅ Flask Server: RUNNING")
            print("🤖 ====================================")
            print("📍 Web Server: http://0.0.0.0:8080")
            print("⏰ Start Time:", self.start_time.strftime("%Y-%m-%d %H:%M:%S"))
            print("🤖 ====================================")
            
            updater.start_polling()
            print("✅ Bot started polling successfully!")
            print("🤖 Bot is now running and ready to receive commands!")
            
            # Keep the bot running
            updater.idle()
            
        except Exception as e:
            print(f"❌ Bot startup error: {e}")
            print("🔄 Restarting in 10 seconds...")
            time.sleep(10)
            self.run_bot()  # Restart

# Run the bot
if __name__ == '__main__':
    print("🔧 Script started...")
    bot = TelegramBot()
    bot.run_bot()
