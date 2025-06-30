import os
import re
import nest_asyncio
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler,
    filters, ConversationHandler, ContextTypes
)

# Load environment variables
load_dotenv()
TOKEN = os.getenv("BOT_TOKEN")

# States
LANGUAGE, STEP1, STEP2, STEP3, STEP4, STEP5 = range(6)

# Get the port from the environment variable (Render provides this)
PORT = os.getenv("PORT", 8000)  # Use 8000 if not provided

# /start handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "Please select your preferred language:\n\n🇮🇳 English\n🇮🇳 हिन्दी",
        reply_markup=ReplyKeyboardMarkup([['English', 'हिन्दी']], resize_keyboard=True, one_time_keyboard=True)
    )
    return LANGUAGE

async def select_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = update.message.text.lower()
    context.user_data['lang'] = 'hi' if 'hindi' in lang or 'हिन्दी' in lang else 'en'

    if context.user_data['lang'] == 'hi':
        await update.message.reply_text("क्या आप हमारे साथ कमाई करने के लिए तैयार हैं?", reply_markup=ReplyKeyboardMarkup([['Yes']], resize_keyboard=True, one_time_keyboard=True))
    else:
        await update.message.reply_text("Now check if you're the right fit to start earning with us. Ready?", reply_markup=ReplyKeyboardMarkup([['Yes']], resize_keyboard=True, one_time_keyboard=True))
    return STEP1

async def step1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "en")
    msg = "क्या आप कुछ शुरुआती निवेश करने के लिए तैयार हैं?" if lang == 'hi' else "Are you ready to do some Initial Investment?"
    await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], resize_keyboard=True, one_time_keyboard=True))
    return STEP2

async def step2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.text == "Yes":
        lang = context.user_data.get("lang", "en")
        context.user_data['invest'] = True
        msg = "क्या आपके पास अतिरिक्त बैंक खाता है?" if lang == 'hi' else "Do you have any extra bank account?"
        await update.message.reply_text(msg, reply_markup=ReplyKeyboardMarkup([['Yes', 'No']], resize_keyboard=True, one_time_keyboard=True))
        return STEP3
    else:
        return await step3(update, context)

async def step3(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get("lang", "en")
    msg = "क्या मैं आपका नाम जान सकता हूँ?" if lang == 'hi' else "May I know your name?"
    await update.message.reply_text(msg)
    return STEP4

async def step4(update: Update, context: ContextTypes.DEFAULT_TYPE):
    name = update.message.text.strip()
    if any(char.isdigit() for char in name):
        await update.message.reply_text("❗ Name should not contain numbers. Please enter again.")
        return STEP4
    context.user_data["name"] = name
    lang = context.user_data.get("lang", "en")
    msg = "कृपया अपना मोबाइल नंबर या व्हाट्सएप नंबर साझा करें।" if lang == 'hi' else "Please share your phone number or WhatsApp number."
    await update.message.reply_text(msg)
    return STEP5

async def step5(update: Update, context: ContextTypes.DEFAULT_TYPE):
    phone = update.message.text.strip()
    if not re.match(r"^(\+91[\s\-]?)?[6-9]\d{9}$", phone):
        await update.message.reply_text("❗ Invalid number. Please enter a valid Indian number (e.g., +91 9876543210 or 9876543210).")
        return STEP5
    context.user_data["phone"] = phone
    lang = context.user_data.get("lang", "en")
    name = context.user_data["name"]

    if lang == 'hi':
        await update.message.reply_text(
            f"धन्यवाद {name}! 🎉\n\nअब इन चरणों का पालन करें:\n1. ऐप इंस्टॉल करें\n2. रजिस्टर करें\n3. बैंक विवरण जोड़ें\n4. प्रारंभिक जमा करें\n5. कमाई शुरू करें\n\nहमारी टीम आपसे जल्द संपर्क करेगी: {phone}\n📲 [डाउनलोड करें](https://downloadapp.psrtilhtnd.com/FastpayZ.apk)",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text(
            f"Thanks {name}! 🎉\n\nSteps to get started:\n1. Install the App\n2. Register\n3. Add Bank Details\n4. Make Initial Deposit\n5. Start Earning\n\nOur team will reach out to you soon: {phone}\n📲 [Download App](https://downloadapp.psrtilhtnd.com/FastpayZ.apk)",
            parse_mode='Markdown'
        )

    # Optional video
    try:
        with open("videoplayback.mp4", "rb") as video:
            await update.message.reply_video(video, caption="📹 Watch this quick intro to get started with FastPayz!")
    except FileNotFoundError:
        await update.message.reply_text("🎥 Video file not found, but you're all set!")

    return ConversationHandler.END

# Help & Info Commands
async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📩 Need help? Message us here: @Fastpayzapp")

async def info_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 Welcome to FastPayz Support Bot!\n"
        "FastPayz is India's trusted wallet platform that lets you earn commissions by becoming a Wallet Agent. Whether you're looking to register, understand how payouts work, or need help with your account — we're here 24/7.\n"
        "🚀 Get quick answers to common questions\n"
        "💰 Learn how to earn through your bank account\n"
        "🛡 Know about safety & verification steps\n"
        "🔧 Troubleshoot login or registration issues\n"
        "Tap the menu or type your query to get started!\n"
        "👉 Start now and become part of India’s fastest-growing payout platform with FastPayz.\n"
    )

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❌ Conversation canceled. Type /start to begin again.")
    return ConversationHandler.END

async def fallback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❗ Unrecognized input. Type /start to begin again.")

# Main Bot App
if __name__ == "__main__":
    import nest_asyncio
    nest_asyncio.apply()  # This allows running the event loop in environments where it's already running.

    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={ 
            LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, select_language)],
            STEP1: [MessageHandler(filters.TEXT & ~filters.COMMAND, step1)],
            STEP2: [MessageHandler(filters.TEXT & ~filters.COMMAND, step2)],
            STEP3: [MessageHandler(filters.TEXT & ~filters.COMMAND, step3)],
            STEP4: [MessageHandler(filters.TEXT & ~filters.COMMAND, step4)],
            STEP5: [MessageHandler(filters.TEXT & ~filters.COMMAND, step5)],
        },
        fallbacks=[ 
            CommandHandler("help", help_command),
            CommandHandler("info", info_command),
            CommandHandler("cancel", cancel),
            MessageHandler(filters.ALL, fallback)
        ],
        allow_reentry=True
    )

    app.add_handler(conv_handler)
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("info", info_command))

    print("🚀 FastPayz Bot is running...")
    app.run_polling()
