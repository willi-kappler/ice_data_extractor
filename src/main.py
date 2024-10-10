

# Python imports
import logging
import sys
import time

# External imports

# Local imports
import extractor

logger = logging.getLogger(__name__)


def main():
    start = time.time()

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    log_file_name = "extractor.log"
    logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=log_format)

    angle = float(sys.argv[1])
    step_x = float(sys.argv[2])
    filename = (sys.argv[3])

    ex = extractor.Extractor(angle, step_x)
    ex.read_file(filename)

    end = time.time()
    duration = end - start

    logger.info(f"Duration in seconds: {duration}")


if __name__ == "__main__":
    main()

