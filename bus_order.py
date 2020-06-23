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
order = Order()


@bot.message_handler(commands=["start"])
def first_order_message(message):
    msg = bot.send_message(message.chat.id, "Привет, выберите город отправления, пожалуйста.",
                           reply_markup=keyboard_cities)
    bot.register_next_step_handler(msg, get_city_from)


@bot.message_handler(content_types=["text"])
def hello_message_handler(message):
    hello_options = ["прив", "привет", "здравствуй", "здравствуйте", "хей", "ghbdtn", "hi", "hello"]
    if message.text.strip().lower() in hello_options:
        first_order_message(message)


def get_city_from(message):
    if message.text not in order.city_mapping.keys():
        msg = bot.send_message(message.chat.id, "Данного города нет в списке. Введите, пожалуйста, "
                                                "правильный город.",
                               reply_markup=keyboard_cities)
        bot.register_next_step_handler(msg, get_city_from)
        return
    order.city_from = message.text
    msg = bot.send_message(message.chat.id, "Выберите город прибытия, пожалуйста.",
                           reply_markup=keyboard_cities)
    bot.register_next_step_handler(msg, get_city_to)


def get_city_to(message):
    if message.text not in order.city_mapping.keys():
        msg = bot.send_message(message.chat.id, "Данного города нет в списке. Введите, пожалуйста, "
                                                "правильный город.",
                               reply_markup=keyboard_cities)
        bot.register_next_step_handler(msg, get_city_to)
        return
    if order.city_from == message.text:
        order.city_from = None
        order.city_to = None
        msg = bot.send_message(message.chat.id, "Города отправления и прибытия должны различаться!"
                                                "Выберите город отправления.",
                               reply_markup=keyboard_cities)
        bot.register_next_step_handler(msg, get_city_from)
    else:
        order.city_to = message.text
        msg = bot.send_message(message.chat.id, "Введите дату в формате \"дд.мм.гггг\", пожалуйста")
        bot.register_next_step_handler(msg, get_date)


def get_date(message):
    try:
        raw_msg = message.text.strip()
        time.strptime(raw_msg, '%d.%m.%Y')
        if len(raw_msg) != 10:  # date format 04.04.2020 contain 10 symbols HARDCODE!!!
            raise ValueError
    except ValueError:
        msg = bot.send_message(message.chat.id, "Проверьте правильность введённой даты и введите "
                                                "подходящую, пожалуйста.\n"
                                                "P.S. В формате \"дд.мм.гггг\"")
        bot.register_next_step_handler(msg, get_date)
        return
    order.date = message.text
    response = order.get_info()
    if not response:
        response = "Информации по текущей дате в данный момент нет."
    bot.send_message(message.chat.id, response)


def unexpected_text_received():
    pass


if __name__ == '__main__':
    bot.polling(timeout=60)
