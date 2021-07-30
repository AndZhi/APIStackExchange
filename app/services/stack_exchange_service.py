import json
from datetime import datetime
from types import SimpleNamespace
from pony.orm import *
from app.search import client
from repository import request_repository, owner_repository, item_repository, tag_repository
from app.models.models import Request, Item, Owner, Tag, Response
from logger import logger


async def get_requests(**kwargs):
    with db_session:
        return _get_all_requests()[:int(kwargs['line_quantity'])]


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
    with db_session:
        try:
            request_id = _check_request(search_string)
            if request_id is not None:
                _update_request(request_id, temp_object)
            else:
                request = Request(request_string=search_string.lower(), date=datetime.now())
                request_id = request_repository.RequestRepository.insert(request)
                for i in temp_object.items:
                    _create_item(request_id, i)
        except Exception as e:
            logger.error(e)
    try:
        response = _get_search_response(request_id)
    except Exception as e:
        logger.error(e)
    return response[:int(kwargs['line_quantity'])]


def _get_all_requests():
    response = []
    requests = request_repository.RequestRepository.get_all_request()
    for i in requests:
        response.append(Response(date=i.date.strftime('%d.%m.%y %H:%M:%S'), title=i.request_string,
                                 link=f'/response?search={i.request_string}&line_quantity=25'))
    return response


def _get_search_response(request_id: int):
    with db_session:
        response = []
        rq = Request.get(id=request_id)
        for i in rq.items:
            response.append(Response(date=i.creation_date, title=i.title, link=i.link))
        return response


def _update_request(request_id: int, temp_object):
    with db_session:
        request = request_repository.RequestRepository.select(request_id)
        links = []
        for i in request.items:
            links.append(i.link)
        for i in temp_object.items:
            if i.link not in links:
                _create_item(request_id, i)


def _check_request(search_string: str):
    with db_session:
        check_request_id = request_repository.RequestRepository.check_request(search_string)
        if check_request_id is not None:
            return check_request_id
        else:
            return None


def _create_item(request_id: int, input_item):
    item = Item(request=request_id,
                is_answered=_get_attribute(input_item, 'is_answered'),
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
                )
    item_id = item_repository.ItemRepository.insert(item)

    owner = Owner(item=item_id,
                  account_id=_get_attribute(input_item.owner, 'account_id'),
                  reputation=_get_attribute(input_item.owner, 'reputation'),
                  user_id=_get_attribute(input_item.owner, 'user_id'),
                  user_type=_get_attribute(input_item.owner, 'user_type'),
                  accept_rate=_get_attribute(input_item.owner, 'accept_rate'),
                  profile_image=_get_attribute(input_item.owner, 'profile_image'),
                  display_name=_get_attribute(input_item.owner, 'display_name'),
                  link=_get_attribute(input_item.owner, 'link'),
                  )
    owner_repository.OwnerRepository.insert(owner)

    if input_item.tags is not None:
        for t in input_item.tags:
            tag = Tag(value=t, item=item_id)
            tag_repository.TagRepository.insert(tag)


def _get_attribute_date(obj, attribute_name):
    if hasattr(obj, attribute_name):
        return datetime.utcfromtimestamp(getattr(obj, attribute_name))
    else:
        None


def _get_attribute(obj, attribute_name):
    if hasattr(obj, attribute_name):
        return getattr(obj, attribute_name)
    else:
        None
