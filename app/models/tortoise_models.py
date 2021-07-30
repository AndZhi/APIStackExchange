import datetime

from tortoise import Tortoise, fields, run_async
from tortoise.models import Model
from tortoise.utils import get_schema_sql


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

    owner: fields.ReverseRelation['Owner']
    tags: fields.ReverseRelation['Tag']

    def __str__(self):
        return self.name


class Owner(Model):
    id = fields.IntField(pk=True)
    account_id = fields.IntField()
    reputation = fields.IntField()
    user_id = fields.IntField()
    user_type = fields.IntField(null=True)
    accept_rate = fields.IntField()
    profile_image = fields.TextField(null=True)
    display_name = fields.TextField(null=True)
    link = fields.TextField(null=True)
    items = fields.ForeignKeyField('models.Item', related_name='owner')

    def __str__(self):
        return self.name


class Tag(Model):
    id = fields.IntField(pk=True)
    value = fields.TextField(null=True)
    item = fields.ForeignKeyField('models.Item', related_name='tags')

    def __str__(self):
        return self.name


async def run():
    print("\n\nPostgreSQL:\n")
    await Tortoise.init(
        db_url="postgres://postgres:11111@127.0.0.1:5400/TT_test", modules={"models": ["__main__"]}
    )
    await Tortoise.generate_schemas(safe=True)
    sql = get_schema_sql(Tortoise.get_connection("default"), safe=False)

    await insert()


async def insert():
    request = Request(date=datetime.datetime.now(),
                      request_string='asdasdasdd')
    await request.save()

    item = Item(is_answered=True,
                view_count=1,
                answer_count=1,
                score=1,
                last_activity_date=datetime.datetime.now(),
                creation_date=datetime.datetime.now(),
                last_edit_date=datetime.datetime.now(),
                question_id=1,
                content_license='asdasd',
                link='asd',
                title='asd',
                request_id=request.id)
    await item.save()

    tags = []
    tag = Tag(value='asd', item_id=item.id)
    tags.append(tag)
    for t in tags:
        await t.save()

    owner = Owner(account_id=1,
                  reputation=1,
                  user_id=1,
                  user_type=1,
                  accept_rate=1,
                  profile_image='asd',
                  display_name='asd',
                  link='asd',
                  items_id=item.id)
    await owner.save()

if __name__ == "__main__":
    run_async(run())
