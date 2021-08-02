import json
from datetime import datetime
from datetime import timedelta
from types import SimpleNamespace
import pytz

import aioredis

from app.models.models import Request, Item, Owner, Tag, Response
from app.search import client
from config_manager import redis_config
from logger import logger
from repository import request_repository, owner_repository, item_repository, tag_repository


def init_redis():
    global red
    red = aioredis.Redis(host=redis_config.host,
                         port=redis_config.port,
                         db=redis_config.db,
                         password=redis_config.password,
                         socket_timeout=redis_config.socket_timeout)


init_redis()


async def get_requests(**kwargs):
    return await _get_all_requests(int(kwargs['line_quantity']))


async def search(**kwargs):
    search_string = kwargs['search_string'].lower()
    line_quantity = int(kwargs['line_quantity'])
    logger.info(f'search_string: {search_string}')
    response = []
    try:
        if await red.exists(search_string) == 1:
            data = _get_temp_object(json.loads(await red.get(search_string)))
            response = _get_response(data)
    except Exception as e:
        logger.error(e)
    if len(response) != 0:
        return response[:line_quantity]

    data_json = await client.search(search_string)
    await red.setex(search_string.lower(),
                    timedelta(minutes=redis_config.ttl_timeout),
                    json.dumps(data_json))
    temp_object = None
    try:
        temp_object = _get_temp_object(data_json)
    except Exception as e:
        logger.error(e)
    request = None
    try:
        request = await _check_request(search_string)
        if request is not None:
            await _update_request(request, temp_object)
        else:
            request = Request(request_string=search_string.lower(), date=datetime.now(pytz.utc))
            await request_repository.RequestRepository.insert(request)
            for i in temp_object.items:
                await _create_item(request, i)
        logger.info('Данные получены и записаны в базу.')
    except Exception as e:
        logger.error(e)
    try:
        response = await _get_response_from_db(request.id, line_quantity)
    except Exception as e:
        logger.error(e)

    if len(response) != 0:
        return response[:line_quantity]


def _get_response(data):
    response = []
    date = None
    for i in data.items:
        if isinstance(i.creation_date, int):
            date = datetime.utcfromtimestamp(i.creation_date).strftime('%d/%m/%Y-%H:%M:%S')
        if isinstance(i.creation_date, datetime):
            date = i.creation_date.strftime('%d/%m/%Y-%H:%M:%S')
        response.append(Response(date=date,
                                 title=i.title,
                                 link=i.link))
    return response


def _get_temp_object(data):
    return json.loads(json.dumps(data), object_hook=lambda d: SimpleNamespace(**d))


async def _get_all_requests(line_quantity: int):
    response = []
    requests = await request_repository.RequestRepository.get_all_request(line_quantity)
    for i in requests:
        response.append(Response(date=i.date.strftime('%d/%m/%Y-%H:%M:%S'), title=i.request_string,
                                 link=f'/response?search={i.request_string}&line_quantity=25'))
    return response


async def _get_response_from_db(request_id: int, line_quantity: int):
    rq = await request_repository.RequestRepository.select(request_id, line_quantity)
    return _get_response(rq)


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
