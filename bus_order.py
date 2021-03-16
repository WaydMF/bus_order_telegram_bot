import logging
import os
import time

import telebot

from order import Order


logger = telebot.logger
telebot.logger.setLevel(logging.DEBUG)

bot = telebot.TeleBot(os.getenv("TELEGRAM_BOT_API"))
keyboard_cities = telebot.types.ReplyKeyboardMarkup(True, True)
keyboard_cities.row("Минск", "Ошмяны")


@bot.message_handler(commands=["start"])
def first_order_message(message, *args, **kwargs):
    user_language = message.from_user.language_code
    order = Order(user_language)
    msg = bot.send_message(message.chat.id, "Привет, выберите город отправления, пожалуйста.",
                           reply_markup=keyboard_cities)
    bot.register_next_step_handler(msg, get_city_from, order)


@bot.message_handler(content_types=["text"])
def hello_message_handler(message, *args, **kwargs):
    hello_options = ["прив", "привет", "здравствуй", "здравствуйте", "хей", "ghbdtn", "hi", "hello"]
    if message.text.strip().lower() in hello_options:
        first_order_message(message)
    else:
        bot.send_message(message.chat.id, "Для запуска функционала бота поздоровайтесь с ним.")


def get_city_from(message, order, *args, **kwargs):
    if message.text not in order.city_mapping.keys():
        msg = bot.send_message(message.chat.id, "Данного города нет в списке. Введите, пожалуйста, "
                                                "правильный город.",
                               reply_markup=keyboard_cities)
        bot.register_next_step_handler(msg, get_city_from, order)
        return
    order.city_from = message.text
    msg = bot.send_message(message.chat.id, "Выберите город прибытия, пожалуйста.",
                           reply_markup=keyboard_cities)
    bot.register_next_step_handler(msg, get_city_to, order)


def get_city_to(message, order, *args, **kwargs):
    if message.text not in order.city_mapping.keys():
        msg = bot.send_message(message.chat.id, "Данного города нет в списке. Введите, пожалуйста, "
                                                "правильный город.",
                               reply_markup=keyboard_cities)
        bot.register_next_step_handler(msg, get_city_to, order)
        return
    if order.city_from == message.text:
        order.city_from = None
        order.city_to = None
        msg = bot.send_message(message.chat.id, "Города отправления и прибытия должны различаться! "
                                                "Выберите город отправления.",
                               reply_markup=keyboard_cities)
        bot.register_next_step_handler(msg, get_city_from, order)
    else:
        order.city_to = message.text
        msg = bot.send_message(message.chat.id, "Введите дату в формате \"дд.мм.гггг\", пожалуйста")
        bot.register_next_step_handler(msg, get_date, order)


def get_date(message, order, *args, **kwargs):
    try:
        raw_msg = message.text.strip()
        day, month, year = raw_msg.split('.')
        if len(day) == 1:
            day = f"0{day}"
        if len(month) == 1:
            month = f"0{month}"
        raw_msg = f"{day}.{month}.{year}"
        time.strptime(raw_msg, '%d.%m.%Y')
    except ValueError:
        msg = bot.send_message(message.chat.id, "Проверьте правильность введённой даты и введите "
                                                "подходящую, пожалуйста.\n"
                                                "P.S. В формате \"дд.мм.гггг\"")
        bot.register_next_step_handler(msg, get_date, order)
        return

    order.date = raw_msg
    info = order.get_info()
    if not info:
        info = "Информации по текущей дате в данный момент нет."
    msg = bot.send_message(message.chat.id, info)


def unexpected_text_received():
    pass


if __name__ == '__main__':
    bot.polling(timeout=60)
