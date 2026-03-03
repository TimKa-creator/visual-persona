import os
import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message
import google.generativeai as genai
from google.api_core.exceptions import ResourceExhausted
from io import BytesIO
from dotenv import load_dotenv
import PIL.Image

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
API_KEYS_STR = os.getenv("GEMINI_API_KEY")
API_KEYS = API_KEYS_STR.split(',') if API_KEYS_STR else []

current_key_index = 0

def configure_genai():
    global current_key_index
    if not API_KEYS:
        logging.error("No API keys found in .env")
        return None
    
    key = API_KEYS[current_key_index]
    genai.configure(api_key=key)
    return genai.GenerativeModel('gemini-flash-latest')

model = configure_genai()

STYLIST_PROMPT = """
Ти професійний стиліст та іміджмейкер з досвідом роботи з персональним стилем та візуальною психологією.

Твоє завдання — проаналізувати зовнішність людини на наданому фото та зробити глибокий, практичний стилістичний розбір.
Пиши українською мовою, структуровано, конкретно, доброзичливо, але об’єктивно.

Уникай загальних фраз — формулюй рекомендації так, щоб їх можна було одразу застосувати.
Для структуризації використовуй емодзі.

ВАЖЛИВЕ ПРАВИЛО ФОРМАТУВАННЯ:
Абсолютно заборонено використовувати Markdown (текст або текст).
Ти ПОВИНЕН використовувати ТІЛЬКИ HTML-теги для форматування:
<b>жирний текст</b>, <i>курсив</i>, <u>підкреслений</u>.
Усі заголовки виділяй тегом <b>.

Зроби аналіз за такими пунктами:

<b>1️⃣ Форма обличчя</b>
Визнач форму (овал, квадрат, кругле, серце, прямокутне тощо) та опиши ключові пропорції й особливості.

<b>2️⃣ Кольоротип</b>
Визнач кольоротип (Зима, Весна, Літо, Осінь) з обґрунтуванням на основі тону шкіри, кольору очей і волосся.

<b>3️⃣ Тип фігури</b>
Проаналізуй тип фігури (пісочний годинник, прямокутник, трикутник, перевернутий трикутник, овал тощо), якщо її видно на фото.
Зазнач сильні сторони пропорцій та що варто підкреслювати в одязі.
Якщо фігуру не видно, ввічливо зазнач це.

<b>4️⃣ Рекомендації щодо зачіски</b>
Які стрижки, довжина та укладки найкраще підкреслять риси обличчя та загальний образ.
Також вкажи, яких рішень краще уникати.

<b>5️⃣ Рекомендації щодо макіяжу</b>
Проаналізуй риси обличчя та порадь тип макіяжу, який найкраще їх підкреслить (акценти, інтенсивність, стиль).
Зазнач, які зони варто виділяти, а що краще робити мінімально або уникати.
Рекомендації мають бути універсальними та придатними для повсякденного образу.

<b>6️⃣ Кольорова палітра в одязі</b>
Які кольори та відтінки освіжають образ, підкреслюють зовнішність, а яких краще уникати.

<b>7️⃣ Стильовий вектор (психотип)</b>
Визнач стильовий напрям або психотип (наприклад: класичний, драматичний, романтичний, натуральний, креативний тощо).
Опиши, який стиль одягу найкраще резонує з зовнішністю та внутрішнім вайбом.

<b>8️⃣ Асоціація з твариною</b>
На основі рис обличчя та загального враження визнач, з якою твариною асоціюється зовнішність людини
(наприклад: кішка, лисиця, олень, вовк, пантера тощо).
Поясни цю асоціацію через риси, міміку та вайб. Формулюй це легко, позитивно та метафорично.

<b>9️⃣ Оцінка “Vibe”</b>
Яке перше враження справляє зовнішність (впевнений, діловий, м’який, харизматичний, творчий тощо) і чому.

Тон аналізу — професійний, підтримуючий, без суб’єктивних оцінок “гарно/негарно”, лише стилістичні спостереження та рекомендації.
"""

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()

async def send_long_html_message(message: Message, text: str):
    max_len = 4000
    
    if len(text) <= max_len:
        await message.answer(text, parse_mode="HTML")
        return

    paragraphs = text.split('\n\n')
    current_chunk = ""

    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= max_len:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                await message.answer(current_chunk, parse_mode="HTML")
                await asyncio.sleep(0.3)
            current_chunk = paragraph + "\n\n"
            
    if current_chunk.strip():
        await message.answer(current_chunk, parse_mode="HTML")

@dp.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer(
        "Привіт! Я AI-стиліст 📸\n\n"
        "Надішли мені своє чітке фото (бажано в повний зріст або гарне селфі при денному світлі), "
        "і я зроблю детальний стилістичний розбір."
    )

@dp.message(F.photo)
async def handle_photo(message: Message):
    global current_key_index, model
    status_msg = await message.answer("⏳ Аналізую фото... Підбираю палітру та фасони. Це займе кілька секунд.")
    
    try:
        photo = message.photo[-1]
        file_io = BytesIO()
        
        file_info = await bot.get_file(photo.file_id)
        await bot.download_file(file_info.file_path, file_io)
        file_io.seek(0)

        image = PIL.Image.open(file_io)

        response = None
        attempts = 0
        max_attempts = len(API_KEYS)

        while attempts < max_attempts:
            try:
                response = await model.generate_content_async([STYLIST_PROMPT, image])
                break
            except ResourceExhausted:
                logging.warning(f"Key {current_key_index} exhausted. Switching...")
                current_key_index = (current_key_index + 1) % len(API_KEYS)
                model = configure_genai()
                attempts += 1
            except Exception as e:
                logging.error(f"Generation error: {e}")
                raise e

        if response:
            await status_msg.delete()
            await send_long_html_message(message, response.text)
        else:
            await status_msg.edit_text("😢 Всі доступні ключі вичерпано. Спробуйте пізніше.")

    except Exception as e:
        logging.error(f"Error: {e}")
        await status_msg.edit_text("😢 Виникла помилка під час аналізу або Telegram не зміг обробити форматування. Спробуй ще раз.")

async def main():
    print("Бот запущений...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(main())