import sqlite3 #импорт библиотеки 

conn = sqlite3.connect("examstrack.db") # создает файл с бд
cursor = conn.cursor() #SQL запросы и инфо из бд

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    user_id INTEGER PRIMARY KEY,
    schedule TEXT,
    subjects TEXT,
    weak_topics TEXT
)
""") #создание таблицы users и ее полей

conn.commit() #сохраняет изменения в бд


def add_user(user_id): # новый пользователь(добавление)
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)",
        (user_id,)
    ) #добавляет его в табл или ignore, если он уже там
    conn.commit() #сохр в бд


def update_field(user_id, field, value): #обновляет КОНКРЕТНОЕ поле
    cursor.execute(
        f"UPDATE users SET {field} = ? WHERE user_id = ?",
        (value, user_id)
    ) 
    conn.commit()


def get_user(user_id): #получение данных пользователя
    cursor.execute(
        "SELECT schedule, subjects, weak_topics FROM users WHERE user_id = ?",
        (user_id,)
    ) #запрос из бд расписания, предметов и слабых тем
    return cursor.fetchone()