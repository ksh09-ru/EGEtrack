import openai
from aiogram import Bot, Dispatcher, executor, types
from config import BOT_TOKEN, OPENAI_API_KEY
from database import add_user, update_field, get_user

openai.api_key = OPENAI_API_KEY

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(bot)


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
    await message.answer(
        "📅 Отправь своё расписание (одним сообщением).\n"
        "Пример:\n"
        "Понедельник 08:30-15:00 школа\n"
        "Понедельник 18:00-19:00 тренировка"
    )


@dp.message_handler(commands=["subjects"])
async def subjects(message: types.Message):
    await message.answer(
        "📘 Отправь предметы ЕГЭ.\n"
        "Пример:\n"
        "Математика профиль\nРусский\nИнформатика"
    )


@dp.message_handler(commands=["weak"])
async def weak(message: types.Message):
    await message.answer(
        "❗️ Отправь слабые задания.\n"
        "Пример:\n"
        "Математика: 13, 15\nРусский: 8, сочинение"
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


@dp.message_handler()
async def save_data(message: types.Message):
    text = message.text.lower()

    if "школа" in text or ":" in text:
        update_field(message.from_user.id, "schedule", message.text)
        await message.answer("✅ Расписание сохранено")
    elif "математика" in text or "русский" in text:
        update_field(message.from_user.id, "subjects", message.text)
        await message.answer("✅ Предметы сохранены")
    else:
        update_field(message.from_user.id, "weak_topics", message.text)
        await message.answer("✅ Слабые задания сохранены")


if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)