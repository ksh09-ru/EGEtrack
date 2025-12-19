import openai #ИИ
from aiogram import Bot, Dispatcher, executor, types #основные компоненты aiogram
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton #для кнопок
from config import BOT_TOKEN, OPENAI_API_KEY #токен бота и аи
from database import add_user, update_field, get_user #функции для бд

# НАСТРОЙКИ 

openai.api_key = OPENAI_API_KEY #ключ аи

bot = Bot(token=BOT_TOKEN) #бот + его ключ
dp = Dispatcher(bot) #опред функции и их вывод

# состояние пользователя
user_state = {} # словарь для хранения инф, полученной от пользователя

# КНОПКИ

main_keyboard = ReplyKeyboardMarkup( # создание кнопок и их располож
    keyboard=[
        [KeyboardButton("📅 Расписание"), KeyboardButton("📘 Предметы")],
        [KeyboardButton("❗ Слабые задания")],
        [KeyboardButton("🧠 Получить план")]
    ],
    resize_keyboard=True # размер кнопок в зависимости от размера экрана
)

# ИИ(пока не работает(из-за бд))

def generate_plan(schedule, subjects, weak):
    prompt = f""" # запрос к ИИ
Ты помощник по подготовке к ЕГЭ.

Обязательные условия:
- Ученик ходит в школу
- Нужен отдых и хобби
- Нельзя перегружать

Расписание:
{schedule}

Предметы:
{subjects}

Слабые задания:
{weak}

Составь подробный недельный план подготовки.
"""

    try:
        response = openai.ChatCompletion.create( #запрос в ИИ
            model="gpt-3.5-turbo", #модель
            messages=[{"role": "user", "content": prompt}], #сообщение для ИИ
            timeout=30 #время на работу ии
        )
        return response["choices"][0]["message"]["content"] #вывод ответа ИИ пользователю

    except Exception:
        return "⚠️ Ошибка при генерации плана. Попробуй позже." #если не сработало

# КОМАНДЫ

@dp.message_handler(commands=["start"]) #декоратор функции старт
async def start(message: types.Message):
    add_user(message.from_user.id) #добавление пользователя в бд
    await message.answer( 
        "👋 Привет! Я ExamsTrack - бот для подготовки к ЕГЭ.\n\n"
        "Выбери действие с помощью кнопок 👇",
        reply_markup=main_keyboard
    ) #приветственный текст и вывод кнопок(функций)

# КНОПКИ

@dp.message_handler(text="📅 Расписание") 
async def schedule_btn(message: types.Message):
    user_state[message.from_user.id] = "schedule" #обновление "расписание" в бд
    await message.answer(
        "📅 Отправь своё расписание одним сообщением.\n\n"
        "Пример:\n"
        "Пн–Пт школа 8:30–15:00\n"
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
        "Математика - задание 13"
    )

@dp.message_handler(text="🧠 Получить план")
async def plan_btn(message: types.Message):
    data = get_user(message.from_user.id) #получение данных пользователя из бд

    if not data or not data["schedule"] or not data["subjects"]: #проверка на наличие заполненного бд
        await message.answer(
            "⚠️ Не хватает данных.\n\n"
            "Сначала заполни:\n"
            "📅 Расписание\n"
            "📘 Предметы"
        )
        return

    await message.answer("⏳ Составляю план...") 

    plan = generate_plan( #передача данных из бд ИИ
        data["schedule"],
        data["subjects"],
        data["weak_topics"] or "нет"
    )

    await message.answer(plan) #отправка плана пользователю 

# СOХРAНЕНИЕ ДАННЫX

@dp.message_handler(content_types=types.ContentType.TEXT)
async def save_data(message: types.Message):
    uid = message.from_user.id
    text = message.text

    # игнорируем кнопки и команды (для бд)
    if text.startswith("/") or text in [
        "📅 Расписание",
        "📘 Предметы",
        "❗ Слабые задания",
        "🧠 Получить план"
    ]:
        return

    if uid not in user_state:
        await message.answer("ℹ️ Сначала выбери действие кнопками")
        return

    state = user_state[uid]

    if state == "schedule":
        update_field(uid, "schedule", text)
        await message.answer("✅ Расписание сохранено")

    elif state == "subjects":
        update_field(uid, "subjects", text)
        await message.answer("✅ Предметы сохранены")

    elif state == "weak":
        update_field(uid, "weak_topics", text)
        await message.answer("✅ Слабые задания сохранены")

    user_state.pop(uid)

# ЗАПУСК 

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)