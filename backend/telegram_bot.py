import os
import logging
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Logger setup
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Constants
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ALLOWED_USER_ID = os.getenv("TELEGRAM_ALLOWED_USER_ID") # Optional: Restrict to one user

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    logger.info(f"User {user_id} started the bot.")
    
    if ALLOWED_USER_ID and str(user_id) != str(ALLOWED_USER_ID):
         await context.bot.send_message(chat_id=update.effective_chat.id, text="⛔ Unauthorized access.")
         return

    await context.bot.send_message(
        chat_id=update.effective_chat.id, 
        text=(
            "👋 Hello! I am your Antigravity Interface.\n\n"
            "Here's what I can do:\n"
            "/agents - List available agents/scripts\n"
            "/status - Check running tasks\n"
            "You can also just chat with me!"
        )
    )

async def agents(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # This list could be dynamic in the future
    agent_list = [
        "api_powerhouse.py (Lead Gen)",
        "run_full_cycle.py (Full Workflow)",
        "check_api_keys.py (Diagnostics)"
    ]
    formatted_list = "\n".join([f"- {a}" for a in agent_list])
    await context.bot.send_message(chat_id=update.effective_chat.id, text=f"🤖 **Available Agents:**\n{formatted_list}")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Placeholder for actual status tracking
    await context.bot.send_message(chat_id=update.effective_chat.id, text="✅ System is Online. No active background tasks reported yet.")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Echoes the user message. 
    TODO: Connect this to OpenAI/Anthropic for real conversation.
    """
    user_text = update.message.text
    # For now, just a simple acknowledgment to prove connectivity
    reply_text = f"I received: {user_text}\n(LLM connection coming soon!)"
    await context.bot.send_message(chat_id=update.effective_chat.id, text=reply_text)

def run_telegram_bot():
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is missing in .env")
        return

    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('agents', agents))
    application.add_handler(CommandHandler('status', status))
    application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), echo))
    
    logger.info("Telegram Bot is starting polling...")
    application.run_polling()

if __name__ == '__main__':
    run_telegram_bot()
