import configparser
import os
from configparser import NoSectionError


class Config(object):
    def __init__(self, section, parser):
        self.section = section
        self.parser = parser
        if section != 'DEFAULT' and section not in self.parser.sections():
            raise NoSectionError(section)

    def _get_param(self, param_name):
        return self.parser.get(self.section, param_name, fallback=None)

    def _get_int_param(self, param_name):
        return self.parser.getint(self.section, param_name, fallback=None)

    def _get_boolean_param(self, param_name):
        return self.parser.getboolean(self.section, param_name, fallback=None)


class DefaultConfig(Config):
    def __init__(self, section, parser):
        super().__init__(section, parser)
        self.debug = self._get_boolean_param('debug')
        self.port = self._get_int_param('port')


class DBConnectionConfig(Config):
    def __init__(self, section, parser):
        super().__init__(section, parser)
        self.provider = self._get_param('provider')
        self.user = self._get_param('user')
        self.password = self._get_param('password')
        self.host = self._get_param('host')
        self.port = self._get_param('port')
        self.database = self._get_param('database')


class ApmConfig(Config):
    def __init__(self, section, parser):
        super().__init__(section, parser)
        self.server_url = self._get_param('server_url')


class LoggingConfig(Config):
    def __init__(self, section, parser):
        super().__init__(section, parser)
        self.period = self._get_param('period')
        self.suffix = self._get_param('suffix')
        self.filename = self._get_param('filename')
        self.path = self._get_param('path')


_app_config_path = os.path.join(os.path.dirname(__file__), '', 'app.config')
_parser = configparser.ConfigParser(allow_no_value=True)
_parser.optionxform = str
_parser.read(_app_config_path)

default_config = DefaultConfig('DEFAULT', _parser)
db_connection_config = DBConnectionConfig('DB_CONNECTION', _parser)
log_config = LoggingConfig('LOGGING', _parser)
try:
    apm_config = ApmConfig('APM', _parser)
except NoSectionError:
    apm_config = None
