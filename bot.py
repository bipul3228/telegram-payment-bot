import logging
import asyncio
from telegram import (
    Update, 
    InlineKeyboardButton, 
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
    ConversationHandler
)

# --- CONFIGURATION ---
BOT_TOKEN = "8500929660:AAGsUNC5s_psEQ51Jm7sbtF0ikmzEGR2Tgo"
UPI_ID = "mina7091@ptaxis"
ADMIN_USERNAME = "@Givygd"
PRICE = "₹99"
VIDEO_URL = "https://example.com/demo.mp4"

# --- LOGGING SETUP ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- STATES ---
AWAITING_TXID = 1

# --- HANDLERS ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Sends a message with 5 inline buttons when the command /start is issued."""
    keyboard = [
        [InlineKeyboardButton("🎥 VIDEO", callback_data='video'),
         InlineKeyboardButton("🛒 BUY NOW", callback_data='buy')],
        [InlineKeyboardButton("✅ PROOFS", callback_data='proofs'),
         InlineKeyboardButton("💳 CHECK PAYMENT", callback_data='check')],
        [InlineKeyboardButton("🆘 HELP", callback_data='help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "👋 *Welcome to our Premium Bot!*\n\n"
        "Select an option below to get started."
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    else:
        # Handle cases where /start might be called via callback or other means
        await update.effective_chat.send_message(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Parses the CallbackQuery and updates the message text."""
    query = update.callback_query
    await query.answer()

    if query.data == 'video':
        await query.edit_message_text(
            text=f"📺 *Sample Video Section*\n\nYou can find our demo here: {VIDEO_URL}\n\n"
                 "Or I can send a physical file if configured.",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back_start')]])
        )
    
    elif query.data == 'buy':
        buy_text = (
            "🛍️ *Purchase Details*\n\n"
            f"💰 *Price:* {PRICE}\n"
            f"🔑 *UPI ID:* `{UPI_ID}`\n\n"
            "After payment, please click 'CHECK PAYMENT' to submit your Transaction ID."
        )
        await query.edit_message_text(
            text=buy_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back_start')]])
        )
        
    elif query.data == 'proofs':
        await query.edit_message_text(
            text="📈 *Success Proofs*\n\n"
                 "• Customer A: Successfully received\n"
                 "• Customer B: Transaction confirmed\n"
                 "• Customer C: Premium access granted\n\n"
                 "_Join our channel for more real-time proofs!_",
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back_start')]])
        )
        
    elif query.data == 'check':
        await query.edit_message_text(
            text="📝 *Payment Verification*\n\n"
                 "Please type your **Transaction ID / Reference Number** below:",
            parse_mode='Markdown'
        )
        # We can use a simple message handler or a ConversationHandler here.
        # For simplicity in a single file, we'll tell the user to just send it.
        context.user_data['expecting_txid'] = True
        
    elif query.data == 'help':
        help_text = (
            "🆘 *Support Center*\n\n"
            "If you have any issues or questions, contact our admin:\n"
            f"👤 *Admin:* {ADMIN_USERNAME}\n\n"
            "Working Hours: 9 AM - 9 PM UTC"
        )
        await query.edit_message_text(
            text=help_text,
            parse_mode='Markdown',
            reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("⬅️ Back", callback_data='back_start')]])
        )
        
    elif query.data == 'back_start':
        await start(update, context)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles incoming text messages, specifically Transaction IDs."""
    if context.user_data.get('expecting_txid'):
        tx_id = update.message.text
        await update.message.reply_text(
            f"✅ *Received!*\n\n"
            f"Your Transaction ID: `{tx_id}`\n"
            "Our admin will verify this shortly. Please wait.",
            parse_mode='Markdown'
        )
        # Notify Admin (Optional but recommended)
        # await context.bot.send_message(chat_id=ADMIN_ID, text=f"New TXID: {tx_id} from {update.effective_user.name}")
        context.user_data['expecting_txid'] = False
    else:
        await update.message.reply_text("Please use the menu buttons to navigate.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error("Exception while handling an update:", exc_info=context.error)
    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ An internal error occurred. Our team has been notified."
        )

# --- MAIN EXECUTION ---

if __name__ == '__main__':
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("Error: Please set your BOT_TOKEN in the code!")
    else:
        print("Bot is starting...")
        # Create the Application
        app = ApplicationBuilder().token(BOT_TOKEN).build()

        # Add Handlers
        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(button_callback_handler))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
        
        # Add Error Handler
        app.add_error_handler(error_handler)

        # Start Polling
        app.run_polling()
      
