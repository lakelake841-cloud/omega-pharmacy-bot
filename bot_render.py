import telebot
from telebot import types
import sqlite3
from datetime import datetime, timedelta
import os

# Bot Token
TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '8564429139:AAEV_sVX0k-cmw4iVCwHo2y87r8qwPhsOag')
bot = telebot.TeleBot(TOKEN)

# Admin and staff IDs
ADMIN_ID = 5110033728
STAFF_IDS = [5110033728, 752640252, 8576036710, 0]

# Database path - use /tmp for Render (writable)
DB_PATH = '/tmp/pharmacy.db'

# Helper function
def get_db():
    return sqlite3.connect(DB_PATH)

# Database setup
def init_db():
    conn = get_db()
    c = conn.cursor()
    
    c.execute('''CREATE TABLE IF NOT EXISTS users (
        telegram_id INTEGER PRIMARY KEY,
        name TEXT,
        role TEXT,
        active INTEGER DEFAULT 1
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS medicines (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        quantity INTEGER,
        price REAL,
        description TEXT,
        added_by INTEGER,
        added_date TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        sold_by INTEGER,
        sale_date TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS archived_sales (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        medicine_id INTEGER,
        quantity INTEGER,
        total_price REAL,
        sold_by INTEGER,
        sale_date TEXT,
        archived_date TEXT
    )''')
    
    c.execute('''CREATE TABLE IF NOT EXISTS daily_closings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        closed_by INTEGER,
        closing_date TEXT,
        total_sales INTEGER,
        total_revenue REAL
    )''')
    
    conn.commit()
    conn.close()

init_db()

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_staff(user_id):
    return user_id in STAFF_IDS or is_admin(user_id)

# Main menu
def get_main_menu(user_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    
    if is_admin(user_id):
        markup.add(
            types.KeyboardButton('➕ መድሃኒት መጨመር'),
            types.KeyboardButton('📋 መድሃኒቶች'),
            types.KeyboardButton('💰 ሽያጭ'),
            types.KeyboardButton('📊 ሁሉም ሽያጮች'),
            types.KeyboardButton('📦 የተሸጡ መድሃኒቶች'),
            types.KeyboardButton('💵 ዋጋ ማስተካከል'),
            types.KeyboardButton('📈 ሪፖርት'),
            types.KeyboardButton('🗑 መድሃኒት ማጥፋት')
        )
    elif is_staff(user_id):
        markup.add(
            types.KeyboardButton('📋 መድሃኒቶች'),
            types.KeyboardButton('💰 ሽያጭ'),
            types.KeyboardButton('📊 የእኔ ሽያጮች'),
            types.KeyboardButton('📝 የቀኑ መዝጋት')
        )
    
    return markup

def get_back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('🏠 ወደ ዋናው ሜኑ'))
    return markup

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    
    if is_admin(user_id):
        bot.reply_to(message, 
            '🏥 *OMEGA PHARMACY - Admin Panel*\n\n'
            'እንኳን ደህና መጡ!\n\n'
            'ከታች ካሉት አማራጮች ይምረጡ:',
            parse_mode='Markdown',
            reply_markup=get_main_menu(user_id)
        )
    elif is_staff(user_id):
        bot.reply_to(message,
            '🏥 *OMEGA PHARMACY - Staff Panel*\n\n'
            'እንኳን ደህና መጡ!\n\n'
            'ከታች ካሉት አማራጮች ይምረጡ:',
            parse_mode='Markdown',
            reply_markup=get_main_menu(user_id)
        )
    else:
        bot.reply_to(message, 'ይቅርታ፣ ይህን ቦት የመጠቀም ፈቃድ የለዎትም።')

print('🏥 OMEGA Pharmacy Bot is running...')
print(f'📁 Database: {DB_PATH}')
bot.infinity_polling()
