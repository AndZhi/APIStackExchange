from pony.orm import db_session, flush
from repository.base_repository import BaseRepository
from app.models.models import Request


class RequestRepository(BaseRepository):
    @staticmethod
    def insert(request: Request):
        if request.id is None:
            with db_session:
                request
                flush()
                return request.id

    @staticmethod
    def update(request: Request):
        if request.id is not None:
            with db_session:
                request

    @staticmethod
    def select(request_id: int):
        return Request.get(id=request_id)

    @staticmethod
    def delete(request_id: int):
        with db_session:
            request = Request.get(id=request_id)
            request.delete()

    @staticmethod
    def check_request(search_string: str):
        with db_session:
            requests = list(Request.select(lambda r: r.request_string.lower() == search_string.lower()))
            if requests:
                return requests[0].id
            else:
                return None

    @staticmethod
    def get_all_request():
        with db_session:
            requests = list(Request.select(lambda x: x))
            return requests
