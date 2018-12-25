import functools
import os

import telebot

from text_templates import example
from utils import cache

bot = telebot.TeleBot(os.environ.get('token'))


def is_admin(func):
    @functools.wraps(func)
    def wrapper(message):
        administrators = [x.user.id for x in bot.get_chat_administrators(message.chat.id)]
        print(message.from_user.id, administrators)
        if message.from_user.id in administrators:
            return func(message)
    return wrapper


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text=example, parse_mode='Markdown')


@bot.message_handler(commands=['accept'], func=lambda m: m.reply_to_message)
@is_admin
def accept_order(message):
    if message.reply_to_message.forward_from:
        bot.forward_message(chat_id='@tgram_jobs', from_chat_id=message.chat.id,
                            message_id=message.reply_to_message.message_id)
        bot.send_message(chat_id=message.reply_to_message.forward_from.id, text='Ваша заявка опубликована.')


@bot.message_handler(commands=['delete'], func=lambda m: m.reply_to_message)
@is_admin
def delete_order(message):
    reason = message.text.split(maxsplit=1)
    info_message = reason[1] if len(reason) > 1 else 'Без указания причины.'
    if message.reply_to_message.forward_from:
        bot.delete_message(
            message.chat.id, message.reply_to_message.message_id)
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(chat_id=message.reply_to_message.forward_from.id,
                         text=f'Ваша заявка удалена.\n{info_message}')


@bot.message_handler(content_types=['text', 'photo', 'video', 'document'], func=lambda m: m.chat.type == 'private')
def take_order(message):
    expire = cache(message.from_user.id)
    if not expire:
        bot.forward_message(chat_id=-1001299756866, from_chat_id=message.chat.id,
                            message_id=message.message_id)
        bot.send_message(chat_id=message.chat.id, text='Заявка принята.')
    else:
        bot.send_message(chat_id=message.chat.id, text=f'Подождите {expire} секунд прежде чем опять отправить заявку.')


if __name__ == '__main__':
    bot.polling(none_stop=True, timeout=13371488)
