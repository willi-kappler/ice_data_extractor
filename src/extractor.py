
# Python imports:
import sys
import logging
import math

# External imports:
from scipy.spatial import KDTree

logger = logging.getLogger(__name__)

PointList = list[tuple[(float, float, float)]]


class Extractor:
    def __init__(self):
        self.start_x: float = -1293737.074199
        self.start_y: float = 124083.532967

        self.dx1: float = -6.643222999991849
        self.dy1: float = 18.864452999987407
        self.dx2: float = 471.61132899997756
        self.dy2: float = 166.08056600000418

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

        self.min_x: float = sys.float_info.max
        self.min_y: float = self.min_x
        self.min_z: float = self.min_x

        self.max_x: float = -self.min_x
        self.max_y: float = -self.min_y
        self.max_z: float = -self.min_z

        self.len_x: float = 0.0
        self.len_y: float = 0.0
        self.len_z: float = 0.0

        self.data_dx1: float
        self.data_dx2: float
        self.column_length: float
        self.data_dy1: float
        self.data_dy2: float
        self.row_length: float

        self.kd_tree = KDTree([(0.0, 0.0), (0.0, 0.0)])

    def read_file(self, filename: str):
        logger.info(f"Reading file: {filename}")

        with open(filename, "r") as f:
            self.find_min_max_values(f)
            f.seek(0)  # rewind file
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

    def find_min_max_values(self, file):
        for (x, y, z, _, _) in self.yield_values_from_file(file):
            if x < self.min_x:
                self.min_x = x
            elif x > self.max_x:
                self.max_x = x

            if y < self.min_y:
                self.min_y = y
            elif y > self.max_y:
                self.max_y = y

            if z < self.min_z:
                self.min_z = z
            elif z > self.max_z:
                self.max_z = z

        self.len_x = self.max_x - self.min_x
        self.len_y = self.max_y - self.min_y
        self.len_z = self.max_z - self.min_z

        logger.debug(f"Min values: x: {self.min_x}, y: {self.min_y}, z: {self.min_z}")
        logger.debug(f"Max values: x: {self.max_x}, y: {self.max_y}, z: {self.max_z}")
        logger.debug(f"Length values: x: {self.len_x}, y: {self.len_y}, z: {self.len_z}")

    def read_data_points(self, file):
        for (x, y, z, column, row) in self.yield_values_from_file(file):
            if column == 1:
                self.start_points.append((x, y, z))
            elif (column == 2) and (row == 1):
                self.data_dx1 = x - self.start_points[0][0]
                self.data_dy1 = y - self.start_points[0][1]
                logger.debug(f"Column step: dx: {self.data_dx1}, dy: {self.data_dy1}")
            elif column == self.num_of_cols:
                self.end_points.append((x, y, z))

            self.original_points_x.append(x)
            self.original_points_y.append(y)
            self.original_points_z.append(z)

        self.data_dx2 = self.start_points[1][0] - self.start_points[0][0]
        self.data_dy2 = self.start_points[1][1] - self.start_points[0][1]
        logger.debug(f"Row step: dx: {self.data_dx2}, dy: {self.data_dy2}")

        logger.debug(f"Number of starting points: {len(self.start_points)}")

        self.row_dx = self.end_points[0][0] - self.start_points[0][0]
        self.row_dy = self.end_points[0][1] - self.start_points[0][1]
        self.row_length = math.hypot(self.row_dx, self.row_dy)
        logger.debug(f"Total row dx: {self.row_dx}, dy: {self.row_dy}")
        logger.debug(f"Total row length: {self.row_length}")

        self.column_dx = self.start_points[-1][0] - self.start_points[0][0]
        self.column_dy = self.start_points[-1][1] - self.start_points[0][1]
        self.column_length = math.hypot(self.column_dx, self.column_dy)
        logger.debug(f"Total column dx: {self.column_dx}, dy: {self.column_dy}")
        logger.debug(f"Total column length: {self.column_length}")

        self.kd_tree = KDTree(list(zip(self.original_points_x, self.original_points_y)))

        self.calculated_angle = math.degrees(math.atan(self.row_dy / self.row_dx))
        logger.debug(f"Calculated row angle: {self.calculated_angle}")

    def extract_points(self):
        x: float = self.start_x
        y: float = self.start_y
        z: float = 0.0

        for i in range(self.num_of_rows):
            x = self.start_x + (float(i) * self.dx2)
            y = self.start_y + (float(i) * self.dy2)
            for _ in range(self.num_of_cols):
                self.extracted_points_x.append(x)
                self.extracted_points_y.append(y)

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

                self.extracted_points_z.append(z)

                x = x + self.dx1
                y = y + self.dy1

    def save_extracted_points(self):
        with open("extracted_points.csv", "w") as f:
            num_points = len(self.extracted_points_x)
            for i in range(num_points):
                x = self.extracted_points_x[i]
                y = self.extracted_points_y[i]
                z = self.extracted_points_z[i]
                f.write(f"{x}, {y}, {z}\n")


