from pony.orm import db_session, flush
from repository.base_repository import BaseRepository
from app.models.models import Owner


class OwnerRepository(BaseRepository):
    @staticmethod
    def insert(owner: Owner):
        if owner.id is None:
            with db_session:
                owner
                flush()
                return owner.id

    @staticmethod
    def update(owner: Owner):
        if owner.id is not None:
            with db_session:
                owner

    @staticmethod
    def select(owner_id: int):
        return Owner.get(id=owner_id)

    @staticmethod
    def delete(owner_id: int,):
        with db_session:
            owner = Owner.get(id=owner_id)
            owner.delete()
