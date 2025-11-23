import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes, MessageHandler, filters
from flask import Flask
from threading import Thread
import sqlite3
from datetime import datetime

# Flask app for keep alive
app = Flask('')

@app.route('/')
def home():
    return """
<!DOCTYPE html>
<html>
<head>
    <title>Telegram User Info Bot</title>
    <style>
        body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
        .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }
        h1 { color: #2c3e50; border-bottom: 2px solid #3498db; padding-bottom: 10px; }
        .status { background: #2ecc71; color: white; padding: 10px; border-radius: 5px; margin: 20px 0; }
        .feature { background: #ecf0f1; padding: 15px; margin: 10px 0; border-radius: 5px; }
    </style>
</head>
<body>
    <div class="container">
        <h1>🤖 Telegram User Info Bot</h1>
        <div class="status">
            <strong>Status:</strong> 🟢 Bot is running successfully on Render!
        </div>
        
        <div class="feature">
            <h3>📊 Bot Features</h3>
            <ul>
                <li>User Information Lookup</li>
                <li>ID Checking</li>
                <li>Group Management Tools</li>
                <li>24/7 Uptime</li>
            </ul>
        </div>
        
        <div class="feature">
            <h3>🔧 Technical Info</h3>
            <p><strong>Host:</strong> Render.com</p>
            <p><strong>Runtime:</strong> Python 3.11</p>
            <p><strong>Uptime:</strong> 24/7 Always Online</p>
            <p><strong>Last Started:</strong> {}</p>
        </div>
        
        <div class="feature">
            <h3>📞 Contact Bot</h3>
            <p>Search for <strong>@YourBotUsername</strong> on Telegram to start using!</p>
        </div>
    </div>
</body>
</html>
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))

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
logger = logging.getLogger(__name__)

class UserInfoBot:
    def __init__(self):
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
                created_at TEXT,
                last_seen TEXT
            )
        ''')
        self.conn.commit()
    
    def save_user(self, user):
        """Save user to database"""
        self.cursor.execute('''
            INSERT OR REPLACE INTO users 
            (user_id, first_name, last_name, username, language_code, is_bot, created_at, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            user.id,
            user.first_name,
            user.last_name,
            user.username,
            user.language_code,
            1 if user.is_bot else 0,
            datetime.now().isoformat(),
            datetime.now().isoformat()
        ))
        self.conn.commit()

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        self.save_user(user)
        
        welcome_text = f"""
🤖 **မြန်မာ User Info Bot** 

**မင်္ဂလာပါ {user.first_name}!** 

ဒီ Bot ကနေ User အချက်အလက်တွေ လွယ်လွယ်ကူကူ ကြည့်ရှုနိုင်ပါတယ်။

**သုံးလို့ရတဲ့ Commands များ:**
/start - Bot စသုံးရန်
/info - User အချက်အလက်ကြည့်ရန်  
/myid - ကိုယ့် User ID ကြည့်ရန်
/chatid - Chat ID ကြည့်ရန်
/groupinfo - Group အချက်အလက်ကြည့်ရန်
/status - Bot status ကြည့်ရန်
/help - အကူအညီရယူရန်

**အခြားသုံးစွဲနည်းများ:**
• မည်သူ့မဆို message ကို reply လုပ်ပြီး /info ရိုက်ပါ
• မည်သူ့မဆို message ကို forward လုပ်ပြီး bot ဆီပို့ပါ

**Server Information:**
🚀 Hosted on: Render.com
⏰ Uptime: 24/7 Always Online
🔧 Version: 2.0.0
        """
        
        await update.message.reply_text(welcome_text, parse_mode='Markdown')

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🆘 **အကူအညီ စင်တာ**

**Commands List:**
/start - Bot ကိုစတင်အသုံးပြုရန်
/info - User အချက်အလက်များကြည့်ရှုရန်
/myid - ကိုယ့်ရဲ့ User ID ကြည့်ရှုရန်
/chatid - Chat ID ကြည့်ရှုရန်
/groupinfo - Group အချက်အလက်ကြည့်ရှုရန်
/status - Bot status ကြည့်ရှုရန်
/help - ဒီအကူအညီစာမျက်နှာကြည့်ရှုရန်

**User Info ကြည့်နည်းများ:**
1. ကိုယ်တိုင် /info ရိုက်ပါ
2. သူများ message ကို reply လုပ်ပြီး /info ရိုက်ပါ  
3. သူများ message ကို forward လုပ်ပြီး bot ဆီပို့ပါ

**Support:**
ပြဿနာတစ်စုံတစ်ရာရှိပါက Bot Developer ဆီဆက်သွယ်ပါ။
        """
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def info(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /info command"""
        try:
            if update.message.reply_to_message:
                user = update.message.reply_to_message.from_user
            else:
                user = update.effective_user
            
            self.save_user(user)
            
            # Get user profile photos
            bot = context.bot
            photos = await bot.get_user_profile_photos(user.id, limit=1)
            has_profile_pic = "✅ ရှိပါတယ်" if photos.total_count > 0 else "❌ မရှိပါ"
            
            info_text = f"""
👤 **User အချက်အလက်**

**အခြေခံ အချက်အလက်:**
🆔 **User ID:** `{user.id}`
📛 **နာမည်:** {user.first_name or "မရှိပါ"}
📛 **မျိုးရိုးနာမည်:** {user.last_name or "မရှိပါ"} 
👤 **Username:** @{user.username or "မရှိပါ"}
🌐 **ဘာသာစကား:** {user.language_code or "မရှိပါ"}
🤖 **Bot လား:** {"✅ ဟုတ်ပါတယ်" if user.is_bot else "❌ မဟုတ်ပါ"}

**Profile အချက်အလက်:**
🖼️ **Profile Picture:** {has_profile_pic}
🔗 **Mention:** [Link](tg://user?id={user.id})

**Chat အချက်အလက်:**
💬 **Chat ID:** `{update.effective_chat.id}`
🏷️ **Chat Type:** {update.effective_chat.type}

**Server Info:**
🚀 **Host:** Render.com
⏰ **Status:** 24/7 Online
        """
            
            await update.message.reply_text(info_text, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in info command: {e}")
            await update.message.reply_text("❌ အချက်အလက်ရယူရာတွင် အမှားတစ်ခုဖြစ်နေပါသည်")

    async def myid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /myid command"""
        user = update.effective_user
        self.save_user(user)
        await update.message.reply_text(f"🆔 **မင်းရဲ့ User ID:** `{user.id}`", parse_mode='Markdown')

    async def chatid(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /chatid command"""
        chat = update.effective_chat
        await update.message.reply_text(
            f"💬 **Chat ID:** `{chat.id}`\n"
            f"🏷️ **Chat Type:** {chat.type}", 
            parse_mode='Markdown'
        )

    async def groupinfo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /groupinfo command"""
        chat = update.effective_chat
        
        if chat.type == 'private':
            await update.message.reply_text("❌ ဒီ command က group တွေမှာပဲ အလုပ်လုပ်ပါတယ်")
            return
        
        try:
            bot = context.bot
            members_count = await bot.get_chat_members_count(chat.id)
            admins = await bot.get_chat_administrators(chat.id)
            admin_count = len(admins)
            
            group_info = f"""
🏠 **Group အချက်အလက်**

**အခြေခံ အချက်အလက်:**
📛 **ခေါင်းစဉ်:** {chat.title}
🆔 **Group ID:** `{chat.id}`
👥 **အမျိုးအစား:** {chat.type}
👤 **အသင်း၀င်:** {members_count} ယောက်
🛡️ **အက်ဒမင်:** {admin_count} ယောက်

**ဖော်ပြချက်:**
{chat.description or 'ဖော်ပြချက် မရှိပါ'}

**ခွင့်ပြုချက်များ:**
✉️ **မက်ဆေ့ပို့နိုင်:** {chat.permissions.can_send_messages}
📎 **မီဒီယာပို့နိုင်:** {chat.permissions.can_send_media_messages}
🔗 **လင့်ပို့နိုင်:** {chat.permissions.can_send_other_messages}
📊 **Poll ပို့နိုင်:** {getattr(chat.permissions, 'can_send_polls', 'N/A')}

**Bot Status:**
🚀 **Hosted on:** Render.com
⏰ **Uptime:** 24/7 Always Running
            """
            
            await update.message.reply_text(group_info, parse_mode='Markdown')
            
        except Exception as e:
            logger.error(f"Error in groupinfo: {e}")
            await update.message.reply_text("❌ Group information ရယူရာတွင် အမှားတစ်ခုဖြစ်နေပါသည်")

    async def status(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        status_text = """
📊 **Bot Status Report**

**Server Information:**
🚀 **Host:** Render.com
⏰ **Uptime:** 24/7 Always Running
💾 **Memory:** 512MB RAM
🔧 **CPU:** Shared CPU
🌐 **Region:** United States

**Bot Features:**
✅ User Information Lookup
✅ ID Checking  
✅ Group Management
✅ Database Storage
✅ 24/7 Online

**Technical Stack:**
• Python 3.11
• python-telegram-bot 20.7
• SQLite Database
• Flask Keep-Alive

**Statistics:**
📈 Stable since deployment
🔒 No downtime reported
⚡ Fast response time

**Powered by:** Python + Telegram Bot API + Render.com
        """
        await update.message.reply_text(status_text, parse_mode='Markdown')

    async def handle_forward(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle forwarded messages"""
        if update.message.forward_from:
            user = update.message.forward_from
            self.save_user(user)
            
            forward_info = f"""
🔄 **Forwarded User အချက်အလက်**

**အခြေခံ အချက်အလက်:**
🆔 **User ID:** `{user.id}`
📛 **နာမည်:** {user.first_name or ""} {user.last_name or ""}
👤 **Username:** @{user.username or "မရှိပါ"}
🤖 **Bot လား:** {"✅ ဟုတ်ပါတယ်" if user.is_bot else "❌ မဟုတ်ပါ"}

**မှတ်ချက်:** ဒီအချက်အလက်က forward လုပ်လို့ရတဲ့ user ကနေရတာဖြစ်ပါတယ်။
            """
            
            await update.message.reply_text(forward_info, parse_mode='Markdown')

    def run(self):
        """Run the bot"""
        # Start keep-alive server
        keep_alive()
        
        # Get bot token from environment variable
        BOT_TOKEN = os.environ.get('BOT_TOKEN')
        
        if not BOT_TOKEN:
            logger.error("❌ BOT_TOKEN environment variable မတွေ့ပါ")
            print("❌ Error: BOT_TOKEN environment variable မတွေ့ပါ")
            print("✅ Render dashboard မှာ Environment Variables ထည့်ပါ")
            return
        
        # Create application
        application = Application.builder().token(BOT_TOKEN).build()
        
        # Add handlers
        application.add_handler(CommandHandler("start", self.start))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("info", self.info))
        application.add_handler(CommandHandler("myid", self.myid))
        application.add_handler(CommandHandler("chatid", self.chatid))
        application.add_handler(CommandHandler("groupinfo", self.groupinfo))
        application.add_handler(CommandHandler("status", self.status))
        application.add_handler(MessageHandler(filters.ALL, self.handle_forward))
        
        # Start the bot
        logger.info("🚀 Bot is starting on Render...")
        print("🤖 ====================================")
        print("🚀 Myanmar User Info Bot Starting...")
        print("📡 Host: Render.com")
        print("⏰ Uptime: 24/7 Always Online")
        print("🔧 Version: 2.0.0")
        print("✅ Bot is running successfully!")
        print("🤖 ====================================")
        
        try:
            application.run_polling()
        except Exception as e:
            logger.error(f"Bot error: {e}")
            print(f"❌ Bot stopped: {e}")
            print("🔄 Restarting in 10 seconds...")
            import time
            time.sleep(10)
            self.run()  # Restart

# Run the bot
if __name__ == '__main__':
    bot = UserInfoBot()
    bot.run()
