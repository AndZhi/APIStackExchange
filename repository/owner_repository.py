from repository.base_repository import BaseRepository
from app.models.models import Owner


class OwnerRepository(BaseRepository):
    @staticmethod
    async def insert(owner: Owner):
        if owner.id is None:
            await owner.save()

    @staticmethod
    async def update(owner: Owner):
        pass

    @staticmethod
    async def select(owner_id: int):
        pass

    @staticmethod
    async def delete(owner_id: int):
        pass
