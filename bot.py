import os
import logging
import requests
import json
import sqlite3
from datetime import datetime
from flask import Flask, request
from threading import Thread
import time

# Flask app
app = Flask(__name__)

# Bot configuration
BOT_TOKEN = os.environ.get('BOT_TOKEN')
if not BOT_TOKEN:
    print("❌ ERROR: BOT_TOKEN not found in environment variables")
    print("✅ Please add BOT_TOKEN to Render environment variables")
    exit(1)

TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"

print(f"✅ Bot Token: {BOT_TOKEN[:10]}...")
print("🚀 Starting Myanmar User Info Bot...")

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TelegramBot:
    def __init__(self):
        self.start_time = datetime.now()
        self.setup_database()
        self.setup_webhook()
    
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
            print(f"❌ Database error: {e}")

    def setup_webhook(self):
        """Setup webhook for Telegram"""
        try:
            # For polling method, we don't need webhook
            print("✅ Using polling method (no webhook needed)")
        except Exception as e:
            print(f"❌ Webhook setup error: {e}")

    def save_user(self, user_data):
        """Save user to database"""
        try:
            self.cursor.execute('''
                INSERT OR REPLACE INTO users 
                (user_id, first_name, last_name, username, language_code, is_bot, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                user_data.get('id'),
                user_data.get('first_name'),
                user_data.get('last_name'),
                user_data.get('username'),
                user_data.get('language_code'),
                1 if user_data.get('is_bot', False) else 0,
                datetime.now().isoformat()
            ))
            self.conn.commit()
            print(f"✅ User saved: {user_data.get('first_name')}")
        except Exception as e:
            print(f"❌ Error saving user: {e}")

    def send_message(self, chat_id, text, parse_mode=None):
        """Send message to Telegram"""
        try:
            url = f"{TELEGRAM_API_URL}/sendMessage"
            payload = {
                'chat_id': chat_id,
                'text': text,
                'parse_mode': parse_mode
            }
            response = requests.post(url, json=payload)
            return response.json()
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return None

    def process_start_command(self, chat_id, user_data):
        """Process /start command"""
        self.save_user(user_data)
        
        welcome_text = f"""
🤖 **မြန်မာ User Info Bot** 

**မင်္ဂလာပါ {user_data.get('first_name', 'User')}!** 

ကျွန်တော့် Bot ကို အသုံးပြုတဲ့အတွက် ကျေးဇူးတင်ပါတယ်။ 
ဒီ Bot ကနေ Telegram User တွေရဲ့ အချက်အလက်တွေကို လွယ်လွယ်ကူကူ ကြည့်ရှုနိုင်ပါတယ်။

**သုံးလို့ရတဲ့ Commands များ:**
/start - Bot ကိုစတင်အသုံးပြုရန် (ဒီမက်ဆေ့)
/info - User အချက်အလက်များ ကြည့်ရှုရန်
/myid - ကိုယ့်ရဲ့ User ID ကြည့်ရှုရန်  
/chatid - Chat ID ကြည့်ရှုရန်
/help - အကူအညီရယူရန်

**Server Information:**
🚀 Hosted on: Render.com
⏰ Uptime: 24/7 Always Online
🔧 Status: Active
📅 Started: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}

ကျေးဇူးပြုပြီး Bot ကိုအသုံးပြုပေးတဲ့အတွက် ကျေးဇူးအထူးတင်ပါတယ်! 
        """
        
        self.send_message(chat_id, welcome_text, parse_mode='Markdown')
        print(f"✅ Start command executed for user: {user_data.get('first_name')}")

    def process_help_command(self, chat_id):
        """Process /help command"""
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
        self.send_message(chat_id, help_text, parse_mode='Markdown')
        print("✅ Help command executed")

    def process_info_command(self, chat_id, user_data, message_data):
        """Process /info command"""
        try:
            # Check if this is a reply to another message
            reply_to_message = message_data.get('reply_to_message')
            if reply_to_message:
                user_data = reply_to_message.get('from', user_data)
            
            self.save_user(user_data)
            
            info_text = f"""
👤 **User အချက်အလက်**

**အခြေခံ အချက်အလက်:**
🆔 **User ID:** `{user_data.get('id')}`
📛 **နာမည်:** {user_data.get('first_name', 'မရှိပါ')}
📛 **မျိုးရိုးနာမည်:** {user_data.get('last_name', 'မရှိပါ')} 
👤 **Username:** @{user_data.get('username', 'မရှိပါ')}
🌐 **ဘာသာစကား:** {user_data.get('language_code', 'မရှိပါ')}
🤖 **Bot လား:** {"✅ ဟုတ်ပါတယ်" if user_data.get('is_bot', False) else "❌ မဟုတ်ပါ"}

**Chat အချက်အလက်:**
💬 **Chat ID:** `{chat_id}`

**Server Info:**
🚀 **Host:** Render.com
⏰ **Status:** 24/7 Online
🔧 **Uptime:** {(datetime.now() - self.start_time).days} days
            """
            
            self.send_message(chat_id, info_text, parse_mode='Markdown')
            print(f"✅ Info command executed for user: {user_data.get('first_name')}")
            
        except Exception as e:
            error_msg = "❌ အချက်အလက်ရယူရာတွင် အမှားတစ်ခုဖြစ်နေပါသည်"
            self.send_message(chat_id, error_msg)
            print(f"❌ Info command error: {e}")

    def process_myid_command(self, chat_id, user_data):
        """Process /myid command"""
        self.save_user(user_data)
        self.send_message(chat_id, f"🆔 **မင်းရဲ့ User ID:** `{user_data.get('id')}`", parse_mode='Markdown')
        print(f"✅ MyID command executed for user: {user_data.get('first_name')}")

    def process_chatid_command(self, chat_id):
        """Process /chatid command"""
        self.send_message(chat_id, f"💬 **Chat ID:** `{chat_id}`", parse_mode='Markdown')
        print(f"✅ ChatID command executed in chat: {chat_id}")

    def get_updates(self, offset=None):
        """Get new messages from Telegram"""
        try:
            url = f"{TELEGRAM_API_URL}/getUpdates"
            params = {'timeout': 30, 'offset': offset}
            response = requests.get(url, params=params, timeout=35)
            return response.json()
        except Exception as e:
            print(f"❌ Error getting updates: {e}")
            return None

    def process_updates(self):
        """Process incoming messages"""
        print("🔄 Checking for new messages...")
        last_update_id = None
        
        while True:
            try:
                updates = self.get_updates(last_update_id)
                
                if updates and updates.get('ok'):
                    for update in updates.get('result', []):
                        last_update_id = update['update_id'] + 1
                        
                        message = update.get('message') or update.get('edited_message')
                        if message:
                            self.handle_message(message)
                
                time.sleep(1)
                
            except Exception as e:
                print(f"❌ Error in process_updates: {e}")
                time.sleep(5)

    def handle_message(self, message):
        """Handle incoming message"""
        try:
            chat_id = message['chat']['id']
            text = message.get('text', '').strip()
            user_data = message.get('from', {})
            
            print(f"📨 Received message: {text} from {user_data.get('first_name')}")
            
            if text.startswith('/start'):
                self.process_start_command(chat_id, user_data)
            elif text.startswith('/help'):
                self.process_help_command(chat_id)
            elif text.startswith('/info'):
                self.process_info_command(chat_id, user_data, message)
            elif text.startswith('/myid'):
                self.process_myid_command(chat_id, user_data)
            elif text.startswith('/chatid'):
                self.process_chatid_command(chat_id)
            else:
                # Send help for unknown commands
                if text.startswith('/'):
                    self.send_message(chat_id, "❌ Unknown command. Use /help to see available commands.")
                    
        except Exception as e:
            print(f"❌ Error handling message: {e}")

    def run_bot(self):
        """Run the bot"""
        print("🤖 ====================================")
        print("🚀 Myanmar User Info Bot Starting...")
        print("📡 Host: Render.com")
        print("⏰ Uptime: 24/7 Always Online")
        print("🔧 Version: 4.0 - NO EXTERNAL LIBRARIES")
        print("✅ Start Command: READY")
        print("✅ Bot Token: LOADED")
        print("✅ Database: INITIALIZED")
        print("🤖 ====================================")
        print("📍 Web Server: http://0.0.0.0:8080")
        print("⏰ Start Time:", self.start_time.strftime("%Y-%m-%d %H:%M:%S"))
        print("🤖 ====================================")
        
        # Start processing updates
        self.process_updates()

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
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Telegram User Info Bot</h1>
        <div class="status">
            <strong>Bot is running successfully on Render!</strong>
        </div>
        <p><strong>Status:</strong> 🟢 Online and Ready</p>
        <p><strong>Host:</strong> Render.com</p>
        <p><strong>Uptime:</strong> 24/7 Always Online</p>
        <p><strong>Start Time:</strong> """ + datetime.now().strftime("%Y-%m-%d %H:%M:%S") + """</p>
        <p><strong>Technology:</strong> Pure Python + Telegram Bot API</p>
    </div>
</body>
</html>
"""

def run_flask():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()

# Run the bot
if __name__ == '__main__':
    print("🔧 Starting bot...")
    keep_alive()
    time.sleep(2)  # Wait for Flask to start
    
    try:
        bot = TelegramBot()
        bot.run_bot()
    except Exception as e:
        print(f"❌ Bot startup failed: {e}")
        print("🔄 Restarting in 10 seconds...")
        time.sleep(10)
        
        # Restart
        bot = TelegramBot()
        bot.run_bot()
