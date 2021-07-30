from datetime import datetime
from tortoise import Model, fields


class Request(Model):
    id = fields.IntField(pk=True)
    date = fields.DatetimeField(null=True)
    request_string = fields.CharField(max_length=255, unique=True, index=True)

    items: fields.ReverseRelation['Item']

    def __str__(self):
        return self.name


class Item(Model):
    id = fields.IntField(pk=True)
    is_answered = fields.BooleanField()
    view_count = fields.IntField()
    answer_count = fields.IntField()
    score = fields.IntField()
    last_activity_date = fields.DatetimeField(null=True)
    creation_date = fields.DatetimeField(null=True)
    last_edit_date = fields.DatetimeField(null=True)
    question_id = fields.IntField()
    content_license = fields.TextField(null=True)
    link = fields.TextField(null=True)
    title = fields.TextField(null=True)
    request = fields.ForeignKeyField('models.Request', related_name='items')
    owner = fields.ForeignKeyField('models.Owner', related_name='items')

    tags: fields.ReverseRelation['Tag']

    def __str__(self):
        return self.name


class Owner(Model):
    id = fields.IntField(pk=True)
    account_id = fields.IntField(null=True)
    reputation = fields.IntField(null=True)
    user_id = fields.IntField(null=True)
    user_type = fields.TextField(null=True)
    accept_rate = fields.IntField(null=True)
    profile_image = fields.TextField(null=True)
    display_name = fields.TextField(null=True)
    link = fields.TextField(null=True)

    items: fields.ReverseRelation['Item']

    def __str__(self):
        return self.name


class Tag(Model):
    id = fields.IntField(pk=True)
    value = fields.TextField(null=True)
    item = fields.ForeignKeyField('models.Item', related_name='tags')

    def __str__(self):
        return self.name


class Response(object):
    def __init__(self, date: datetime, title: str, link: str):
        self.date = date
        self.title = title
        self.link = link
