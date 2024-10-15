
# Python imports:
import logging
import math

# External imports:
from scipy.spatial import KDTree

logger = logging.getLogger(__name__)

PointList = list[tuple[(float, float, float)]]


class Extractor:
    def __init__(self, angle: float, step: float):
        self.start_x: float = 0.0
        self.start_y: float = 0.0

        # Column (yellow to green)
        self.dx1: float = 0.0
        self.dy1: float = 0.0

        # Row (yellow to yellow)
        self.dx2: float = 0.0
        self.dy2: float = 0.0

        self.user_angle: float = angle
        self.user_step: float = step

        self.num_of_rows: int = 36
        self.num_of_cols: int = 895

        self.start_points: PointList = []
        self.end_points: PointList = []

        self.extracted_points_x: list[float] = []
        self.extracted_points_y: list[float] = []
        self.extracted_points_z: list[float] = []

        self.original_points_x: list[float] = []
        self.original_points_y: list[float] = []
        self.original_points_z: list[float] = []

        self.data_dx1: float = 0.0
        self.data_dx2: float = 0.0
        self.total_column_dx: float = 0.0
        self.total_column_dy: float = 0.0
        self.total_column_length: float = 0.0
        self.data_dy1: float = 0.0
        self.data_dy2: float = 0.0
        self.total_row_dx: float = 0.0
        self.total_row_dy: float = 0.0
        self.total_row_length: float = 0.0

        self.step_length1: float = 0.0
        self.kd_tree = KDTree([(0.0, 0.0), (0.0, 0.0)])

    def read_file(self, filename: str):
        logger.info(f"Reading file: {filename}")

        with open(filename, "r") as f:
            self.read_data_points(f)

        self.extract_points()
        self.save_extracted_points()

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

    def set_dx1_dy1(self):
        factor: float = self.user_step / self.step_length1
        logger.debug(f"Column step factor: {factor}")

        self.dx1 = self.data_dx1 * factor
        self.dy1 = self.data_dy1 * factor
        logger.debug(f"dx1: {self.dx1}, dy1: {self.dy1}")

    def set_dx2_dy2(self):
        # Rotate row vector:
        angle_rad = math.radians(self.user_angle)
        sin_angle = math.sin(angle_rad)
        cos_angle = math.cos(angle_rad)
        self.dx2 = (self.data_dx2 * cos_angle) - (self.data_dy2 * sin_angle)
        self.dy2 = (self.data_dx2 * sin_angle) + (self.data_dy2 * cos_angle)
        logger.debug(f"dx2: {self.dx2}, dy2: {self.dy2}")

    def read_data_points(self, file):
        self.original_points_x = []
        self.original_points_y = []
        self.original_points_z = []

        self.start_points = []
        self.end_points = []

        for (x, y, z, column, row) in self.yield_values_from_file(file):
            if column == 1:
                self.start_points.append((x, y, z))
                if row == 1:
                    self.start_x = x
                    self.start_y = y
            elif (column == 2) and (row == 1):
                self.data_dx1 = x - self.start_points[0][0]
                self.data_dy1 = y - self.start_points[0][1]
                logger.debug(f"Column step: dx: {self.data_dx1}, dy: {self.data_dy1}")
                self.step_length1: float = math.hypot(self.data_dx1, self.data_dy1)
                logger.debug(f"Column step length: {self.step_length1}")
                self.set_dx1_dy1()
            elif column == self.num_of_cols:
                self.end_points.append((x, y, z))

            self.original_points_x.append(x)
            self.original_points_y.append(y)
            self.original_points_z.append(z)

        logger.debug(f"Number of starting points: {len(self.start_points)}")

        self.data_dx2 = self.start_points[1][0] - self.start_points[0][0]
        self.data_dy2 = self.start_points[1][1] - self.start_points[0][1]
        logger.debug(f"Row step: dx: {self.data_dx2}, dy: {self.data_dy2}")

        self.set_dx2_dy2()

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

        s: float = 1.0

        while True:
            f1: float = math.exp(-d1 * s)
            f2: float = math.exp(-d2 * s)
            f3: float = math.exp(-d3 * s)
            f4: float = math.exp(-d4 * s)

            f_sum = f1 + f2 + f3 + f4

            if f_sum > 0.0:
                break

            s = s * 0.5
            logger.debug(f"Scale: {s}, x: {x}, y: {y}, d1: {d1}, d2: {d2}, d3: {d3}, d4: {d4}")

        z = (z1 * f1) + (z2 * f2) + (z3 * f3) + (z4 * f4) / f_sum

        return z

    def extract_points(self):
        x: float = self.start_x
        y: float = self.start_y
        z: float = 0.0

        self.extracted_points_x = []
        self.extracted_points_y = []
        self.extracted_points_z = []

        num_of_cols: int = math.floor(self.total_column_length / self.user_step)
        logger.debug(f"Final number of columns: {num_of_cols}")

        for i in range(num_of_cols):
            x = self.start_x + (float(i) * self.dx1)
            y = self.start_y + (float(i) * self.dy1)

            for _ in range(self.num_of_rows):
                self.extracted_points_x.append(x)
                self.extracted_points_y.append(y)
                z = self.calculate_z_value(x, y)
                self.extracted_points_z.append(z)

                x = x + self.dx2
                y = y + self.dy2

    def save_extracted_points(self):
        with open("extracted_points.csv", "w") as f:
            for (x, y, z) in zip(self.extracted_points_x, self.extracted_points_y, self.extracted_points_z):
                f.write(f"{x}, {y}, {z}\n")


