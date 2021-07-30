from repository.base_repository import BaseRepository
from app.models.models import Item


class ItemRepository(BaseRepository):
    @staticmethod
    async def insert(item: Item):
        if item.id is None:
            await item.save()

    @staticmethod
    async def update(item: Item):
        pass

    @staticmethod
    async def select(item_id: int):
        pass

    @staticmethod
    async def delete(item_id: int):
        pass
