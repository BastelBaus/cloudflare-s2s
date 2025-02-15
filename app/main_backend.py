import sys
import logging

from backend.main import main


logger = logging.getLogger(__name__)

logging.basicConfig(
    level=logging.INFO,
    format="[%(name)s.%(funcName)s:%(lineno)d] %(levelname)s %(message)s",
    stream=sys.stdout)


if __name__ == "__main__":
    app = main()
