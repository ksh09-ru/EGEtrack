import openai
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, OPENAI_API_KEY
from database import add_user, update_field, get_user

openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)
user_state = {}

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
    add_user(message.from_user.id)
    await message.answer(
        "👋 Привет! Я ExamsTrack.\n\n"
        "Я помогу составить план подготовки к ЕГЭ.\n\n"
        "Команды:\n"
        "/schedule — ввести расписание\n"
        "/subjects — предметы ЕГЭ\n"
        "/weak — слабые задания\n"
        "/plan — получить план"
    )


@dp.message_handler(commands=["schedule"])
async def schedule(message: types.Message):
    user_state[message.from_user.id] = "schedule"
    await message.answer(
    "📅 Отправь своё расписание одним сообщением.\n\n"
    "Пример:\n"
    "Пн–Пт: школа 8:30–15:00\n"
    "Пн: математика 16:00–17:30\n"
    "Ср: русский 16:00–17:30\n"
    "Сб: отдых, друзья"
)
                         
    


@dp.message_handler(commands=["subjects"])
async def subjects(message: types.Message):
    user_state[message.from_user.id] = "subjects"
    await message.answer(
    "📘 Отправь предметы, которые ты сдаёшь.\n\n"
    "Пример:\n"
    "Математика\nРусский\nИнформатика"
)
    


@dp.message_handler(commands=["weak"])
async def weak(message: types.Message):
    user_state[message.from_user.id] = "weak"
    await message.answer(
    "❗ Напиши задания, которые даются сложнее.\n\n"
    "Пример:\n"
    "Математика — задание 13\n"
    "Русский — задание 8\n"
    "Информатика — задачи на циклы"
)
    


@dp.message_handler(commands=["plan"])
async def plan(message: types.Message):
    user = get_user(message.from_user.id)

    if not user or not all(user):
        await message.answer("⚠️ Сначала введи расписание, предметы и слабые задания.")
        return

    schedule, subjects, weak = user
    await message.answer("⏳ Анализирую расписание и составляю план...")

    plan_text = generate_plan(schedule, subjects, weak)
    await message.answer(plan_text)


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