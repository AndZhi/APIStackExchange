from abc import abstractmethod, ABC
import psycopg2
from psycopg2 import sql, errors, errorcodes
from tortoise.contrib.aiohttp import register_tortoise

from config_manager import db_connection_config as configs


class BaseRepository(ABC):
    @staticmethod
    def db_init(app):
        BaseRepository._create_db()
        BaseRepository._generate_mapping(app)

    @staticmethod
    def _create_db():
        try:
            con = psycopg2.connect(user=configs.user,
                                   password=configs.password,
                                   host=configs.host,
                                   port=configs.port)
            con.autocommit = True
            cur = con.cursor()
            cur.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(configs.database)))
        except psycopg2.errors.lookup(psycopg2.errorcodes.DUPLICATE_DATABASE):
            pass
        except Exception as e:
            raise e

    @staticmethod
    def _generate_mapping(app):
        register_tortoise(
            app,
            db_url=f'{configs.provider}://{configs.user}:{configs.password}@{configs.host}:{configs.port}/{configs.database}',
            modules={'models': ['app.models.models']},
            generate_schemas=True)

    @abstractmethod
    async def insert(self, obj):
        pass

    @abstractmethod
    async def select(self, obj):
        pass

    @abstractmethod
    async def update(self, obj):
        pass

    @abstractmethod
    async def delete(self, obj):
        pass
