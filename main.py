
import asyncio
import json
import logging
import os
from datetime import datetime
from aiogram import Bot, Dispatcher, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils import exceptions
from fastapi import FastAPI, Request
from mangum import Mangum

# ========== CONFIG ==========
BOT_TOKEN = "8256115743:AAELBRqA1tFinwkS2siFvzx9Tyv_WGs8z1M"
ADMIN_ID = 6493383873
WEBHOOK_PATH = "/webhook"
PORT = int(os.environ.get("PORT", 8000))

USERS_FILE = "users.json"
SETTINGS_FILE = "settings.json"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
app = FastAPI()

# ========== LOAD / SAVE ==========
def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f, indent=4)

def load_settings():
    default = {
        "start_text": "Salom mening ismim **SHEYX**. Siz ham menga yozing.",
        "reviews_text": "Botni 3 kunga tekin olish uchun promo kod: AA3394",
        "how_text": "Siz kuniga 1 soat vaqtingiz bo‘lsa pul ishlashingiz mumkin.",
        "vip_text": "Atabek VIP maxfiy kanal: https://t.me/+mKIJqJKfyg01MTgy",
        "admin_link": "https://t.me/Sheyxxbet",
        "vip_link": "https://t.me/+mKIJqJKfyg01MTgy",
        "promo_code": "AA3394",
        "mandatory_sub": False,
        "bot_status": True
    }
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, "r") as f:
            data = json.load(f)
            default.update(data)
    return default

def save_settings(settings):
    with open(SETTINGS_FILE, "w") as f:
        json.dump(settings, f, indent=4)

users = load_users()
settings = load_settings()

# ========== HELPER FUNCTIONS ==========
def is_admin(user_id):
    return user_id == ADMIN_ID

def user_exists(user_id):
    return str(user_id) in users

def add_user(user: types.User):
    if not user_exists(user.id):
        users[str(user.id)] = {
            "username": user.username,
            "first_name": user.first_name,
            "start_time": datetime.now().isoformat()
        }
        save_users(users)

# ========== START COMMAND ==========
@dp.message_handler(commands=["start"])
async def start_handler(message: types.Message):
    add_user(message.from_user)
    if not settings["bot_status"]:
        return await message.answer("Bot hozir o‘chirilgan.")
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Menga yozing", url=settings["admin_link"]),
        InlineKeyboardButton("Otzivlar", callback_data="reviews"),
        InlineKeyboardButton("Programma qanday ishlaydi?", callback_data="how_it_works"),
        InlineKeyboardButton("VIP Kanal", callback_data="vip_channel")
    )
    await message.answer(settings["start_text"], reply_markup=kb, parse_mode="Markdown")

# ========== CALLBACK QUERIES ==========
@dp.callback_query_handler()
async def callback_handler(query: types.CallbackQuery):
    add_user(query.from_user)
    data = query.data

    if data == "reviews":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Botni olish", url=settings["admin_link"]))
        await query.message.edit_text(settings["reviews_text"], reply_markup=kb, parse_mode="Markdown")

    elif data == "how_it_works":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Programmani olish", callback_data="get_program"))
        await query.message.edit_text(settings["how_text"], reply_markup=kb, parse_mode="Markdown")

    elif data == "get_program":
        kb = InlineKeyboardMarkup()
        kb.add(
            InlineKeyboardButton("3 kun bepul kodini olish", callback_data="free_code"),
            InlineKeyboardButton("Botni olish", url=settings["admin_link"])
        )
        await query.message.edit_text(settings["reviews_text"], reply_markup=kb, parse_mode="Markdown")

    elif data == "free_code":
        kb = InlineKeyboardMarkup()
        kb.add(InlineKeyboardButton("Botni olish", url=settings["admin_link"]))
        await query.message.edit_text(f"3 kun bepul programma olish uchun promo kod: {settings['promo_code']}", reply_markup=kb, parse_mode="Markdown")

    elif data == "vip_channel":
        await query.message.edit_text(settings["vip_text"] + f"\n\n{settings['vip_link']}", parse_mode="Markdown")

# ========== ADMIN PANEL ==========
@dp.message_handler(lambda m: is_admin(m.from_user.id), commands=["admin"])
async def admin_panel(message: types.Message):
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("Statistika", callback_data="admin_stats"),
        InlineKeyboardButton("Reklama jo‘natish", callback_data="admin_broadcast"),
        InlineKeyboardButton("Sozlamalar", callback_data="admin_settings"),
        InlineKeyboardButton("Botni ON/OFF", callback_data="admin_toggle")
    )
    await message.answer("Admin panel:", reply_markup=kb)

# ============================
# Webhook endpoint for Render
# ============================
@app.post("/webhook")
async def webhook(req: Request):
    data = await req.json()
    update = types.Update(**data)
    await dp.process_update(update)
    return {"ok": True}

# ============================
# Startup / Shutdown
# ============================
@app.on_event("startup")
async def on_startup():
    await bot.set_webhook(f"https://{os.environ.get('RENDER_SERVICE_NAME','sheyx-bot')}.onrender.com/webhook")
    logging.info("Webhook o‘rnatildi.")

@app.on_event("shutdown")
async def on_shutdown():
    await bot.delete_webhook()
    logging.info("Bot o‘chmoqda...")

handler = Mangum(app)
