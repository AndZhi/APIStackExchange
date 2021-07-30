from repository.base_repository import BaseRepository
from app.models.models import Tag


class TagRepository(BaseRepository):
    @staticmethod
    async def insert(tag: Tag):
        if tag.id is None:
            await tag.save()

    @staticmethod
    async def update(tag: Tag):
        pass

    @staticmethod
    async def select(tag_id: int):
        pass

    @staticmethod
    async def delete(tag_id: int):
        pass
