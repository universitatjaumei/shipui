import logging
import StringIO
import sys
from colors import Colors

class ShipLogger:
    logger = logging.getLogger("ship")

    def __init__(self):
        if not ShipLogger.logger.handlers:
            ShipLogger._setup_handlers()

    @staticmethod
    def _setup_handlers(loglevel="INFO", fmt="[ship] %(levelname)s %(message)s"):
        ShipLogger.logger.setLevel(loglevel)
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(logging.Formatter(fmt))
        ShipLogger.logger.addHandler(handler)
        memory_handler = logging.StreamHandler(StringIO.StringIO())
        memory_handler.setFormatter(logging.Formatter(fmt))
        ShipLogger.logger.addHandler(memory_handler)

    @staticmethod
    def get_memory_stream():
        if not ShipLogger.logger.handlers:
            ShipLogger._setup_handlers()

        return ShipLogger.logger.handlers[1].stream

    def setup_logger_if_not_initialized(self):
        if not self.__class__.logger.handlers:
            self.__class__._setup_handlers()

    def info(self, msg):
        self.setup_logger_if_not_initialized()
        self.__class__.logger.info(Colors.OKGREEN + msg + Colors.ENDC)

    def warning(self, msg):
        self.setup_logger_if_not_initialized()
        self.__class__.logger.warning(Colors.WARNING + msg + Colors.ENDC)

    def error(self, msg):
        self.setup_logger_if_not_initialized()
        self.__class__.logger.error(Colors.FAIL + msg + Colors.ENDC)

    def success(self, msg):
        self.setup_logger_if_not_initialized()
        self.__class__.logger.error(Colors.OKBLUE + msg + Colors.ENDC)
