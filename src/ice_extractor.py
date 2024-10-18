
# Python imports:
import logging
import math

# External imports:
from scipy.interpolate import LinearNDInterpolator

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

        self.row_roughness: list[tuple[(int, float, float, float)]] = []

        self.total_column_dx: float = 0.0
        self.total_column_dy: float = 0.0
        self.total_column_length: float = 0.0
        self.total_row_dx: float = 0.0
        self.total_row_dy: float = 0.0
        self.total_row_length: float = 0.0

        self.step_length1: float = 0.0

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

        self.interpolator = LinearNDInterpolator(
            list(zip(self.original_points_x, self.original_points_y)),
            self.original_points_z)

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

        self.row_roughness = []

        # Calculation of roughness:
        col: int = 0
        num_of_samples: int = 5
        num_of_samples2: float = float(num_of_samples)
        num_of_samples3: int = round(num_of_samples / 2)

        min_rough: float = self.original_points_z[0]
        min_x: float = 0.0
        min_y: float = 0.0

        max_rough: float = 0.0
        max_x: float = 0.0
        max_y: float = 0.0

        for (xr, yr, _) in self.first_row:
            current_row_x: list[float] = []
            current_row_y: list[float] = []
            current_row_z: list[float] = []

            for i in range(num_of_rows):
                x = xr + (float(i) * dx)
                y = yr + (float(i) * dy)

                z = self.interpolator(x, y)
                if not math.isnan(z):
                    self.extracted_points_x.append(x)
                    self.extracted_points_y.append(y)
                    self.extracted_points_z.append(z)

                    current_row_x.append(x)
                    current_row_y.append(y)
                    current_row_z.append(z)

            num_z_vals: int = len(current_row_z)

            if num_z_vals > num_of_samples:
                z_mean: float = sum(current_row_z) / float(num_z_vals)
                z_std_div: list[float] = [math.pow(val_z - z_mean, 2.0) for val_z in current_row_z]

                for i in range(num_z_vals - num_of_samples + 1):
                    std_sum: float = sum(z_std_div[i:i + num_of_samples])
                    rough: float = math.sqrt(std_sum / num_of_samples2)
                    x = current_row_x[i + num_of_samples3]
                    y = current_row_y[i + num_of_samples3]
                    self.row_roughness.append((col, x, y, rough))

                    if rough < min_rough:
                        min_rough = rough
                        min_x = x
                        min_y = y
                    elif rough > max_rough:
                        max_rough = rough
                        max_x = x
                        max_y = y

            col = col + 1

        logger.debug(f"Min roughness: {min_rough} at {min_x}, {min_y}")
        logger.debug(f"Max roughness: {max_rough} at {max_x}, {max_y}")

    def save_roughness(self, filename: str):
        with open(filename, "w") as f:
            for (c, x, y, r) in self.row_roughness:
                f.write(f"{c}, {x}, {y}, {r}\n")


