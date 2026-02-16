import telebot
from telebot import types
import sqlite3
from datetime import datetime
from keep_alive import keep_alive

# Bot Token - Direct configuration for Replit
TOKEN = '8564429139:AAEV_sVX0k-cmw4iVCwHo2y87r8qwPhsOag'
bot = telebot.TeleBot(TOKEN)

# Admin and staff IDs
ADMIN_ID = 5110033728
STAFF_IDS = [5110033728, 752640252, 8576036710, 0]

# Database setup
def init_db():
    conn = sqlite3.connect('pharmacy.db')
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

# Start keep alive web server
keep_alive()

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_staff(user_id):
    return user_id in STAFF_IDS or is_admin(user_id)

# Create main menu keyboard
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
            types.KeyboardButton('� የተሸጡ መድሃኒቶች'),
            types.KeyboardButton('�💵 ዋጋ ማስተካከል'),
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

# Back button
def get_back_button():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(types.KeyboardButton('🏠 ወደ ዋናው ሜኑ'))
    return markup

# Start command
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

# Handle button clicks
@bot.message_handler(func=lambda message: message.text in [
    '➕ መድሃኒት መጨመር', '📋 መድሃኒቶች', '💰 ሽያጭ', 
    '📊 ሁሉም ሽያጮች', '📊 የእኔ ሽያጮች', '📈 ሪፖርት', 
    '💵 ዋጋ ማስተካከል', '🗑 መድሃኒት ማጥፋት', '📝 የቀኑ መዝጋት', 
    '📦 የተሸጡ መድሃኒቶች', '🏠 ወደ ዋናው ሜኑ'
])
def handle_buttons(message):
    user_id = message.from_user.id
    
    if not is_staff(user_id):
        bot.reply_to(message, 'ፈቃድ የለዎትም።')
        return
    
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
    elif message.text == '➕ መድሃኒት መጨመር':
        if is_admin(user_id):
            add_medicine_start(message)
        else:
            bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
    elif message.text == '📋 መድሃኒቶች':
        list_medicines(message)
    elif message.text == '💰 ሽያጭ':
        sell_start(message)
    elif message.text == '📊 ሁሉም ሽያጮች':
        if is_admin(user_id):
            view_sales(message)
        else:
            bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
    elif message.text == '📊 የእኔ ሽያጮች':
        my_sales(message)
    elif message.text == '📈 ሪፖርት':
        if is_admin(user_id):
            generate_report(message)
        else:
            bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
    elif message.text == '💵 ዋጋ ማስተካከል':
        if is_admin(user_id):
            update_price_start(message)
        else:
            bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
    elif message.text == '🗑 መድሃኒት ማጥፋት':
        if is_admin(user_id):
            delete_medicine_start(message)
        else:
            bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
    elif message.text == '📝 የቀኑ መዝጋት':
        daily_closing(message)
    elif message.text == '📦 የተሸጡ መድሃኒቶች':
        if is_admin(user_id):
            sold_medicines_report(message)
        else:
            bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')

# Add medicine (Admin only)
@bot.message_handler(commands=['addmedicine'])
def add_medicine_start(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
        return
    
    msg = bot.reply_to(message, 'የመድሃኒቱን ስም ያስገቡ:', reply_markup=get_back_button())
    bot.register_next_step_handler(msg, get_medicine_name)

def get_medicine_name(message):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    name = message.text
    msg = bot.reply_to(message, 'ብዛት ያስገቡ:', reply_markup=get_back_button())
    bot.register_next_step_handler(msg, get_medicine_quantity, name)

def get_medicine_quantity(message, name):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    try:
        quantity = int(message.text)
        msg = bot.reply_to(message, 'ዋጋ ያስገቡ (በብር):', reply_markup=get_back_button())
        bot.register_next_step_handler(msg, get_medicine_price, name, quantity)
    except ValueError:
        msg = bot.reply_to(message, 'እባክዎ ትክክለኛ ቁጥር ያስገቡ:')
        bot.register_next_step_handler(msg, get_medicine_quantity, name)

def get_medicine_price(message, name, quantity):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    try:
        price = float(message.text)
        msg = bot.reply_to(message, 'መግለጫ ያስገቡ:', reply_markup=get_back_button())
        bot.register_next_step_handler(msg, save_medicine, name, quantity, price)
    except ValueError:
        msg = bot.reply_to(message, 'እባክዎ ትክክለኛ ዋጋ ያስገቡ:')
        bot.register_next_step_handler(msg, get_medicine_price, name, quantity)

def save_medicine(message, name, quantity, price):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    description = message.text
    user_id = message.from_user.id
    date = datetime.now().isoformat()
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute(
        'INSERT INTO medicines (name, quantity, price, description, added_by, added_date) VALUES (?, ?, ?, ?, ?, ?)',
        (name, quantity, price, description, user_id, date)
    )
    conn.commit()
    conn.close()
    
    # Send confirmation to user
    bot.reply_to(message,
        f'✅ መድሃኒት በተሳካ ሁኔታ ተጨምሯል!\n\n'
        f'ስም: {name}\n'
        f'ብዛት: {quantity}\n'
        f'ዋጋ: {price} ብር\n'
        f'መግለጫ: {description}',
        reply_markup=get_main_menu(user_id)
    )
    
    # Send notification to admin (if not admin adding)
    if user_id != ADMIN_ID:
        staff_name = message.from_user.first_name or "ሰራተኛ"
        admin_notification = f'🔔 *አዲስ መድሃኒት ተጨምሯል*\n\n'
        admin_notification += f'👤 በ: {staff_name}\n'
        admin_notification += f'📅 ቀን: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n\n'
        admin_notification += f'💊 *መድሃኒት:*\n'
        admin_notification += f'   ስም: {name}\n'
        admin_notification += f'   ብዛት: {quantity}\n'
        admin_notification += f'   ዋጋ: {price} ብር\n'
        admin_notification += f'   መግለጫ: {description}'
        
        try:
            bot.send_message(ADMIN_ID, admin_notification, parse_mode='Markdown')
        except:
            pass  # If admin is not reachable, continue


# List medicines
@bot.message_handler(commands=['listmedicines'])
def list_medicines(message):
    user_id = message.from_user.id
    
    if not is_staff(user_id):
        bot.reply_to(message, 'ፈቃድ የለዎትም።')
        return
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute('SELECT * FROM medicines WHERE quantity > 0')
    medicines = c.fetchall()
    conn.close()
    
    if not medicines:
        bot.reply_to(message, 'ምንም መድሃኒት አልተገኘም።')
        return
    
    response = '💊 *የሚገኙ መድሃኒቶች*\n\n'
    for i, med in enumerate(medicines, 1):
        response += f'{i}. *{med[1]}*\n'
        response += f'   ID: {med[0]}\n'
        response += f'   ብዛት: {med[2]}\n'
        
        # Only show price to admin
        if is_admin(user_id):
            response += f'   ዋጋ: {med[3]} ብር\n'
        
        response += f'   መግለጫ: {med[4]}\n\n'
    
    bot.reply_to(message, response, parse_mode='Markdown')

# Sell medicine - Search by name
@bot.message_handler(commands=['sell'])
def sell_start(message):
    user_id = message.from_user.id
    
    if not is_staff(user_id):
        bot.reply_to(message, 'ፈቃድ የለዎትም።')
        return
    
    msg = bot.reply_to(message, 'የመድሃኒቱን ስም ወይም ID ያስገቡ:', reply_markup=get_back_button())
    bot.register_next_step_handler(msg, search_medicine_for_sale)

def search_medicine_for_sale(message):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    search_term = message.text
    user_id = message.from_user.id
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    
    # Try to search by ID first
    try:
        medicine_id = int(search_term)
        c.execute('SELECT * FROM medicines WHERE id = ? AND quantity > 0', (medicine_id,))
        medicine = c.fetchone()
        
        if medicine:
            conn.close()
            
            # Show price only to admin
            if is_admin(user_id):
                msg = bot.reply_to(message, 
                    f'✅ ተገኝቷል: {medicine[1]}\n'
                    f'ያለው ብዛት: {medicine[2]}\n'
                    f'ዋጋ: {medicine[3]} ብር\n\n'
                    f'የሚሸጡትን ብዛት ያስገቡ:',
                    reply_markup=get_back_button()
                )
            else:
                msg = bot.reply_to(message, 
                    f'✅ ተገኝቷል: {medicine[1]}\n'
                    f'ያለው ብዛት: {medicine[2]}\n\n'
                    f'የሚሸጡትን ብዛት ያስገቡ:',
                    reply_markup=get_back_button()
                )
            
            bot.register_next_step_handler(msg, process_sale, medicine)
            return
    except ValueError:
        pass
    
    # Search by name
    c.execute('SELECT * FROM medicines WHERE name LIKE ? AND quantity > 0', (f'%{search_term}%',))
    medicines = c.fetchall()
    conn.close()
    
    if not medicines:
        msg = bot.reply_to(message, 'መድሃኒት አልተገኘም። እንደገና ይሞክሩ:', reply_markup=get_back_button())
        bot.register_next_step_handler(msg, search_medicine_for_sale)
        return
    
    if len(medicines) == 1:
        medicine = medicines[0]
        
        # Show price only to admin
        if is_admin(user_id):
            msg = bot.reply_to(message, 
                f'✅ ተገኝቷል: {medicine[1]}\n'
                f'ያለው ብዛት: {medicine[2]}\n'
                f'ዋጋ: {medicine[3]} ብር\n\n'
                f'የሚሸጡትን ብዛት ያስገቡ:',
                reply_markup=get_back_button()
            )
        else:
            msg = bot.reply_to(message, 
                f'✅ ተገኝቷል: {medicine[1]}\n'
                f'ያለው ብዛት: {medicine[2]}\n\n'
                f'የሚሸጡትን ብዛት ያስገቡ:',
                reply_markup=get_back_button()
            )
        
        bot.register_next_step_handler(msg, process_sale, medicine)
    else:
        # Multiple results - show list
        response = '🔍 የተገኙ መድሃኒቶች:\n\n'
        for med in medicines:
            if is_admin(user_id):
                response += f'ID: {med[0]} - {med[1]} (ብዛት: {med[2]}, ዋጋ: {med[3]} ብር)\n'
            else:
                response += f'ID: {med[0]} - {med[1]} (ብዛት: {med[2]})\n'
        response += '\nየመድሃኒቱን ID ያስገቡ:'
        
        msg = bot.reply_to(message, response, reply_markup=get_back_button())
        bot.register_next_step_handler(msg, search_medicine_for_sale)

def process_sale(message, medicine):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    try:
        quantity = int(message.text)
        user_id = message.from_user.id
        
        if quantity > medicine[2]:
            msg = bot.reply_to(message, f'በቂ መድሃኒት የለም። ያለው: {medicine[2]}. እንደገና ያስገቡ:', reply_markup=get_back_button())
            bot.register_next_step_handler(msg, process_sale, medicine)
            return
        
        total_price = quantity * medicine[3]
        date = datetime.now().isoformat()
        
        conn = sqlite3.connect('pharmacy.db')
        c = conn.cursor()
        
        c.execute(
            'INSERT INTO sales (medicine_id, quantity, total_price, sold_by, sale_date) VALUES (?, ?, ?, ?, ?)',
            (medicine[0], quantity, total_price, user_id, date)
        )
        
        c.execute(
            'UPDATE medicines SET quantity = quantity - ? WHERE id = ?',
            (quantity, medicine[0])
        )
        
        conn.commit()
        conn.close()
        
        # Send confirmation to user
        bot.reply_to(message,
            f'✅ ሽያጭ በተሳካ ሁኔታ ተመዝግቧል!\n\n'
            f'መድሃኒት: {medicine[1]}\n'
            f'ብዛት: {quantity}\n'
            f'አጠቃላይ ዋጋ: {total_price} ብር\n'
            f'የቀረው: {medicine[2] - quantity}',
            reply_markup=get_main_menu(user_id)
        )
        
        # Send notification to admin
        staff_name = message.from_user.first_name or "ሰራተኛ"
        admin_notification = f'💰 *አዲስ ሽያጭ*\n\n'
        admin_notification += f'👤 በ: {staff_name}\n'
        admin_notification += f'📅 ቀን: {datetime.now().strftime("%Y-%m-%d %H:%M")}\n\n'
        admin_notification += f'💊 መድሃኒት: {medicine[1]}\n'
        admin_notification += f'📦 ብዛት: {quantity}\n'
        admin_notification += f'💵 ዋጋ: {total_price} ብር\n'
        admin_notification += f'📊 የቀረው: {medicine[2] - quantity}'
        
        try:
            bot.send_message(ADMIN_ID, admin_notification, parse_mode='Markdown')
        except:
            pass  # If admin is not reachable, continue
    except ValueError:
        msg = bot.reply_to(message, 'እባክዎ ትክክለኛ ብዛት ያስገቡ:', reply_markup=get_back_button())
        bot.register_next_step_handler(msg, process_sale, medicine)

# View all sales (Admin only)
@bot.message_handler(commands=['sales'])
def view_sales(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
        return
    
    from datetime import datetime
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute('''
        SELECT s.id, s.medicine_id, s.quantity, s.total_price, s.sale_date, s.sold_by, m.name 
        FROM sales s 
        JOIN medicines m ON s.medicine_id = m.id 
        ORDER BY s.sale_date DESC LIMIT 50
    ''')
    sales = c.fetchall()
    conn.close()
    
    if not sales:
        bot.reply_to(message, 'ምንም ሽያጭ አልተገኘም።', reply_markup=get_main_menu(user_id))
        return
    
    response = '📊 *ሁሉም ሽያጮች (የመጨረሻዎቹ 50)*\n\n'
    total = 0
    
    for i, sale in enumerate(sales, 1):
        response += f'{i}. {sale[6]}\n'
        response += f'   ብዛት: {sale[2]}\n'
        response += f'   ዋጋ: {sale[3]} ብር\n'
        response += f'   ቀን: {sale[4][:16].replace("T", " ")}\n\n'
        total += sale[3]
        
        # Split message if too long
        if i % 15 == 0 and i < len(sales):
            response += f'💰 *ድምር እስካሁን: {total:.2f} ብር*'
            bot.send_message(message.chat.id, response, parse_mode='Markdown')
            response = ''
    
    if response:
        response += f'\n💰 *አጠቃላይ: {total:.2f} ብር*\n'
        response += f'📦 *ጠቅላላ ሽያጮች: {len(sales)}*'
        bot.reply_to(message, response, parse_mode='Markdown', reply_markup=get_main_menu(user_id))
        bot.reply_to(message, response, parse_mode='Markdown', reply_markup=get_main_menu(user_id))


# View my sales (Staff)
@bot.message_handler(commands=['mysales'])
def my_sales(message):
    user_id = message.from_user.id
    
    if not is_staff(user_id):
        bot.reply_to(message, 'ፈቃድ የለዎትም።')
        return
    
    from datetime import datetime, timedelta
    
    # Get today's sales (last 24 hours)
    yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    c.execute('''
        SELECT s.id, s.medicine_id, s.quantity, s.total_price, s.sale_date, s.sold_by, m.name 
        FROM sales s 
        JOIN medicines m ON s.medicine_id = m.id 
        WHERE s.sold_by = ? AND s.sale_date >= ?
        ORDER BY s.sale_date DESC
    ''', (user_id, yesterday))
    sales = c.fetchall()
    conn.close()
    
    if not sales:
        bot.reply_to(message, 'በመጨረሻዎቹ 24 ሰዣት ውስጥ ምንም ሽያጭ አልተገኘም።', reply_markup=get_main_menu(user_id))
        return
    
    response = '📊 *የእኔ የዛሬ ሽያጮች (24 ሰዓት)*\n\n'
    total = 0
    
    for i, sale in enumerate(sales, 1):
        response += f'{i}. {sale[6]}\n'
        response += f'   ብዛት: {sale[2]}\n'
        response += f'   ዋጋ: {sale[3]} ብር\n'
        response += f'   ቀን: {sale[4][:16].replace("T", " ")}\n\n'
        total += sale[3]
    
    response += f'\n💰 *አጠቃላይ ገቢ: {total:.2f} ብር*\n'
    response += f'📦 *ጠቅላላ ሽያጮች: {len(sales)}*'
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=get_main_menu(user_id))

# Daily closing report (Staff)
@bot.message_handler(commands=['closing'])
def daily_closing(message):
    user_id = message.from_user.id
    
    if not is_staff(user_id):
        bot.reply_to(message, 'ፈቃድ የለዎትም।')
        return
    
    from datetime import datetime, timedelta
    
    # Get today's sales (last 24 hours)
    yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
    today_date = datetime.now().strftime('%Y-%m-%d %H:%M')
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    
    # Get my sales for today
    c.execute('''
        SELECT s.id, s.medicine_id, s.quantity, s.total_price, s.sale_date, s.sold_by, m.name 
        FROM sales s 
        JOIN medicines m ON s.medicine_id = m.id 
        WHERE s.sold_by = ? AND s.sale_date >= ?
        ORDER BY s.sale_date DESC
    ''', (user_id, yesterday))
    my_sales_data = c.fetchall()
    
    # Get all sales for today (for comparison)
    c.execute('''
        SELECT COUNT(*), SUM(total_price)
        FROM sales 
        WHERE sale_date >= ?
    ''', (yesterday,))
    all_sales_stats = c.fetchone()
    
    conn.close()
    
    # Calculate my totals
    my_total = sum(sale[3] for sale in my_sales_data)
    my_count = len(my_sales_data)
    
    # Build report
    response = f'📝 *የቀኑ መዝጋት - {today_date}*\n\n'
    response += '━━━━━━━━━━━━━━━━━━━━\n\n'
    
    response += '👤 *የእኔ ሽያጮች:*\n'
    response += f'   📦 ጠቅላላ ሽያጮች: {my_count}\n'
    response += f'   💰 ጠቅላላ ገቢ: {my_total:.2f} ብር\n\n'
    
    if my_sales_data:
        response += '📋 *ዝርዝር:*\n'
        for i, sale in enumerate(my_sales_data[:10], 1):  # Show top 10
            response += f'{i}. {sale[6]} - {sale[3]} ብር\n'
        
        if len(my_sales_data) > 10:
            response += f'\n... እና ሌሎች {len(my_sales_data) - 10}\n'
    
    response += '\n━━━━━━━━━━━━━━━━━━━━\n\n'
    
    response += '🏥 *የፋርማሲው ጠቅላላ (24 ሰዓት):*\n'
    response += f'   📦 ጠቅላላ ሽያጮች: {all_sales_stats[0] or 0}\n'
    response += f'   💰 ጠቅላላ ገቢ: {all_sales_stats[1] or 0:.2f} ብር\n\n'
    
    if all_sales_stats[1] and all_sales_stats[1] > 0:
        my_percentage = (my_total / all_sales_stats[1]) * 100
        response += f'📊 *የእኔ አስተዋፅዖ: {my_percentage:.1f}%*\n'
    
    # Send to staff member
    bot.reply_to(message, response, parse_mode='Markdown', reply_markup=get_main_menu(user_id))
    
    # Send notification to admin
    staff_name = message.from_user.first_name or "ሰራተኛ"
    admin_notification = f'🔔 *የቀኑ መዝጋት ማሳወቂያ*\n\n'
    admin_notification += f'👤 ሰራተኛ: {staff_name}\n'
    admin_notification += f'📅 ቀን: {today_date}\n\n'
    admin_notification += f'📦 ሽያጮች: {my_count}\n'
    admin_notification += f'💰 ገቢ: {my_total:.2f} ብር\n\n'
    
    if all_sales_stats[1] and all_sales_stats[1] > 0:
        admin_notification += f'📊 አስተዋፅዖ: {my_percentage:.1f}%\n\n'
    
    admin_notification += '✅ የቀኑ መዝጋት ተጠናቋል።'
    
    # Archive today's sales and reset for new day (Admin only)
    if is_admin(user_id):
        conn = sqlite3.connect('pharmacy.db')
        c = conn.cursor()
        
        # Archive all sales from last 24 hours
        archive_date = datetime.now().isoformat()
        c.execute('''
            INSERT INTO archived_sales (medicine_id, quantity, total_price, sold_by, sale_date, archived_date)
            SELECT medicine_id, quantity, total_price, sold_by, sale_date, ?
            FROM sales
            WHERE sale_date >= ?
        ''', (archive_date, yesterday))
        
        # Save closing record
        c.execute('''
            INSERT INTO daily_closings (closed_by, closing_date, total_sales, total_revenue)
            VALUES (?, ?, ?, ?)
        ''', (user_id, archive_date, all_sales_stats[0] or 0, all_sales_stats[1] or 0))
        
        # Delete archived sales
        c.execute('DELETE FROM sales WHERE sale_date >= ?', (yesterday,))
        
        conn.commit()
        conn.close()
        
        admin_notification += '\n\n🗂️ *ሽያጮች archived ተደርገዋል።*\n'
        admin_notification += '✨ *አዲስ ቀን ተጀምሯል!*'
    
    try:
        bot.send_message(ADMIN_ID, admin_notification, parse_mode='Markdown')
    except:
        pass  # If admin is not reachable, continue

# Sold medicines report (Admin only)
@bot.message_handler(commands=['soldmedicines'])
def sold_medicines_report(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
        return
    
    from datetime import datetime, timedelta
    
    # Get last 24 hours
    yesterday = (datetime.now() - timedelta(hours=24)).isoformat()
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    
    # Get sold medicines summary
    c.execute('''
        SELECT m.name, SUM(s.quantity) as total_qty, SUM(s.total_price) as total_price, COUNT(*) as times_sold
        FROM sales s
        JOIN medicines m ON s.medicine_id = m.id
        WHERE s.sale_date >= ?
        GROUP BY m.name
        ORDER BY total_price DESC
    ''', (yesterday,))
    sold_medicines = c.fetchall()
    
    # Get total stats
    c.execute('''
        SELECT COUNT(*), SUM(total_price)
        FROM sales
        WHERE sale_date >= ?
    ''', (yesterday,))
    total_stats = c.fetchone()
    
    conn.close()
    
    if not sold_medicines:
        bot.reply_to(message, 'በመጨረሻዎቹ 24 ሰዓት ውስጥ ምንም ሽያጭ አልተገኘም።', reply_markup=get_main_menu(user_id))
        return
    
    response = '📦 *የተሸጡ መድሃኒቶች (24 ሰዓት)*\n\n'
    response += '━━━━━━━━━━━━━━━━━━━━\n\n'
    
    for i, med in enumerate(sold_medicines, 1):
        response += f'{i}. *{med[0]}*\n'
        response += f'   📦 ብዛት: {med[1]}\n'
        response += f'   💰 ገቢ: {med[2]:.2f} ብር\n'
        response += f'   🔄 ጊዜ: {med[3]} ጊዜ ተሽጧል\n\n'
        
        # Split message if too long
        if i % 10 == 0 and i < len(sold_medicines):
            bot.send_message(message.chat.id, response, parse_mode='Markdown')
            response = ''
    
    if response:
        response += '\n━━━━━━━━━━━━━━━━━━━━\n\n'
        response += f'📊 *ጠቅላላ ማጠቃለያ:*\n'
        response += f'   📦 ጠቅላላ ሽያጮች: {total_stats[0]}\n'
        response += f'   💰 ጠቅላላ ገቢ: {total_stats[1]:.2f} ብር\n'
        response += f'   🏷️ የተለያዩ መድሃኒቶች: {len(sold_medicines)}'
        
        bot.reply_to(message, response, parse_mode='Markdown', reply_markup=get_main_menu(user_id))

# Generate report (Admin only)
@bot.message_handler(commands=['report'])
def generate_report(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
        return
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    
    # Total medicines
    c.execute('SELECT COUNT(*), SUM(quantity) FROM medicines')
    med_stats = c.fetchone()
    
    # Total sales
    c.execute('SELECT COUNT(*), SUM(total_price) FROM sales')
    sales_stats = c.fetchone()
    
    # Low stock medicines
    c.execute('SELECT name, quantity FROM medicines WHERE quantity < 10 AND quantity > 0')
    low_stock = c.fetchall()
    
    conn.close()
    
    response = '📊 *የኦሜጋ ፋርማሲ ሪፖርት*\n\n'
    response += f'📦 *የመድሃኒት ክምችት*\n'
    response += f'   አይነቶች: {med_stats[0] or 0}\n'
    response += f'   አጠቃላይ ብዛት: {med_stats[1] or 0}\n\n'
    
    response += f'💰 *ሽያጮች*\n'
    response += f'   ጠቅላላ ሽያጮች: {sales_stats[0] or 0}\n'
    response += f'   ጠቅላላ ገቢ: {sales_stats[1] or 0:.2f} ብር\n\n'
    
    if low_stock:
        response += '⚠️ *ዝቅተኛ ክምችት*\n'
        for med in low_stock:
            response += f'   • {med[0]}: {med[1]}\n'
    
    bot.reply_to(message, response, parse_mode='Markdown')

# Delete medicine (Admin only)
@bot.message_handler(commands=['deletemedicine'])
def delete_medicine_start(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
        return
    
    msg = bot.reply_to(message, 'የሚሰረዘውን መድሃኒት ID ያስገቡ:', reply_markup=get_back_button())
    bot.register_next_step_handler(msg, delete_medicine)

def delete_medicine(message):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    try:
        medicine_id = int(message.text)
        
        conn = sqlite3.connect('pharmacy.db')
        c = conn.cursor()
        c.execute('DELETE FROM medicines WHERE id = ?', (medicine_id,))
        conn.commit()
        
        if c.rowcount > 0:
            bot.reply_to(message, '✅ መድሃኒት ተሰርዟል።', reply_markup=get_main_menu(message.from_user.id))
        else:
            msg = bot.reply_to(message, 'መድሃኒት አልተገኘም። እንደገና ይሞክሩ:', reply_markup=get_back_button())
            bot.register_next_step_handler(msg, delete_medicine)
        
        conn.close()
    except ValueError:
        msg = bot.reply_to(message, 'እባክዎ ትክክለኛ ID ያስገቡ:', reply_markup=get_back_button())
        bot.register_next_step_handler(msg, delete_medicine)

# Update medicine price (Admin only)
@bot.message_handler(commands=['updateprice'])
def update_price_start(message):
    user_id = message.from_user.id
    
    if not is_admin(user_id):
        bot.reply_to(message, 'ይህ ትዕዛዝ ለአስተዳዳሪ ብቻ ነው።')
        return
    
    msg = bot.reply_to(message, 'የመድሃኒቱን ስም ወይም ID ያስገቡ:', reply_markup=get_back_button())
    bot.register_next_step_handler(msg, search_medicine_for_price_update)

def search_medicine_for_price_update(message):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    search_term = message.text
    
    conn = sqlite3.connect('pharmacy.db')
    c = conn.cursor()
    
    # Try to search by ID first
    try:
        medicine_id = int(search_term)
        c.execute('SELECT * FROM medicines WHERE id = ?', (medicine_id,))
        medicine = c.fetchone()
        
        if medicine:
            conn.close()
            msg = bot.reply_to(message, 
                f'✅ ተገኝቷል: {medicine[1]}\n'
                f'የአሁኑ ዋጋ: {medicine[3]} ብር\n\n'
                f'አዲሱን ዋጋ ያስገቡ:',
                reply_markup=get_back_button()
            )
            bot.register_next_step_handler(msg, update_medicine_price, medicine[0])
            return
    except ValueError:
        pass
    
    # Search by name
    c.execute('SELECT * FROM medicines WHERE name LIKE ?', (f'%{search_term}%',))
    medicines = c.fetchall()
    conn.close()
    
    if not medicines:
        msg = bot.reply_to(message, 'መድሃኒት አልተገኘም። እንደገና ይሞክሩ:', reply_markup=get_back_button())
        bot.register_next_step_handler(msg, search_medicine_for_price_update)
        return
    
    if len(medicines) == 1:
        medicine = medicines[0]
        msg = bot.reply_to(message, 
            f'✅ ተገኝቷል: {medicine[1]}\n'
            f'የአሁኑ ዋጋ: {medicine[3]} ብር\n\n'
            f'አዲሱን ዋጋ ያስገቡ:',
            reply_markup=get_back_button()
        )
        bot.register_next_step_handler(msg, update_medicine_price, medicine[0])
    else:
        # Multiple results - show list
        response = '🔍 የተገኙ መድሃኒቶች:\n\n'
        for med in medicines:
            response += f'ID: {med[0]} - {med[1]} (ዋጋ: {med[3]} ብር)\n'
        response += '\nየመድሃኒቱን ID ያስገቡ:'
        
        msg = bot.reply_to(message, response, reply_markup=get_back_button())
        bot.register_next_step_handler(msg, search_medicine_for_price_update)

def update_medicine_price(message, medicine_id):
    if message.text == '🏠 ወደ ዋናው ሜኑ':
        start(message)
        return
    
    try:
        new_price = float(message.text)
        
        conn = sqlite3.connect('pharmacy.db')
        c = conn.cursor()
        c.execute('UPDATE medicines SET price = ? WHERE id = ?', (new_price, medicine_id))
        conn.commit()
        conn.close()
        
        bot.reply_to(message, 
            f'✅ ዋጋ በተሳካ ሁኔታ ተቀይሯል!\n'
            f'አዲሱ ዋጋ: {new_price} ብር',
            reply_markup=get_main_menu(message.from_user.id)
        )
    except ValueError:
        msg = bot.reply_to(message, 'እባክዎ ትክክለኛ ዋጋ ያስገቡ:', reply_markup=get_back_button())
        bot.register_next_step_handler(msg, update_medicine_price, medicine_id)

print('🏥 OMEGA Pharmacy Bot is running...')
bot.infinity_polling()
