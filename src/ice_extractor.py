
# Python imports:
import logging
import math

# External imports:
from scipy.spatial import KDTree

logger = logging.getLogger(__name__)

PointList = list[tuple[(float, float, float)]]


class IceExtractor:
    def __init__(self):
        self.angle: float = 0.0
        self.step: float = 500.0

        self.num_of_rows: int = 36
        self.num_of_cols: int = 895

        self.start_points: PointList = []
        self.end_points: PointList = []

        self.first_row: PointList = []

        self.extracted_points_x: list[float] = []
        self.extracted_points_y: list[float] = []
        self.extracted_points_z: list[float] = []

        self.original_points_x: list[float] = []
        self.original_points_y: list[float] = []
        self.original_points_z: list[float] = []

        self.total_column_dx: float = 0.0
        self.total_column_dy: float = 0.0
        self.total_column_length: float = 0.0
        self.total_row_dx: float = 0.0
        self.total_row_dy: float = 0.0
        self.total_row_length: float = 0.0

        self.step_length1: float = 0.0
        self.kd_tree = KDTree([(0.0, 0.0), (0.0, 0.0)])

    def is_empty(self) -> bool:
        return not self.start_points

    def read_file(self, filename: str):
        logger.info(f"Reading file: {filename}")

        with open(filename, "r") as f:
            self.read_data_points(f)

        self.extract_points()

    def yield_values_from_file(self, file):
        for line in file:
            if line.startswith("# Grid_size:"):
                grid_info = line[12:].split("x")
                self.num_of_cols = int(grid_info[0])
                self.num_of_rows = int(grid_info[1])

                logger.debug(f"Last col: {self.num_of_cols}")
                logger.debug(f"Last row: {self.num_of_rows}")

                continue
            elif line.startswith("#"):
                continue

            items: list[str] = line.split()

            x: float = float(items[0])
            y: float = float(items[1])
            z: float = float(items[2])
            column: int = int(items[3])
            row: int = int(items[4])

            yield (x, y, z, column, row)

    def read_data_points(self, file):
        self.original_points_x = []
        self.original_points_y = []
        self.original_points_z = []

        self.start_points = []
        self.end_points = []

        self.first_row = []

        for (x, y, z, column, row) in self.yield_values_from_file(file):
            if column == 1:
                self.start_points.append((x, y, z))
            elif column == self.num_of_cols:
                self.end_points.append((x, y, z))

            if row == 1:
                self.first_row.append((x, y, z))

            self.original_points_x.append(x)
            self.original_points_y.append(y)
            self.original_points_z.append(z)

        logger.debug(f"Number of starting points: {len(self.start_points)}")

        self.total_column_dx = self.end_points[0][0] - self.start_points[0][0]
        self.total_column_dy = self.end_points[0][1] - self.start_points[0][1]
        self.total_column_length = math.hypot(self.total_column_dx, self.total_column_dy)
        logger.debug(f"Total column dx: {self.total_column_dx}, dy: {self.total_column_dy}")
        logger.debug(f"Total column length: {self.total_column_length}")

        self.total_row_dx = self.start_points[-1][0] - self.start_points[0][0]
        self.total_row_dy = self.start_points[-1][1] - self.start_points[0][1]
        self.total_row_length = math.hypot(self.total_row_dx, self.total_row_dy)
        logger.debug(f"Total row dx: {self.total_row_dx}, dy: {self.total_row_dy}")
        logger.debug(f"Total row length: {self.total_row_length}")

        angle = math.asin(-self.total_row_dy / self.total_row_length)
        angle_d: float = math.degrees(angle)

        if self.total_row_dx < 0.0:
            angle_d = 180.0 - angle_d
        else:
            if angle_d < 0.0:
                angle_d = 360.0 + angle_d

        self.angle = angle_d

        self.kd_tree = KDTree(list(zip(self.original_points_x, self.original_points_y)))

    def calculate_z_value(self, x: float, y: float) -> float:
        (distances, indices) = self.kd_tree.query((x, y), k=4)

        d1: float = distances[0]
        d2: float = distances[1]
        d3: float = distances[2]
        d4: float = distances[3]

        i1: int = indices[0]
        i2: int = indices[1]
        i3: int = indices[2]
        i4: int = indices[3]

        z1: float = self.original_points_z[i1]
        z2: float = self.original_points_z[i2]
        z3: float = self.original_points_z[i3]
        z4: float = self.original_points_z[i4]

        f1: float = math.exp(-d1 * 0.5)
        f2: float = math.exp(-d2 * 0.5)
        f3: float = math.exp(-d3 * 0.5)
        f4: float = math.exp(-d4 * 0.5)

        f_sum = f1 + f2 + f3 + f4

        if f_sum == 0.0:
            return math.nan
        else:
            z = (z1 * f1) + (z2 * f2) + (z3 * f3) + (z4 * f4) / f_sum
            return z

    def extract_points(self):
        x: float = 0.0
        y: float = 0.0
        z: float = 0.0

        num_of_rows: int = math.floor(self.total_row_length / self.step)

        angle_r: float = math.radians(self.angle)
        dx: float = self.step * math.cos(angle_r)
        dy: float = -self.step * math.sin(angle_r)

        logger.debug(f"{dx=}, {dy=}, {num_of_rows=}")

        self.extracted_points_x = []
        self.extracted_points_y = []
        self.extracted_points_z = []

        for (xr, yr, _) in self.first_row:
            for i in range(num_of_rows):
                x = xr + (float(i) * dx)
                y = yr + (float(i) * dy)

                z = self.calculate_z_value(x, y)
                if not math.isnan(z):
                    self.extracted_points_x.append(x)
                    self.extracted_points_y.append(y)
                    self.extracted_points_z.append(z)

    def save_extracted_points(self, filename: str):
        with open(filename, "w") as f:
            for (x, y, z) in zip(self.extracted_points_x, self.extracted_points_y, self.extracted_points_z):
                f.write(f"{x}, {y}, {z}\n")


