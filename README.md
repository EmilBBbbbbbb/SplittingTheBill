# SplittingTheBill
# Разделение чека с помощью Telegram-бота и OCR (pytesseract)

Этот проект представляет собой Telegram-бота, который обрабатывает фотографии чеков, извлекает текст с помощью OCR (pytesseract) и разделяет общую сумму между гостями.

## Функционал

[*] Прием фотографий чеков от пользователей
[*] Автоматическое распознавание текста на изображении
[*] Поиск общей суммы в распознанном тексте
[*] Разделение суммы между указанными участниками
[*] Отправка результатов пользователю
## Технологии

Python 3.12
python - aiogram для работы с Telegram API
pytesseract и opencv-python для обработки изображений и OCR
re для регулярных выражений
## Установка и настройка

Установите зависимости:
bash
Copy
pip install python-telegram-bot pytesseract opencv-python
Установите Tesseract OCR
app.py
## Использование

1 - Отправьте боту фотографию чека
2 - Бот обработает изображение и найдет общую сумму
3 - Укажите, на сколько человек нужно разделить сумму
4 - Получите результат с суммой для каждого участника

## Пример использования

