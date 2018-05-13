from yaml import load, dump
import time
import random
import datetime
from uuid import uuid4
import threading

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:
    from yaml import Loader, Dumper


# Common consts
FINE_TAX = 50 # Штраф за удаление action
START_BILL = 10 # Начальный капитал


version = 0.1


class Storage:
    def __init__(self, import_path, export_path):
        self.import_path = import_path
        self.export_path = export_path
        self.data = dict()

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

    def __getitem__(self, item):
        return self.data[item]

    def __setitem__(self, key, value):
        self.data[key] = value


class User:
    def __init__(self, name, user_id, is_admin=False):
        self.name = name
        self.id = user_id
        self.__balance = float(START_BILL)
        self.is_admin = is_admin

        self.actions_list = dict()

    def add_action(self, action):
        self.actions_list[action.id] = action
        self.__balance += action.rate

    def del_action(self, action_id):
        if action_id in self.actions_list:
            fine = self.actions_list[action_id].rate * (1 + FINE_TAX / 100)
            self.actions_list.pop(action_id)
            self.__balance -= fine

    def send(self, other, value):
        if self.__balance + START_BILL >= value:
            self.__balance -= value
            other.balance += value

    def __str__(self):
        return f'{self.name} ({self.balance})'

    def __repr__(self):
        return f'{self.name} ({self.balance}, {self.actions_list})'

    @property
    def balance(self):
        return self.__balance

    @balance.getter
    def balance(self):
        return self.__balance

    @balance.setter
    def balance(self, value):
        self.__balance = value


class Action:
    def __init__(self, timestamp=time.time()):
        self.timestamp = int(timestamp)
        self.id = int(str(uuid4().fields[-1])[:5])

        self.icon = None
        self.rate = None

    def __str__(self):
        return self.icon

    def __repr__(self):
        return self.icon


class CustomAction(Action):
    def __init__(self, rate, icon, timestamp=time.time()):
        super().__init__(timestamp)
        self.rate = rate
        self.icon = icon


def badge_count(actions_list):
    recorded = dict()
    for item in actions_list.values():
        recorded[str(item)] = recorded.get(str(item), 0) + 1

    return ' '.join([f'{i}({recorded[i]})' for i in recorded.keys()])


class Board:
    def __init__(self, title=None):
        self.title = title
        self.agenda = dict()
        self.marked_as_done = 0

    def __getitem__(self, item):
        return self.agenda[item]

    def __setitem__(self, key, value):
        self.agenda[key] = value

    def __len__(self):
        return len(self.agenda)

    def pin_goal(self, goal):
        self.agenda[goal.id] = goal

    def unpin_goal(self, goal_id):
        if goal_id in self.agenda:
            self.agenda.pop(goal_id)

    def mark_as_done(self, goal_id, user):
        if goal_id in self.agenda:
            user.balance += self.agenda[goal_id].rate
            self.agenda.pop(goal_id)
            self.marked_as_done += 1


class Goal:
    def __init__(self, title, rate, description=None, timestamp=time.time()):
        self.title = title
        self.description = description

        self.timestamp = int(timestamp)
        self.done = None

        self.rate = rate
        self.id = int(str(uuid4().fields[-1])[:5])

    def is_done(self):
        return self.done is not None

    def mark_as_done(self, user, timestamp=time.time()):
        if not self.is_done():
            self.done = int(timestamp)
            user.balance += self.rate

    def reborn(self):
        if self.is_done():
            self.done = None

    def __str__(self):
        if self.is_done():
            return f'[V] {self.title}'
        else:
            return f'[ ] {self.title}'

    def __repr__(self):
        return self.title
