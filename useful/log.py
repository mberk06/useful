import logging


class FilterPy4JClientServer(logging.Filter):
    def filter(self, record):
        return 'py4j.clientserver' not in record.name and 'py4j.clientserver' not in record.message

def get_or_create_logger(name: str = None) -> logging.Logger:
    """Get or create a logger with a given name, or use the default logger if no name is provided.

    .. code-block:: python
        :caption: Example Usage

        _logger = init_logger() # For default root logger
        _logger = init_logger('my_logger') # For a named logger

    """

    logging.getLogger("py4j").setLevel(logging.ERROR) # Set py4j logs to ERROR

    logger = logging.getLogger(name)

    if logger.hasHandlers():
        return logger

    logger.setLevel(logging.DEBUG)

    info_handler = logging.StreamHandler()
    info_handler.setLevel(logging.INFO)
    error_handler = logging.StreamHandler()
    error_handler.setLevel(logging.ERROR)

    formatter = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    info_handler.setFormatter(formatter)
    error_handler.setFormatter(formatter)

    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    filter_py4j = FilterPy4JClientServer()
    logger.addFilter(filter_py4j)

    return logger
