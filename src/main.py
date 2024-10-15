

# Python imports
import logging
import sys
import time

# External imports
import matplotlib.pyplot as plt

# Local imports
import extractor

logger = logging.getLogger(__name__)


# Call this Python script with:
# python3 src/main.py -1.23 -500.0 assets/Rutford_DELORES_TWTT_2D_201617_500m_spaced

def plot_data(ex: extractor.Extractor):
    x1 = ex.original_points_x
    y1 = ex.original_points_y
    z1 = ex.original_points_z

    x2 = ex.extracted_points_x
    y2 = ex.extracted_points_y
    z2 = ex.extracted_points_z

    fig, (ax1, ax2) = plt.subplots(2)
    fig.suptitle("Heatmaps of measured points")

    cmap = ax1.tricontourf(x1, y1, z1, cmap="RdBu_r")

    for (x, y, _) in ex.start_points:
        ax1.plot(x, y, "yo")  # yellow circle

    for (x, y, _) in ex.end_points:
        ax1.plot(x, y, "go")  # green circle

    fig.colorbar(cmap, ax=ax1)
    ax1.tick_params(axis="x", labelrotation=90)

    ax2.tricontourf(x2, y2, z2, cmap="RdBu_r")
    fig.colorbar(cmap, ax=ax2)
    ax2.tick_params(axis="x", labelrotation=90)

    fig.set_size_inches(10.0, 15.0)
    fig.tight_layout()

    plt.savefig("plot.png", dpi=100)


def main():
    start = time.time()

    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    log_file_name = "extractor.log"
    logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=log_format)
    logging.getLogger("matplotlib").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)

    filename = (sys.argv[1])

    ex = extractor.Extractor()
    ex.read_file(filename)

    plot_data(ex)

    end = time.time()
    duration = end - start

    logger.info(f"Duration in seconds: {duration}")


if __name__ == "__main__":
    main()

