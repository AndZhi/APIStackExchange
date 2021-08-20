""" Файл с функциями для логирования. """
import logging as logging
import os
import structlog
import sys

from logging.handlers import TimedRotatingFileHandler
from structlog import processors

import config_manager

_service_name = 'test-project'


def _get_filename(filename):
    # Получаем директорию, где расположены логи
    log_directory = os.path.split(filename)[0]

    # Расширением (с точкой) файла является
    # значение suffix (у нас - %Y%m%d) (например .20181231).
    # Но точка нам не нужна, т.к. файл будет
    # называться suffix.log (20181231.log)
    date = os.path.splitext(filename)[1][1:]

    # Сформировали имя нового лог-файла
    filename = os.path.join(log_directory, date)

    if not os.path.exists('{}.log'.format(filename)):
        return '{}.log'.format(filename)

    index = 0
    file = '{}.{}.log'.format(filename, index)
    while os.path.exists(file):
        index += 1
        file = '{}.{}.log'.format(filename, index)
    return file


def _event_renamer_processor(_, __, event_dict):
    event_dict['message'] = event_dict.pop('event')
    return event_dict


def _add_timestamp(_, __, event_dict):
    from datetime import datetime, timezone, timedelta
    import time

    def current_tz():
        if time.daylight:
            return timezone(timedelta(seconds=-time.altzone), time.tzname[1])
        else:
            return timezone(timedelta(seconds=-time.timezone), time.tzname[0])

    event_dict['@timestamp'] = datetime.now(current_tz()).isoformat()
    return event_dict


def _add_log_level_info(_, __, event_dict):
    record = event_dict.get('_record')
    if record is not None:
        event_dict['log.level'] = record.levelname.title()
    return event_dict


def _add_log_info(_, __, event_dict):
    record = event_dict.get('_record')
    if record is not None:
        event_dict['log'] = {
            'logger': record.name,
            'origin': {
                'file': {
                    'line': record.lineno,
                    'name': record.filename,
                },
                'function': record.funcName,
            },
        }
    return event_dict


def _add_process_info(_, __, event_dict):
    import threading

    event_dict['process'] = {
        'pid': os.getpid(),
        'thread': {
            'id': threading.get_ident(),
            'name': threading.current_thread().name,
        },
    }
    return event_dict


def _add_service_info(_, __, event_dict):
    event_dict['service'] = {
        'name': _service_name
    }
    return event_dict


def _add_host_info(_, __, event_dict):
    from getpass import getuser
    from socket import gethostname

    event_dict['host'] = {
        'name': gethostname(),
        'user': {'name': getuser()}
    }
    return event_dict


def _add_exception_info(_, method_name, event_dict):
    import traceback

    if method_name == 'error':
        error = {'message': event_dict['message']}
        exc_info = event_dict.pop('exc_info', None)
        if exc_info:
            exc_type = exc_info[0]
            if issubclass(exc_type, BaseException):
                error['type'] = exc_type.__name__
            error['stack_trace'] = traceback.format_exception(exc_type, exc_info[1], exc_info[2])
        event_dict['error'] = error
    return event_dict


def _add_trace_info(_, __, event_dict):
    # TODO добавить методы для получения транзакций в tracer и использовать его
    from elasticapm.traces import execution_context

    transaction = execution_context.get_transaction()
    if transaction:
        event_dict['transaction'] = {'id': transaction.id}
    if transaction and transaction.trace_parent:
        event_dict['trace'] = {'id': transaction.trace_parent.trace_id}
    span = execution_context.get_span()
    if span and span.id:
        event_dict['span'] = {'id': span.id}
    return event_dict


def _get_struct_log_formatter():
    formatter_processors = [
        _add_timestamp,
        _add_log_level_info,
        _event_renamer_processor,
        _add_log_info,
        _add_process_info,
        _add_service_info,
        _add_host_info,
        _add_exception_info,
        _add_trace_info,
    ]

    formatter = structlog.stdlib.ProcessorFormatter(
        processor=processors.JSONRenderer(sort_keys=False, ensure_ascii=False),
        foreign_pre_chain=formatter_processors,
    )
    return formatter


def _get_logger():
    config_manager.apm_config and logging.getLogger('elasticapm').setLevel(logging.ERROR)
    logging.getLogger('urllib3.connectionpool').setLevel(logging.ERROR)

    log_level = (logging.DEBUG if config_manager.default_config.debug else logging.INFO)
    when_mode = {'per_day': 'd', 'per_minute': 'm',
                 'per_hour': 'h', 'midnight': 'midnight'}

    when_mode_config = config_manager.log_config.period
    log_suffix_config = config_manager.log_config.suffix
    folder = config_manager.log_config.path
    filename = config_manager.log_config.filename
    path = os.path.join(folder, filename)

    if not os.path.exists(folder):
        os.mkdir(folder)

    formatter = _get_struct_log_formatter()
    rotation_logging_handler = TimedRotatingFileHandler(
        path, when=when_mode[when_mode_config], interval=1, backupCount=5, encoding='utf-8')
    rotation_logging_handler.setLevel(log_level)
    rotation_logging_handler.setFormatter(formatter)
    rotation_logging_handler.suffix = log_suffix_config
    rotation_logging_handler.namer = _get_filename

    console_format = u'%(asctime)s\t%(levelname)s\t' \
                     u'%(filename)s:%(lineno)d\t%(message)s'
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(logging.Formatter(console_format))

    logger = logging.getLogger()
    logger.setLevel(log_level)
    logger.addHandler(rotation_logging_handler)
    logger.addHandler(stream_handler)
    return logger


def _handle_exception(exc_type, exc_value, exc_traceback):
    if issubclass(exc_type, KeyboardInterrupt):
        sys.__excepthook__(exc_type, exc_value, exc_traceback)
        return
    try:
        logging.exception(exc_value, exc_info=(exc_type, exc_value, exc_traceback))
    except Exception:
        sys.__excepthook__(exc_type, exc_value, exc_traceback)


logger = _get_logger()
sys.excepthook = _handle_exception