import logging


def get_or_create_logger(name: str = None) -> logging.Logger:
    """Get or create a logger with a given name, or use the default logger if no name is provided.

    .. code-block:: python
        :caption: Example Usage

        _logger = init_logger() # For default root logger
        _logger = init_logger('my_logger') # For a named logger

    """
    logger = logging.getLogger(name)

    # If the logger has handlers, it has already been set up, so return it.
    if logger.hasHandlers():
        return logger

    # Set the logger level
    logger.setLevel(logging.DEBUG)

    # Define handlers
    info_handler = logging.StreamHandler()
    info_handler.setLevel(logging.INFO)
    error_handler = logging.StreamHandler()
    error_handler.setLevel(logging.ERROR)

    # Define formatter
    local_time_format = logging.Formatter(
        "%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    # Set formatter for handlers
    info_handler.setFormatter(local_time_format)
    error_handler.setFormatter(local_time_format)

    # Add handlers to the logger
    logger.addHandler(info_handler)
    logger.addHandler(error_handler)

    return logger
