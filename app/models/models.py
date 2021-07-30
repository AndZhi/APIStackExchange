from datetime import datetime
from pony.orm import *


db = Database()


class Item(db.Entity):
    id = PrimaryKey(int, auto=True)
    request = Required('Request')
    is_answered = Optional(bool)
    view_count = Optional(int)
    answer_count = Optional(int)
    score = Optional(int)
    last_activity_date = Optional(datetime)
    creation_date = Optional(datetime)
    last_edit_date = Optional(datetime)
    question_id = Optional(int)
    content_license = Optional(str, nullable=True)
    link = Optional(str, nullable=True)
    title = Optional(str, nullable=True)
    tags = Set('Tag')
    owners = Set('Owner')


class Owner(db.Entity):
    id = PrimaryKey(int, auto=True)
    account_id = Optional(int)
    reputation = Optional(int)
    user_id = Optional(int)
    user_type = Optional(str, nullable=True)
    accept_rate = Optional(int)
    profile_image = Optional(str, nullable=True)
    display_name = Optional(str, nullable=True)
    link = Optional(str, nullable=True)
    item = Required(Item)


class Tag(db.Entity):
    id = PrimaryKey(int, auto=True)
    value = Optional(str, nullable=True)
    item = Required(Item)


class Request(db.Entity):
    id = PrimaryKey(int, auto=True)
    date = Required(datetime)
    request_string = Required(str, unique=True, index='i_request_request_string')
    items = Set(Item)


class Response(object):
    def __init__(self, date: datetime, title: str, link: str):
        self.date = date
        self.title = title
        self.link = link
