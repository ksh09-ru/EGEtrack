import openai
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, OPENAI_API_KEY
from database import add_user, update_field, get_user
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
user_state = {}

main_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton("📅 Расписание"), KeyboardButton("📘 Предметы")],
        [KeyboardButton("❗ Слабые задания")],
        [KeyboardButton("🧠 Получить план")]
    ],
    resize_keyboard=True
)

def generate_plan(schedule, subjects, weak):
    prompt = f"""
Ты — помощник для подготовки к ЕГЭ.

Данные ученика (10 класс):

Расписание:
{schedule}

Предметы ЕГЭ:
{subjects}

Слабые задания:
{weak}

Задача:
Составь удобный недельный план подготовки к ЕГЭ.
Обязательно:
- учитывать школу
- учитывать отдых и хобби
- не более 2 часов учёбы подряд
- указывать номера заданий ЕГЭ
- рекомендовать задания из ФИПИ (без копирования)

Ответ дай в виде расписания по дням недели.
"""

    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["choices"][0]["message"]["content"]


@dp.message_handler(commands=["start"])
async def start(message: types.Message):
    await message.answer(
        "👋 Привет! Я ExamsTrack — бот для подготовки к ЕГЭ.\n\n"
        "Выбери действие с помощью кнопок 👇",
        reply_markup=main_keyboard
    )


@dp.message_handler(text="📅 Расписание")
async def schedule_btn(message: types.Message):
    user_state[message.from_user.id] = "schedule"
    await message.answer(
        "📅 Отправь своё расписание.\n\n"
        "Пример:\n"
        "Пн–Пт: школа 8:30–15:00\n"
        "Пн: математика 16:00–17:30"
    )
                         
    


@dp.message_handler(text="📘 Предметы")
async def subjects_btn(message: types.Message):
    user_state[message.from_user.id] = "subjects"
    await message.answer(
        "📘 Напиши предметы ЕГЭ.\n\n"
        "Пример:\n"
        "Математика\nРусский\nИнформатика"
    )
    


@dp.message_handler(text="❗ Слабые задания")
async def weak_btn(message: types.Message):
    user_state[message.from_user.id] = "weak"
    await message.answer(
        "❗ Напиши слабые задания.\n\n"
        "Пример:\n"
        "Математика — задание 13"
    )
    


@dp.message_handler(text="🧠 Получить план")
async def plan_btn(message: types.Message):
    user = get_user(message.from_user.id)
    await message.answer("⏳ Анализирую данные и составляю план...")
    
    data = get_user_data(message.from_user.id)
    plan = generate_plan(
        data["schedule"],
        data["subjects"],
        data["weak_topics"]
    )
    await message.answer(plan)

@dp.message_handler(content_types=types.ContentType.TEXT)
async def save_data(message: types.Message):
    uid = message.from_user.id

    if uid not in user_state:
        await message.answer("ℹ️ Используй команды: /schedule, /subjects, /weak или /plan")
        return

    state = user_state[uid]

    if state == "schedule":
        update_field(uid, "schedule", message.text)
        await message.answer("✅ Расписание сохранено")

    elif state == "subjects":
        update_field(uid, "subjects", message.text)
        await message.answer("✅ Предметы сохранены")

    elif state == "weak":
        update_field(uid, "weak_topics", message.text)
        await message.answer("✅ Слабые задания сохранены")

    user_state.pop(uid)

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)