
# Python imports
import sys
import logging
import math
from operator import itemgetter

logger = logging.getLogger(__name__)

PointList = list[tuple[(float, float, float)]]

def calculate_z_value(x: float, y: float,
        points: PointList,
        num_of_values: int = 4
        ) -> float:

    assert num_of_values > 3, "To interpolate the z values at least 4 points must be used!"
    assert num_of_values <= len(points), "Number of points too low!"

    values: list[tuple[(float, float)]] = []
    max_dist: float = sys.float_info.max

    for _ in range(num_of_values):
        values.append((max_dist, 0.0))

    for (x2, y2, z) in points:
        d: float = math.hypot(x - x2, y - y2)

        if d < values[-1][0]:
            values[-1] = (d, z)
            values.sort(key = itemgetter(0))

    result: float = 0.0
    factor_sum: float = 0.0

    for (dist, z_val) in values:
        factor = math.exp(-dist * 0.1)
        result = result + (z_val * factor)
        factor_sum = factor_sum + factor

    if factor_sum > 0.0:
        result = result / factor_sum

    return result


class Tile:
    def __init__(self, min_x: float, min_y: float, 
            max_x: float, max_y: float):
        self.min_x: float = min_x
        self.min_y: float = min_y
        self.max_x: float = max_x
        self.max_y: float = max_y
        self.center_x: float = (self.min_x + self.max_x) / 2.0
        self.center_y: float = (self.min_y + self.max_y) / 2.0
        self.points: PointList = []
        self.maybe_points: list[tuple[(float, float, float, float)]] = []

        max_dist: float = sys.float_info.max
        for _ in range(10):
            self.maybe_points.append((max_dist, 0.0, 0.0, 0.0))

    def point_in_tile(self, x: float, y: float) -> bool:
        in_x: bool = (x >= self.min_x) and (x < self.max_x)
        in_y: bool = (y >= self.min_y) and (y < self.max_y)

        return in_x and in_y

    def add_point(self, x: float, y: float, z: float):
        self.points.append((x, y, z))

    def maybe_close_point(self, x, y, z):
        d: float = math.hypot(self.center_x - x, self.center_y - y)

        if d < self.maybe_points[-1][0]:
            self.maybe_points[-1] = (d, x, y, z)
            self.maybe_points.sort(key = itemgetter(0))

    def merge_points(self):
        for (_, x, y, z) in self.maybe_points:
            self.points.append((x, y, z))

        # No longer needed
        del self.maybe_points

    def calculate_z_value(self, x: float, y: float) -> float:
        return calculate_z_value(x, y, self.points)


class Extractor:
    def __init__(self, angle: float):
        self.angle: float = angle
        self.step_x = 500 # [m]
        self.step_y = math.sin(math.radians(self.angle)) * self.step_x

        logger.debug(f"Angle: {self.angle}")
        logger.debug(f"X step: {self.step_x} m, Y step: {self.step_y} m")

        self.tile_x: int = 30
        self.tile_y: int = 30
        self.num_of_tiles: int = self.tile_x * self.tile_y
        self.tiles: list[Tile] = []
        self.starting_points: list[tuple[(float, float)]] = []
        self.extracted_points: PointList = []

        self.min_x: float = sys.float_info.max
        self.min_y: float = self.min_x
        self.min_z: float = self.min_x

        self.max_x: float = -self.min_x
        self.max_y: float = -self.min_y
        self.max_z: float = -self.min_z

        self.len_x: float = 0.0
        self.len_y: float = 0.0
        self.len_z: float = 0.0

        self.tile_dx: float = 0.0
        self.tile_dy: float = 0.0

    def read_file(self, filename: str):
        logger.info(f"Reading file: {filename}")

        with open(filename, "r") as f:
            self.find_min_max_values(f)
            self.create_tiles()
            f.seek(0) # rewind file
            self.read_data_points(f)

        self.extract_points()
        self.save_extracted_points()

    def create_tiles(self):
        x1: float = self.min_x
        x2: float = x1 + self.tile_dx
        y1: float = self.min_y
        y2: float = y1 + self.tile_dy

        for _ in range(self.num_of_tiles):
            new_tile = Tile(x1, y1, x2, y2)
            self.tiles.append(new_tile)

            x1 += self.tile_dx
            x2 = x1 + self.tile_dx

            if x1 >= self.max_x:
                x1 = self.min_x
                x2 = x1 + self.tile_dx
                y1 += self.tile_dy
                y2 = y1 + self.tile_dy

    def yield_points(self):
        for tile in self.tiles:
            for point in tile.points:
                yield point

    def yield_values_from_file(self, file):
        for line in file:
            if line.startswith("#"):
                continue

            items: list[str] = line.split()

            x: float = float(items[0])
            y: float = float(items[1])
            z: float = float(items[2])
            column: int = int(items[3])

            yield (x, y, z, column)

    def find_min_max_values(self, file):
        for (x, y, z, _) in self.yield_values_from_file(file):
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

        self.tile_dx = self.len_x / float(self.tile_x)
        self.tile_dy = self.len_y / float(self.tile_y)

        logger.debug(f"Min values: x: {self.min_x}, y: {self.min_y}, z: {self.min_z}")
        logger.debug(f"Max values: x: {self.max_x}, y: {self.max_y}, z: {self.max_z}")
        logger.debug(f"Length values: x: {self.len_x}, y: {self.len_y}, z: {self.len_z}")
        logger.debug(f"Tile spacing: x: {self.tile_dx}, y: {self.tile_dy}")

    def read_data_points(self, file):
        for (x, y, z, column) in self.yield_values_from_file(file):
            if column == 1:
                self.starting_points.append((x, y))

            for tile in self.tiles:
                if tile.point_in_tile(x, y):
                    tile.add_point(x, y, z)
                else:
                    tile.maybe_close_point(x, y, z)

        for tile in self.tiles:
            tile.merge_points()
            logger.debug(f"Number of points in tile: {len(tile.points)}")

        logger.debug(f"Number of starting points: {len(self.starting_points)}")

    def calculate_z_value(self, x: float, y: float) -> float:
        result: float = 0.0

        for tile in self.tiles:
            if tile.point_in_tile(x, y):
                result = tile.calculate_z_value(x, y)

        return result

    def extract_points(self):
        for (sx, sy) in self.starting_points:
            x: float = sx + self.step_x
            y: float = sy + self.step_y

            while (x < self.max_x) and (y < self.max_y):
                z = self.calculate_z_value(x, y)
                self.extracted_points.append((x, y, z))

                x = x + self.step_x
                y = y + self.step_y


    def save_extracted_points(self):
        with open("extracted_points.csv", "w") as f:
            for (x, y, z) in self.extracted_points:
                f.write(f"{x}, {y}, {z}\n")


