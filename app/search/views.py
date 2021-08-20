import aiohttp_jinja2
from app.services import stack_exchange_service


@aiohttp_jinja2.template("all_query.html")
async def all_query(request):
    data = request.query
    try:
        line_quantity = data['line_quantity']
    except Exception:
        line_quantity = 25
    list_items = await stack_exchange_service.get_requests(line_quantity=line_quantity)
    return {'data': list_items}


@aiohttp_jinja2.template("search.html")
async def search(request):
    pass


@aiohttp_jinja2.template("response.html")
async def response(request):
    data = request.query
    if data['search'] == '':
        return {'theme': data['search'], 'data': []}
    try:
        line_quantity = data['line_quantity']
    except Exception:
        line_quantity = 25
    list_items = await stack_exchange_service.search(search_string=data['search'], line_quantity=line_quantity)
    return {'theme': data['search'], 'data': list_items}
