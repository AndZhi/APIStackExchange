from abc import abstractmethod, ABC
import psycopg2
from psycopg2 import sql, errors, errorcodes
from config_manager import db_connection_config as configs
from app.models.models import db


class BaseRepository(ABC):
    @staticmethod
    def db_init():
        BaseRepository._create_db()
        BaseRepository._generate_mapping()

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
        except psycopg2.errors.lookup(psycopg2.errorcodes.DUPLICATE_DATABASE) as e:
            pass
        except Exception as e:
            raise e

    @staticmethod
    def _generate_mapping():
        db.bind(provider=configs.provider,
                user=configs.user,
                password=configs.password,
                host=configs.host,
                port=configs.port,
                database=configs.database)

        db.generate_mapping(create_tables=True)

    @abstractmethod
    def insert(self, obj):
        pass

    @abstractmethod
    def select(self, obj):
        pass

    @abstractmethod
    def update(self, obj):
        pass

    @abstractmethod
    def delete(self, obj):
        pass
