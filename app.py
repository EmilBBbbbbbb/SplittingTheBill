import asyncio

import logging
import os
import re
from findi_total_cost import  final
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram import F
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

TOKEN = '7797972820:AAGZGsZSXzvJuR-1t0kxjF5BfTlxpkWWTwE'
bot = Bot(token=TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)



# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[
        logging.FileHandler("bot_errors.log"),
        logging.StreamHandler()
    ]
)


class FeedbackState(StatesGroup):
    waiting_for_feedback = State()
    waiting_for_photo = State()


class MemberState(StatesGroup):
    waiting_for_member = State()


# Кнопки
upload_button = KeyboardButton(text='📸 Загрузить чек')

greet_kb = ReplyKeyboardMarkup(
    keyboard=[
        [upload_button]
    ],
    resize_keyboard=True,
    input_field_placeholder='Выберите пункт меню'
)

members_button = InlineKeyboardButton(text="По количеству гостей", callback_data="members")
keyboard = InlineKeyboardMarkup(inline_keyboard=[
    [members_button]
])


@dp.message(Command('start'))
async def start_command(message: types.Message):
    await message.answer("Привет! Я помогу тебе разделить счет.")
    await message.answer("Загрузи фотографию чека, и я предложу тебе удобные варианты разделения.",
                         reply_markup=greet_kb)


@dp.message(F.text == '📸 Загрузить чек')
async def request_photo(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, загрузите фотографию чека.")
    await state.set_state(FeedbackState.waiting_for_photo)


@dp.message(FeedbackState.waiting_for_photo, F.photo)
async def handle_photo(message: types.Message, state: FSMContext):
    photo = message.photo[-1]
    file_id = photo.file_id
    file = await bot.get_file(file_id)
    file_path = f'images/{file.file_path.split("/")[-1]}'

    await bot.download_file(file.file_path, file_path)
    await message.answer("Спасибо! Чек загружен. Теперь вы можете продолжить.")
    await message.answer("выберите удобный вариант разделения", reply_markup=keyboard)
    await state.clear()


@dp.callback_query(F.data == "members")
async def members(callback_query: types.CallbackQuery, state: FSMContext):
    await callback_query.message.answer('Введите количество посетителей')
    await state.set_state(MemberState.waiting_for_member)


@dp.message(MemberState.waiting_for_member)
async def func_member(message: types.Message, state: FSMContext):
    try:
        # Проверяем, что введено число
        members_count = int(message.text)

        if members_count <= 0:
            await message.answer("Число должно быть больше 0. Введите корректное количество.")
            return

        try:
            # Проверяем существование папки
            if not os.path.exists('images'):
                await message.answer("Папка с чеками не найдена. Загрузите чек сначала.")
                return

            files = os.listdir('images')

            # Проверяем, что папка не пуста
            if not files:
                await message.answer("Нет загруженных чеков. Загрузите чек сначала.")
                return

            # Сортируем файлы по времени изменения (новые сначала)
            files.sort(key=lambda x: os.path.getmtime(os.path.join('images', x)), reverse=True)
            last_file = files[0]  # Берем самый новый файл
            file_path = os.path.join('images', last_file)

            print(f"Обрабатываем файл: {file_path}")  # Отладочная информация

            # Получаем общую стоимость
            total_cost = float(final(file_path))
            print(f"Распознанная сумма: {total_cost}")  # Отладочная информация

            if total_cost <= 0:
                await message.answer("Не удалось распознать сумму в чеке. Попробуйте загрузить чек снова.")
                return

            # Рассчитываем стоимость на человека
            cost_per_person = total_cost / members_count

            # Формируем сообщение с результатами
            result_message = (
                f"Общая стоимость: {total_cost:.2f}₽\n"
                f"Количество гостей: {members_count}\n\n"
            )

            for i in range(1, members_count + 1):
                result_message += f"Гость {i} — {cost_per_person:.2f}₽\n"

            await message.answer(result_message)

        except Exception as e:
            logging.error(f"Ошибка при обработке чека: {str(e)}", exc_info=True)
            await message.answer("Произошла ошибка при обработке чека. Попробуйте еще раз.")

    except ValueError:
        await message.answer("Пожалуйста, введите число (например: 2, 3, 4).")
    finally:
        await state.clear()

async def main():
    print('Бот запущен')
    await dp.start_polling(bot)


if __name__ == '__main__':
    asyncio.run(main())