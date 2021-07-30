import json
from datetime import datetime
from types import SimpleNamespace
from app.search import client
from repository import request_repository, owner_repository, item_repository, tag_repository
from app.models.models import Request, Item, Owner, Tag, Response
from logger import logger


async def get_requests(**kwargs):
    return await _get_all_requests(int(kwargs['line_quantity']))


async def search(**kwargs):
    search_string = kwargs['search_string']
    logger.info(f'search_string: {search_string}')
    try:
        data_json = await client.search(search_string)
    except Exception as e:
        logger.error(e)
    try:
        temp_object = json.loads(json.dumps(data_json), object_hook=lambda d: SimpleNamespace(**d))
    except Exception as e:
        logger.error(e)
    try:
        request = await _check_request(search_string)
        if request is not None:
            await _update_request(request, temp_object)
        else:
            request = Request(request_string=search_string.lower(), date=datetime.now())
            await request_repository.RequestRepository.insert(request)
            for i in temp_object.items:
                await _create_item(request, i)
    except Exception as e:
        logger.error(e)
    try:
        response = await _get_search_response(request.id, int(kwargs['line_quantity']))
    except Exception as e:
        logger.error(e)
    return response[:int(kwargs['line_quantity'])]


async def _get_all_requests(line_quantity: int):
    response = []
    requests = await request_repository.RequestRepository.get_all_request(line_quantity)
    for i in requests:
        response.append(Response(date=i.date.strftime('%d/%m/%Y-%H:%M:%S'), title=i.request_string,
                                 link=f'/response?search={i.request_string}&line_quantity=25'))
    return response


async def _get_search_response(request_id: int, line_quantity: int):
    response = []
    rq = await request_repository.RequestRepository.select(request_id, line_quantity)
    for i in rq.items:
        response.append(Response(date=i.creation_date.strftime('%d/%m/%Y-%H:%M:%S'), title=i.title, link=i.link))
    return response


async def _update_request(request, temp_object):
    links = []
    for i in request.items:
        links.append(i.link)
    for i in temp_object.items:
        if i.link not in links:
            await _create_item(request, i)


async def _check_request(search_string: str):
    check_request = await request_repository.RequestRepository.check_request(search_string)
    if check_request is not None:
        return check_request
    else:
        return None


async def _create_item(request, input_item):
    owner = Owner(account_id=_get_attribute(input_item.owner, 'account_id'),
                  reputation=_get_attribute(input_item.owner, 'reputation'),
                  user_id=_get_attribute(input_item.owner, 'user_id'),
                  user_type=_get_attribute(input_item.owner, 'user_type'),
                  accept_rate=_get_attribute(input_item.owner, 'accept_rate'),
                  profile_image=_get_attribute(input_item.owner, 'profile_image'),
                  display_name=_get_attribute(input_item.owner, 'display_name'),
                  link=_get_attribute(input_item.owner, 'link'))
    await owner_repository.OwnerRepository.insert(owner)

    item = Item(is_answered=_get_attribute(input_item, 'is_answered'),
                view_count=_get_attribute(input_item, 'view_count'),
                answer_count=_get_attribute(input_item, 'answer_count'),
                score=_get_attribute(input_item, 'score'),
                last_activity_date=_get_attribute_date(input_item, 'last_activity_date'),
                creation_date=_get_attribute_date(input_item, 'creation_date'),
                last_edit_date=_get_attribute_date(input_item, 'last_edit_date'),
                question_id=_get_attribute(input_item, 'question_id'),
                content_license=_get_attribute(input_item, 'content_license'),
                link=_get_attribute(input_item, 'link'),
                title=_get_attribute(input_item, 'title'),
                request_id=request.id,
                owner_id=owner.id
                )
    await item_repository.ItemRepository.insert(item)

    if input_item.tags is not None:
        for t in input_item.tags:
            tag = Tag(value=t, item_id=item.id)
            await tag_repository.TagRepository.insert(tag)

    owner = Owner(account_id=_get_attribute(input_item.owner, 'account_id'),
                  reputation=_get_attribute(input_item.owner, 'reputation'),
                  user_id=_get_attribute(input_item.owner, 'user_id'),
                  user_type=_get_attribute(input_item.owner, 'user_type'),
                  accept_rate=_get_attribute(input_item.owner, 'accept_rate'),
                  profile_image=_get_attribute(input_item.owner, 'profile_image'),
                  display_name=_get_attribute(input_item.owner, 'display_name'),
                  link=_get_attribute(input_item.owner, 'link'))
    await owner_repository.OwnerRepository.insert(owner)


def _get_attribute_date(obj, attribute_name):
    if hasattr(obj, attribute_name):
        return datetime.utcfromtimestamp(getattr(obj, attribute_name))
    else:
        return None


def _get_attribute(obj, attribute_name):
    if hasattr(obj, attribute_name):
        return getattr(obj, attribute_name)
    else:
        return None
