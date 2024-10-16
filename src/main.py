

# Python imports
import logging
import sys
import time

# Local imports
import ice_extractor as ie
import ice_plotter as ip

logger = logging.getLogger(__name__)


def main():
    start = time.time()

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    log_file_name = "extractor.log"
    logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=log_format)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    filename = (sys.argv[1])

    ex = ie.IceExtractor()
    ex.read_file(filename)

    plotter = ip.IcePlotter()
    plotter.get_data_from_extractor(ex)
    plotter.plot_both()
    plotter.save_figure("plot.png")

    end = time.time()
    duration = end - start

    logger.info(f"Duration in seconds: {duration}")


if __name__ == "__main__":
    main()

