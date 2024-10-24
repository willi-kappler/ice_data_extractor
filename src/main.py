
# Python imports
import logging

# Local imports
import ice_gui as ig

logger = logging.getLogger(__name__)


def main():
    # start = time.time()

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    log_file_name = "extractor.log"
    logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=log_format)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    gui = ig.IceGUI()
    gui.run()


if __name__ == "__main__":
    main()

