import logging
from typing import Optional

LEVEL = logging.INFO


# TODO: provide interface to use ``logging.dictConfig``
def get_logger(name: str, log_level: Optional[int] = None) -> logging.Logger:
    logger = logging.getLogger(name)
    # We must not call setLevel by default except on the root logger otherwise
    # we cannot change log levels for all modules by changing level of the root
    # logger
    if log_level is not None:
        logger.setLevel(log_level)
    return logger


# set default log level to LEVEL
trino_root_logger = get_logger('avrio', LEVEL)
