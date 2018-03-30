import telebot
from yaml import load, dump
import time
import random
import datetime
from uuid import uuid4

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


class Storage:
    def __init__(self, import_path, export_path):
        self.import_path = import_path
        self.export_path = export_path
        self.data = None

    def load(self):
        with open(self.import_path, 'r', encoding='utf-8') as stream:
            source = load(stream, Loader=Loader)
        self.data = source

    def save(self):
        with open(self.export_path, 'w', encoding='utf-8') as stream:
            dump(self.data,
                 stream,
                 Dumper=Dumper,
                 allow_unicode=True,
                 default_flow_style=False)

    def add_action(self, action):
        self.data['actions'].append(action)
        self.data['user_scores'][action.boy] += action.price
        self.save()

    def del_action(self, id):
        if id in [i.id for i in room.data["actions"]]:
            index = [i.id for i in room.data["actions"]].index(id)
            author = self.data["actions"][index].boy
            price = self.data["actions"][index].price * 1.5
            self.data['user_scores'][author] -= price
            del room.data["actions"][index]
            self.save()
            return True
        return False


class Action:
    def __init__(self, user_id):
        self.created = int(time.time())
        self.boy = user_id
        self.icon = None
        self.id = str(uuid4().fields[-1])[:5]

    def __str__(self):
        return self.icon


class Wash(Action):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.price = 20
        self.icon = '🌊'


class Throw(Action):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.price = 25
        self.icon = '💩'


class PutOut(Action):
    def __init__(self, user_id):
        super().__init__(user_id)
        self.price = 5
        self.icon = '🗑'


token = '480724884:AAG56xG41QrObyjCSs8gEuhP0ioCLjyZbnA'
bot = telebot.TeleBot(token)

# CHAT = -1000000000000 # Supergroup ID
# MENTORS = ['Mentor 1', 'Mentor 2', 'Mentor 3']
# BOYS = {1234321: 'User 1',
#         1234321: 'User 2',
#         1234321: 'User 3',
#         1234321: 'User 4'}
# Users list id-int: 'name'-str
# DISPLAY_LIMIT = 10 # Manage screen display limit
# ADMIN_ID # Admin User ID

MONTHS = ['Января',
          'Февраля',
          'Марта',
          'Апреля',
          'Мая',
          'Июня',
          'Июля',
          'Августа',
          'Сентября',
          'Октября',
          'Ноября',
          'Декабря']

WEEKDAYS = ['Понедельник',
            'Вторник',
            'Среда',
            'Четверг',
            'Пятница',
            'Суббота',
            'Воскресенье']


room = Storage('data.yaml', 'data.yaml')
room.load()


def get_scores():
    result = f'_Счет комнаты — {sum(room.data["user_scores"].values())}_'
    data = list()
    for item in room.data['user_scores'].keys():
        data.append([BOYS[item], room.data["user_scores"][item]])
    for item in sorted(data, key=lambda x: x[1], reverse=True):
        result += f'\n*{item[0]}*: _{item[1]}_'
    result += f'\n_Мидлскор по комнате — {sum(room.data["user_scores"].values()) / len(BOYS):.4}_'
    return result


def get_actions():
    action_per_user = [[] for i in range(len(BOYS))]
    for action in room.data['actions']:
        action_per_user[list(BOYS.keys()).index(action.boy)].append(action.icon)
    result = str()
    for i in range(len(BOYS)):
        result += f'*{list(BOYS.values())[i]}*: {" ".join(action_per_user[i])}\n'
    return result


def get_nightmare():
    return MENTORS[(datetime.date.today() - datetime.date(datetime.date.today().year, 1, 1)).days % len(MENTORS)]


@bot.message_handler(commands=['wash'])
def handle_start_help(message):
    if message.from_user.id in BOYS.keys():
        room.add_action(Wash(message.from_user.id))


@bot.message_handler(commands=['throw'])
def handle_start_help(message):
    if message.from_user.id in BOYS.keys():
        room.add_action(Throw(message.from_user.id))


@bot.message_handler(commands=['put_out'])
def handle_start_help(message):
    if message.from_user.id in BOYS.keys():
        room.add_action(PutOut(message.from_user.id))


@bot.message_handler(commands=['actions'])
def handle_start_help(message):
    if message.from_user.id in BOYS.keys():
        m = bot.send_message(CHAT, get_actions(), parse_mode='Markdown')


@bot.message_handler(commands=['scores'])
def handle_start_help(message):
    if message.from_user.id in BOYS.keys():
        m = bot.send_message(CHAT, get_scores(), parse_mode='Markdown')


@bot.message_handler(commands=['nightmare'])
def handle_start_help(message):
    if message.from_user.id in BOYS.keys():
        bot.send_message(CHAT, get_nightmare(), parse_mode='Markdown')


@bot.message_handler(commands=['manage'])
def handle_start_help(message):
    if message.from_user.id == ADMIN_ID:
        keyboard = telebot.types.InlineKeyboardMarkup()
        i = 0
        while i < DISPLAY_LIMIT and i < len(room.data['actions']):
            item = room.data['actions'][-i-1]
            d = datetime.datetime.fromtimestamp(item.created).strftime("%H:%M:%S %d.%m.%Y")
            button = telebot.types.InlineKeyboardButton(text=f'{item.icon} — {BOYS[item.boy]} ({d})',
                                                        callback_data=item.id)
            keyboard.add(button)
            i += 1
        bot.send_message(message.chat.id, "Админ-панель для главного в комнате.\nВыберите элемент для удаления:", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_inline(call):
    if call.message:
        if call.from_user.id == ADMIN_ID:
            if room.del_action(call.data):
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Пыщь")
            else:
                bot.edit_message_text(chat_id=call.message.chat.id,
                                      message_id=call.message.message_id,
                                      text="Сорри, ошибочка")


if __name__ == '__main__':
    m = str()
    today = datetime.date.today()
    m += f'{today.day} {MONTHS[today.month - 1]} ({WEEKDAYS[datetime.date.weekday(today)]})'
    m += f'\n*Ночная воспетка*: _{get_nightmare()}_'
    m += f'\n\n{get_actions()}'
    m += f'\n{get_scores()}'
    m = bot.send_message(CHAT, m, parse_mode='Markdown')
    bot.pin_chat_message(CHAT,
                         m.message_id,
                         disable_notification=True)
    while True:
        try:
            bot.polling(none_stop=True)
        except Exception as err:
            time.sleep(5)
            print("Internet error!")
