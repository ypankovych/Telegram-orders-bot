import os
import telebot
from utils import cache
from text_templates import example

bot = telebot.TeleBot(os.environ.get('token'))
moderators = []


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, text=example, parse_mode='Markdown')


@bot.message_handler(commands=['accept'], func=lambda m: m.reply_to_message)
def accept_order(message):
    if message.reply_to_message.forward_from and message.from_user.id in moderators:
        bot.forward_message(chat_id='@tgram_jobs', from_chat_id=message.chat.id,
                            message_id=message.reply_to_message.message_id)
        bot.send_message(
            chat_id=message.reply_to_message.forward_from.id, text='Ваша заявка опубликована.')


@bot.message_handler(commands=['delete'], func=lambda m: m.reply_to_message)
def delete_order(message):
    reason = message.text.split(maxsplit=1)
    if len(reason) > 1 and message.reply_to_message.forward_from and message.from_user.id in moderators:
        bot.delete_message(
            message.chat.id, message.reply_to_message.message_id)
        bot.delete_message(message.chat.id, message.message_id)
        bot.send_message(
            chat_id=message.reply_to_message.forward_from.id, text=f'Ваша заявка удалена.\n{reason[1]}')


@bot.message_handler(content_types=['text', 'photo', 'video', 'document'])
def take_order(message):
    if message.chat.type == 'private':
        if cache(message.from_user.id):
            bot.forward_message(chat_id=-, from_chat_id=message.chat.id,
                                message_id=message.message_id)
            bot.send_message(chat_id=message.chat.id, text='Заявка принята.')
        else:
            bot.send_message(chat_id=message.chat.id, text='Между заявками должно пройти хотябы 5 минут.')


if __name__ == '__main__':
    bot.polling(none_stop=True)
