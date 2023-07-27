import logging


class BaseFilter(logging.Filter):
    def filter(self, record):
        msg = ("Received command c on object id p0",)  # databricks py4j message
        if any(msg in record.getMessage()):
            return 0
        return True
