import os
import re
from dotenv import load_dotenv
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.fsm import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

load_dotenv()
bot = Bot(token=os.getenv("BOT_TOKEN"))
dp = Dispatcher()

class Diary(StatesGroup):
    emotion = State()
    event = State()
    thought = State()

emotion_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="😞 Тревога"), KeyboardButton(text="😭 Стыд")],
        [KeyboardButton(text="😐 Пустота"), KeyboardButton(text="🤬 Злость")],
        [KeyboardButton(text="😔 Вина")]
    ],
    resize_keyboard=True
)

skills = {
    "тревога": "🌬️ Дыши квадратом: 4с вдох → 4с задержка → 4с выдох → 4с задержка. 5 раз.",
    "стыд": "🧊 Опусти лицо в холодную воду на 15 секунд или зажми кубик льда.",
    "пустота": "💧 Сделай микро-действие: выпей глоток воды или умойся.",
    "злость": "🦵 10 прыжков на месте или 2 минуты быстрой ходьбы.",
    "вина": "🗣️ Скажи вслух 3 раза: 'Я сделал ошибку, а не я ошибка'."
}

def detect_distortion(text):
    t = text.lower()
    if "всегда" in t or "никогда" in t:
        return "⚠️ Сверхобобщение ('всегда/никогда')"
    if "должен" in t or "надо" in t or "обязан" in t:
        return "⚠️ Долженствование ('я должен')"
    if "ужасно" in t or "кошмар" in t or "всё пропало" in t:
        return "⚠️ Катастрофизация ('это ужасно')"
    if "подумают" in t or "решат" in t or "наверняка" in t:
        return "⚠️ Чтение мыслей ('они подумают')"
    return "✅ Мысль без явных искажений"

@dp.message(Command("start"))
async def start(msg: types.Message, state: FSMContext):
    await state.clear()
    await msg.answer(
        "🧠 Я дневник эмоций. За 3 шага разберёмся, почему плохо.\n\n"
        "👉 Какая эмоция сейчас главная?",
        reply_markup=emotion_kb
    )
    await state.set_state(Diary.emotion)

@dp.message(Diary.emotion)
async def get_emotion(msg: types.Message, state: FSMContext):
    emotion = msg.text.strip()
    await state.update_data(emotion=emotion)
    await msg.answer(
        "📋 Что случилось? Напиши событие коротко.",
        reply_markup=types.ReplyKeyboardRemove()
    )
    await state.set_state(Diary.event)

@dp.message(Diary.event)
async def get_event(msg: types.Message, state: FSMContext):
    await state.update_data(event=msg.text)
    await msg.answer("💭 Какая мысль пронеслась в голове? Напиши.")
    await state.set_state(Diary.thought)

@dp.message(Diary.thought)
async def get_thought(msg: types.Message, state: FSMContext):
    thought = msg.text
    data = await state.get_data()
    emotion = data.get("emotion", "")
    
    skill = skills.get("пустота")
    for key in skills:
        if key in emotion.lower():
            skill = skills[key]
            break
    
    distortion = detect_distortion(thought)
    
    await msg.answer(
        f"🔍 {distortion}\n\n"
        f"🧘 Навык на {emotion}:\n{skill}\n\n"
        f"Попробуй прямо сейчас. Напиши /start для новой записи."
    )
    await state.clear()

@dp.message(F.text)
async def fallback(msg: types.Message):
    await msg.answer("Напиши /start, чтобы начать.")

if __name__ == "__main__":
    dp.run_polling(bot)