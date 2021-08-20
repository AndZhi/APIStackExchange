from pony.orm import db_session, flush
from repository.base_repository import BaseRepository
from app.models.models import Tag


class TagRepository(BaseRepository):
    @staticmethod
    def insert(tag: Tag):
        if tag.id is None:
            with db_session:
                tag
                flush()
                return tag.id

    @staticmethod
    def update(tag: Tag):
        if tag.id is not None:
            with db_session:
                tag

    @staticmethod
    def select(tag_id: int):
        return Tag.get(id=tag_id)

    @staticmethod
    def delete(tag_id: int,):
        with db_session:
            tag = Tag.get(id=tag_id)
            tag.delete()
