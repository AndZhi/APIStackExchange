from repository.base_repository import BaseRepository
from app.models.models import Request, Item
from tortoise.query_utils import Prefetch


class RequestRepository(BaseRepository):
    @staticmethod
    async def insert(request: Request):
        if request.id is None:
            await request.save()

    @staticmethod
    async def update(request: Request):
        if request.id is not None:
            await request.save()

    @staticmethod
    async def select(request_id: int, line_quantity: int):
        return await Request.filter(id=request_id).prefetch_related(
            Prefetch('items', queryset=Item.all().order_by('-creation_date').limit(line_quantity))).first()

    @staticmethod
    async def delete(request):
        await request.delete()

    @staticmethod
    async def check_request(search_string: str):
        return await Request.filter(request_string=search_string.lower()).first().prefetch_related('items')

    @staticmethod
    async def get_all_request(line_quantity: int):
        return await Request.all().order_by('-date').limit(line_quantity)
