from pony.orm import db_session, flush, select
from repository.base_repository import BaseRepository
from app.models.models import Item


class ItemRepository(BaseRepository):
    @staticmethod
    def insert(item: Item):
        if item.id is None:
            with db_session:
                item
                flush()
                return item.id

    @staticmethod
    def update(item: Item):
        if item.id is not None:
            with db_session:
                item

    @staticmethod
    def select(item_id: int):
        return Item.get(id=item_id)

    @staticmethod
    def delete(item_id: int,):
        with db_session:
            item = Item.get(id=item_id)
            item.delete()

    @staticmethod
    def get_items(request_id: int):
        with db_session:
            return list(Item.select(i for i in Item if i.request == request_id))
