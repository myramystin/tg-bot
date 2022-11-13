import telebot as telebot
from telebot import types
import requests
from datetime import datetime

TOKEN = '5758333321:AAGUFuqY864Mtfy9Yo9ZCF1ERZVOeNV2gTQ'
bot = telebot.TeleBot(TOKEN)

question_ids = dict()


def get_exchange_rate(code1: str, code2: str) -> float:
    print(code1, code2)
    today = datetime.now()
    iso_date = today.isoformat()
    url = "https://www.sf-international.com/sf-service-owf-web/" \
          "service/exrate?lang=en&region=ru&translate=&time=" + \
          str(iso_date).split(".")[0].replace(":", "%3A") + \
          "%2B03%3A00" + f"&originCode={code1}&destCode={code2}".format(code1=code1,
                                                                        code2=code2)
    response = requests.get(url)
    print(code1, code2, response.text)
    return float(response.text)


@bot.message_handler(commands=['opts', "clear_all"])
def button_message(message):
    markup = types.InlineKeyboardMarkup(row_width=4)
    item_1 = types.InlineKeyboardButton("статс", callback_data="stats")
    markup.row(item_1)
    item_2 = types.InlineKeyboardButton("кикнуть меня(",
                                        callback_data="leave_chat")
    markup.row(item_2)
    item_3 = types.InlineKeyboardButton("Самопромоут",
                                        callback_data="promote_myself")
    markup.row(item_3)
    item_4 = types.InlineKeyboardButton("курс валют", callback_data="currency")
    markup.row(item_4)
    bot.send_message(message.chat.id, 'Выбирай',
                     reply_markup=markup)


@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    currencies = ['CNY', 'EUR', 'GBP', 'KRW',
                  'USD', 'JPY',  'RUB', 'CAD']
    currencies_names = ['Китайский юань', 'Евро', 'Фунт стерлингов',
                        'Вон Республики Корея',
                        'Доллар США', 'Иена', 'Российский рубль',
                        'Канадский доллар']
    if call.message:
        if call.data == 'promote_myself':
            chat_id = call.message.chat.id
            user_id = call.message.from_user.id
            bot.promote_chat_member(chat_id, user_id, can_change_info=True,
                                    can_invite_users=True,
                                    can_delete_messages=True,
                                    can_restrict_members=True,
                                    can_pin_messages=True,
                                    can_promote_members=True,
                                    can_manage_chat=True,
                                    can_manage_video_chats=True,
                                    can_manage_voice_chats=True)
        if call.data == 'stats':
            markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
            num_members = bot.get_chat_members_count(call.message.chat.id)
            admins = bot.get_chat_administrators(call.message.chat.id)
            flag1 = "всего" if len(admins) < num_members - len(
                admins) else "целых"
            flag2 = "админов" if len(admins) > 4 else "админа"
            flag2 = "админ" if len(admins) == 1 else flag2
            bot.send_message(call.message.chat.id,
                             f"в чате {num_members} пользователей и {flag1} "
                             f"{len(admins)} {flag2}",
                             reply_markup=markup)
            bot.answer_callback_query(call.id, 'Successful')
        if call.data == 'leave_chat':
            bot.leave_chat(call.message.chat.id)
        if call.data == 'currency':
            markup = types.InlineKeyboardMarkup(row_width=len(currencies))
            for [idx, code] in enumerate(currencies):
                item = types.InlineKeyboardButton(currencies_names[idx],
                                                  callback_data="CURR_1." + code)
                markup.row(item)
            bot.send_message(call.message.chat.id, "выбери первую валюту",
                             reply_markup=markup)
        if call.data.startswith("CURR_1."):
            markup = types.InlineKeyboardMarkup(row_width=len(currencies))
            for [idx, code] in enumerate(currencies):
                # CURR_2.VAL2.CURR_1.VAL1
                item = types.InlineKeyboardButton(currencies_names[idx],
                                                  callback_data= "CURR_2."
                                                  + code + "." + call.data)
                markup.row(item)
            bot.send_message(call.message.chat.id, "выбери вторую валюту",
                             reply_markup=markup)
        if call.data.startswith("CURR_2."):
            print(call.data)
            curr1 = call.data.split(".")[3]
            curr2 = call.data.split(".")[1]
            curr = "{:3f}".format(get_exchange_rate(curr1, curr2))
            bot.send_message(call.message.chat.id, f"курс "
                                                   f"{currencies_names[currencies.index(curr1)]} "
                                                   f"к {currencies_names[currencies.index(curr2)]} "
                                                   f"равен {curr}")


@bot.message_handler(content_types=['new_chat_members'])
def new_member(message):
    user_name = message.new_chat_members[0].first_name
    user_handle = message.new_chat_members[0].username
    msg = bot.send_message(message.chat.id,
                     'привет-привет, {0}! 2 + 2 * 2 = ? '
                     '(жду ответ в реплае)'.format(user_name))
    question_ids[msg.id] = user_handle


def new_member_answer(message):
    try:
        num = int(message.text)
        if num == 6:
            bot.send_message(message.chat.id, 'хорооош')
        else:
            bot.send_message(message.chat.id, 'мимо')
    except ValueError:
        bot.send_message(message.chat.id, 'че-то совсем мимо')
        return
    question_ids.pop(message.reply_to_message.id)


@bot.message_handler(content_types=["text"])
def filter_of_answers(message):
    if message.reply_to_message is not None:
        if message.reply_to_message.id in question_ids and \
                question_ids[message.reply_to_message.id] == \
                message.from_user.username:
            new_member_answer(message)


@bot.message_handler(commands=['restrict'])
def restrict_member(message: [telebot.types.Message]):
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    bot.restrict_chat_member(chat_id, user_id)


@bot.message_handler(commands=['unrestrict'])
def unrestrict_member(message: [telebot.types.Message]):
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    bot.restrict_chat_member(chat_id, user_id,
                             can_send_messages=True,
                             can_send_media_messages=True,
                             can_send_other_messages=True,
                             can_add_web_page_previews=True,
                             can_send_polls=True,
                             can_change_info=True)


@bot.message_handler(commands=['ban'])
def ban_user(message: [telebot.types.Message]):
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    bot.kick_chat_member(chat_id, user_id)


@bot.message_handler(commands=['unban'])
def unban_user(message: [telebot.types.Message]):
    chat_id = message.chat.id
    user_id = message.reply_to_message.from_user.id
    bot.unban_chat_member(chat_id, user_id)


@bot.message_handler(commands=['help'])
def help_message(message):
    bot.send_message(message.chat.id, "привет-привет!\n"
                                      "я бот, который поможет тебе управлять"
                                      " чатом. помимо этого могу скинуть курс"
                                      " валют\n"
                                      "вот список моих команд:\n"
                                      "/opts - показать меню\n"
                                      "/ban - забанить пользователя\n"
                                      "/unban - разбанить пользователя\n"
                                      "/restrict - ограничить пользователя\n"
                                      "/unrestrict - снять ограничения с "
                                      "пользователя\n"
                                      "/help - показать это сообщение\n")


if __name__ == '__main__':
    try:
        bot.polling(none_stop=True, interval=0)
    except Exception as e:
        print(e)
