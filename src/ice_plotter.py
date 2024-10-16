

# External imports
import matplotlib.pyplot as plt


# Local imports
import ice_extractor as ie


class IcePlotter:
    def __init__(self):
        self.x1: list[float] = []
        self.y1: list[float] = []
        self.z1: list[float] = []

        self.x2: list[float] = []
        self.y2: list[float] = []
        self.z2: list[float] = []

        self.start_points: ie.PointList = []
        self.end_points: ie.PointList = []

        # self.fig = None
        # self.ax1 = None
        # self.ax2 = None
        # self.cmap = None

    def get_data_from_extractor(self, extractor: ie.IceExtractor):
        self.set_original(
            extractor.original_points_x,
            extractor.original_points_y,
            extractor.original_points_z)

        self.set_extracted(
            extractor.extracted_points_x,
            extractor.extracted_points_y,
            extractor.extracted_points_z)

        self.set_start_points(extractor.start_points)
        self.set_end_points(extractor.end_points)

    def set_original(self, x1: list[float], y1: list[float], z1: list[float]):
        self.x1 = x1
        self.y1 = y1
        self.z1 = z1

    def set_extracted(self, x2: list[float], y2: list[float], z2: list[float]):
        self.x2 = x2
        self.y2 = y2
        self.z2 = z2

    def set_start_points(self, start_points: ie.PointList):
        self.start_points = start_points

    def set_end_points(self, end_points: ie.PointList):
        self.end_points = end_points

    def plot_original(self):
        self.cmap = self.ax1.tricontourf(self.x1, self.y1, self.z1, cmap="RdBu_r")

        for (x, y, _) in self.start_points:
            self.ax1.plot(x, y, "yo")  # yellow circle

        for (x, y, _) in self.end_points:
            self.ax1.plot(x, y, "go")  # green circle

        self.fig.colorbar(self.cmap, ax=self.ax1)
        self.ax1.tick_params(axis="x", labelrotation=90)

    def plot_extracted(self):
        self.ax2.tricontourf(self.x2, self.y2, self.z2, cmap="RdBu_r")
        self.fig.colorbar(self.cmap, ax=self.ax2)
        self.ax2.tick_params(axis="x", labelrotation=90)

    def plot_both(self):
        self.fig, (self.ax1, self.ax2) = plt.subplots(2)
        self.fig.suptitle("Heatmaps of measured points")

        self.plot_original()
        self.plot_extracted()

        self.fig.set_size_inches(10.0, 15.0)
        self.fig.tight_layout()

    def save_figure(self, filename: str):
        plt.savefig(filename, dpi=100)


