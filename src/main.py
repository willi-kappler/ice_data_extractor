
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

    # filename = (sys.argv[1])

    # ex.read_file(filename)

    # plotter.get_data_from_extractor(ex)
    # plotter.plot_both()
    # plotter.save_figure("plot.png")

    # end = time.time()
    # duration = end - start

    # logger.info(f"Duration in seconds: {duration}")


if __name__ == "__main__":
    main()

