import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes
from flask import Flask, request

# Bot konfiguratsiyasi
BOT_TOKEN = "8256115743:AAELBRqA1tFinwkS2siFvzx9Tyv_WGs8z1M"
ADMIN_LINK = "https://t.me/Sheyxxbet"
CHANNEL_LINK = "https://t.me/+mKIJqJKfyg01MTgy"

app = Flask(__name__)

# Log sozlash
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Start komandasi
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("Menga yozing", url=ADMIN_LINK)],
        [InlineKeyboardButton("Otzivlar", callback_data="reviews")],
        [InlineKeyboardButton("Programma qanday ishlaydi?", callback_data="how_it_works")],
        [InlineKeyboardButton("VIP Kanal", callback_data="vip_channel")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    start_text = """Salom mening ismim **SHEYX**

Men oddiy oiladan chitgan oyiga 1 - 1.5 mln som oladigan ishchi edim. Astronaut oynab yutqazish jonga tegdi va bu haqida izlanib shu oyinni KAMCHILIKLARINI topdim. Endi oddiy menga oxshaganlarga yordan beraman.

Siz ham menga oxshab pul ishlashingiz kelsa menga yozing."""
    
    await update.message.reply_text(
        start_text,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# Callback handler
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == "reviews":
        review_text = f"""Bot ni 3 kunga tekinga olish uchun shaxsiy kodingizni oling

3 kun bepul programma olish uchun menga AA3394 deb yozing 🟧
{ADMIN_LINK}"""
        
        keyboard = [[InlineKeyboardButton("Bot ni olish", url=ADMIN_LINK)]]
        await query.edit_message_text(review_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "how_it_works":
        how_text = f"""Sizda kuniga 1 soat bosh vahtiz bolsa boldi
Va siz 100 000 som dan qiynalmasdan 2 - 3 million qila olasiz
TEZROQ YOZING!

"Bot" deb yozing men sizga 3 000 000 so'm tez orada ishlashni orgataman
{ADMIN_LINK}"""
        
        keyboard = [[InlineKeyboardButton("Programmani olish", callback_data="get_program")]]
        await query.edit_message_text(how_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "get_program":
        program_text = f"""Bot ni 3 kunga tekinga olish uchun shaxsiy kodingizni olish

3 kun bepul programma olish uchun menga AA3394 deb yozing 🟧
{ADMIN_LINK}"""
        
        keyboard = [
            [InlineKeyboardButton("3 kun bepul kodini olish", callback_data="free_code")],
            [InlineKeyboardButton("Bot ni olish", url=ADMIN_LINK)]
        ]
        await query.edit_message_text(program_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "free_code":
        free_code_text = f"""3 kun bepul programma olish uchun menga AA3394 deb yozing 🟧
{ADMIN_LINK}"""
        
        keyboard = [[InlineKeyboardButton("Bot ni olish", url=ADMIN_LINK)]]
        await query.edit_message_text(free_code_text, reply_markup=InlineKeyboardMarkup(keyboard))
    
    elif query.data == "vip_channel":
        vip_text = f"""Atabek VIP
maxfiy kanal

Atabek bn pul topish
Eng oson pul topish yollarini orgataman hammasi haqqonly va organish bepul

{CHANNEL_LINK}"""
        
        await query.edit_message_text(vip_text, parse_mode='Markdown')

@app.route('/')
def home():
    return "🤖 Bot ishlayapti!"

@app.route('/webhook', methods=['POST'])
async def webhook():
    try:
        application = app.config['telegram_app']
        json_data = await request.get_json()
        update = Update.de_json(json_data, application.bot)
        await application.process_update(update)
        return 'ok'
    except Exception as e:
        logging.error(f"Webhook error: {e}")
        return 'error', 500

async def main():
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    # Webhook sozlash
    webhook_url = f"https://{os.environ.get('RENDER_SERVICE_NAME', 'sheyx-bot')}.onrender.com/webhook"
    await application.bot.set_webhook(webhook_url)
    app.config['telegram_app'] = application
    
    logging.info(f"🤖 Bot ishga tushdi! Webhook: {webhook_url}")

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=False)
