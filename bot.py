import telebot
from engine import *


class Wash(Action):
    def __init__(self, timestamp=time.time()):
        super().__init__(timestamp)
        self.rate = 20
        self.icon = '💧'


class Throw(Action):
    def __init__(self, timestamp=time.time()):
        super().__init__(timestamp)
        self.rate = 25
        self.icon = '🏃'


class PutOut(Action):
    def __init__(self, timestamp=time.time()):
        super().__init__(timestamp)
        self.rate = 5
        self.icon = '🗑'


class Buy(Action):
    def __init__(self, timestamp=time.time()):
        super().__init__(timestamp)
        self.rate = 20
        self.icon = '🛒'


class Craft(Action):
    def __init__(self, timestamp=time.time()):
        super().__init__(timestamp)
        self.rate = 5
        self.icon = '🥤'


class Carry(Action):
    def __init__(self, timestamp=time.time()):
        super().__init__(timestamp)
        self.rate = 10
        self.icon = '🛍'


channels = {
    'main': {
        'token': '495959130:AAFVxttJodzYYDe6fqjk-dWsSbqhVstbcpw',
        'supergroup': -1001093228903
    },
    'experimental': {
        'token': '480724884:AAEXMoK5nqwz2rUOWexp35XIG681Y9GQcok',
        'supergroup': -1001272011188
    }
}

current_channel = 'experimental'
bot = telebot.TeleBot(channels[current_channel]['token'])
chat = channels[current_channel]['supergroup']

MENTORS = ['Беленькая', 'Кудряшка', 'Черненькая']
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

DISPLAY_LIMIT = 10


room = Storage('test/bot.yaml', 'test/bot.yaml')
room.load()

randomize = {'time': time.time(), 'message': None, 'user': None}


def get_nightmare():
    today = datetime.date.today()
    new_year = datetime.date(datetime.date.today().year, 1, 1)
    shift = room.data.get('nightmare_shift', 0)
    return ((today - new_year).days + shift) % len(MENTORS)


@bot.message_handler(commands=['help'])
def handle_help(message):
    if message.chat.id == channels[current_channel]['supergroup']:
        bot.send_message(message.chat.id,
                         f'*Бот комнатный*\n_Версия ядра: {version}_',
                         parse_mode='Markdown')


@bot.message_handler(commands=['dashboard'])
def handle_dashboard(message):
    if message.chat.id == channels[current_channel]['supergroup']:
        d = room['users']
        m = str()

        today = datetime.date.today()
        weekday = WEEKDAYS[datetime.date.weekday(today)]
        total_score = sum([item.balance for item in d.values()])
        middle_score = total_score / len(d)

        m = f'''{today.day} {MONTHS[today.month - 1]} ({weekday})
*Ночная воспетка*: _{MENTORS[get_nightmare()]}_
_Счёт комнаты: {total_score}_\n
'''
        for user in sorted(d.values(), key=lambda x: len(x.actions_list)):
            m += f'*{user.name}*: {badge_count(user.actions_list)}'
            m += '\n'
        m += '\n'
        for user in sorted(d.values(), key=lambda x: x.balance):
            m += f'*{user.name}*: {user.balance}'
            m += '\n'

        m += f'`Мидлскор по комнате: {middle_score}`'
        bot.send_message(message.chat.id,
                         m,
                         parse_mode='Markdown')


@bot.message_handler(commands=['wash'])
def handle_action(message):
    if message.from_user.id in room['users'].keys():
        room['users'][message.from_user.id].add_action(Wash(message.date))
        room.save()


@bot.message_handler(commands=['throw'])
def handle_action(message):
    if message.from_user.id in room['users'].keys():
        room['users'][message.from_user.id].add_action(Throw(message.date))
        room.save()


@bot.message_handler(commands=['put_out'])
def handle_action(message):
    if message.from_user.id in room['users'].keys():
        room['users'][message.from_user.id].add_action(PutOut(message.date))
        room.save()


@bot.message_handler(commands=['buy'])
def handle_action(message):
    if message.from_user.id in room['users'].keys():
        room['users'][message.from_user.id].add_action(Buy(message.date))
        room.save()


@bot.message_handler(commands=['craft'])
def handle_action(message):
    if message.from_user.id in room['users'].keys():
        room['users'][message.from_user.id].add_action(Craft(message.date))
        room.save()


@bot.message_handler(commands=['carry'])
def handle_action(message):
    if message.from_user.id in room['users'].keys():
        room['users'][message.from_user.id].add_action(Carry(message.date))
        room.save()


@bot.message_handler(commands=['challenge'])
def handle_board(message):
    if message.from_user.id in room['users'].keys():
        if room['board'].title is not None:
            m = f'*{room["board"].title}:*'
        else:
            m = '*Доступные челленджи:*'
        bot.send_message(message.chat.id,
                         m,
                         parse_mode='Markdown')
        if len(room['board']):
            for goal in room['board'].values():
                timestamp = datetime.datetime.fromtimestamp(goal.timestamp).strftime("%H:%M:%S %d.%m.%Y")
                m = f'*{goal.title}*\n_Награда: {goal.rate}_\nСоздано: {timestamp}'
                bot.send_message(message.chat.id,
                                 m,
                                 parse_mode='Markdown')
        else:
            bot.send_message(message.chat.id,
                             '_К сожалению, лист челленджей пуст!_',
                             parse_mode='Markdown')
        keyboard = telebot.types.InlineKeyboardMarkup()
        button = telebot.types.InlineKeyboardButton(
            text=f'Добавить челлендж',
            callback_data=f'AC')
        keyboard.add(button)
        bot.send_message(message.chat.id,
                         "*Вы всегда можете объявить свой челлендж:*",
                         reply_markup=keyboard,
                         parse_mode='Markdown')


@bot.message_handler(commands=['admin'])
def handle_kick_ass(message):
    if message.chat.id == channels[current_channel]['supergroup']:
        if room['users'][message.from_user.id].is_admin:
            keyboard = telebot.types.InlineKeyboardMarkup()
            i = 0
            actions = list()

            for user in room['users'].values():
                for item in user.actions_list.values():
                    actions.append((item, user.id))
                    actions.sort(key=lambda x: x[0].timestamp)

            while i < DISPLAY_LIMIT and i < len(actions):
                item = actions[-i - 1]
                timestamp = datetime.datetime.fromtimestamp(item[0].timestamp).strftime("%H:%M:%S %d.%m.%Y")
                button = telebot.types.InlineKeyboardButton(
                    text=f'{item[0].icon} — {room["users"][item[1]].name} ({timestamp})',
                    callback_data=f'M{item[0].id}.{item[1]}')
                keyboard.add(button)
                i += 1
            mentor_switch = telebot.types.InlineKeyboardButton(
                text='Сменить ночную воспетку',
                callback_data='NM')
            custom_action = telebot.types.InlineKeyboardButton(
                text='Присвоить экшн',
                callback_data='CA'
            )
            hide = telebot.types.InlineKeyboardButton(
                text='Спрятать меню',
                callback_data='HM'
            )
            keyboard.add(mentor_switch)
            keyboard.add(custom_action)
            keyboard.add(hide)

            bot.send_message(message.chat.id,
                             "Админ-панель для бати комнаты.\nВыберите элемент для удаления:",
                             reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: len(call.data) and call.data[0] == 'M')
def callback_inline(call):
    action_id, user_id = map(int, call.data[1:].split('.'))
    if room['users'][call.from_user.id].is_admin:
        fine = room['users'][call.from_user.id].actions_list[action_id].rate * (1 + FINE_TAX / 100)
        room['users'][user_id].del_action(action_id)
        room.save()
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text=f'*Экшн был удалён!*\nШтраф для пользователя {room["users"][user_id].name} составил {fine}.',
                              parse_mode='Markdown')
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="У вас недостаточно прав!")


@bot.callback_query_handler(func=lambda call: len(call.data) >= 2 and call.data[:2] == 'NM')
def callback_inline(call):
    if room['users'][call.from_user.id].is_admin:
        if len(call.data) == 2:
            keyboard = telebot.types.InlineKeyboardMarkup()
            for i, item in enumerate(MENTORS):
                button = telebot.types.InlineKeyboardButton(
                    text=f'{item}',
                    callback_data=f'NM{i}')
                keyboard.add(button)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text='Какая воспетка пришла сегодня?',
                                  reply_markup=keyboard)
        else:
            index = int(call.data[2:])
            room['nightmare_shift'] = (index - len(MENTORS) + 1) % len(MENTORS)
            room.save()
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text='Новая воспетка установлена!')
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="У вас недостаточно прав!")


@bot.callback_query_handler(func=lambda call: len(call.data) >= 2 and call.data[:2] == 'CA')
def callback_inline(call):
    if room['users'][call.from_user.id].is_admin:
        if len(call.data) == 2:
            keyboard = telebot.types.InlineKeyboardMarkup()
            for item in room['users'].values():
                button = telebot.types.InlineKeyboardButton(text=f'{item.name}', callback_data=f'CA.{item.id}')
                keyboard.add(button)
            bot.edit_message_text(chat_id=call.message.chat.id,
                                  message_id=call.message.message_id,
                                  text="Отправьте эмоджи и цену через пробел, затем выберите получателя",
                                  reply_markup=keyboard)
        else:
            if event_listener is not None and room['users'][event_listener.from_user.id].is_admin:
                date = event_listener.date
                m = event_listener.text
                if len(m) and len(m.split()) == 2:
                    m = m.split()
                    emoji = m[0]
                    try:
                        rate = int(m[1])
                    except ValueError:
                        bot.edit_message_text(chat_id=call.message.chat.id,
                                              message_id=call.message.message_id,
                                              text="Что-то пошло не так!")
                    else:
                        user = int(call.data.split('.')[1])
                        room['users'][user].add_action(CustomAction(rate, emoji, date))
                        room.save()
                        bot.edit_message_text(chat_id=call.message.chat.id,
                                              message_id=call.message.message_id,
                                              text="Экшн добавлен!")
    else:
        bot.edit_message_text(chat_id=call.message.chat.id,
                              message_id=call.message.message_id,
                              text="У вас недостаточно прав!")


event_listener = None


@bot.message_handler(content_types=["text"])
def handle_event_listener(message):
    global event_listener
    event_listener = message


if __name__ == '__main__':
    t1 = threading.Thread(target=bot.polling, args=(True, ))
    # t2 = threading.Thread(target=display_table)

    t1.start()
    # t2.start()

    t1.join()
    # t2.join()
