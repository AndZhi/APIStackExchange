from aiohttp import web
import jinja2
import aiohttp_jinja2
from repository.base_repository import BaseRepository
from logger import logger
from config_manager import default_config
from tortoise.contrib.aiohttp import register_tortoise


def setup_routes(application):
    from app.search.routes import setup_routes as setup_forum_routes
    setup_forum_routes(application)


def setup_external_libraries(application: web.Application) -> None:
    aiohttp_jinja2.setup(application, loader=jinja2.FileSystemLoader("templates"))


def setup_app(application):
    setup_external_libraries(application)
    setup_routes(application)


app = web.Application()
register_tortoise(
    app,
    db_url="postgres://postgres:11111@127.0.0.1:5400/TT_test",
    modules={"models": ["__main__"]},
    generate_schemas=True)

if __name__ == "__main__":
    port = default_config.port
    BaseRepository.db_init()
    setup_app(app)
    web.run_app(app, port=port)
    logger.info('Web-Service started at port %s', port)
