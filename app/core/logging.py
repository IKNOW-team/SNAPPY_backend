import logging
import sys

LOG_FORMAT = "%(levelname)s %(asctime)s %(name)s:%(lineno)d - %(message)s"

def setup_logging(debug: bool = False) -> None:
    level = logging.DEBUG if debug else logging.INFO
    logging.basicConfig(stream=sys.stdout, level=level, format=LOG_FORMAT)