
# Python imports
import sys
import logging
import math

logger = logging.getLogger(__name__)


def calculate_z_value(x: float, y: float, points: list[tuple[(float, float, float)]]) -> float:
    result = math.nan

    d1: float = sys.float_info.max
    d2: float = d1
    d3: float = d1
    d4: float = d1

    z1: float = math.nan
    z2: float = z1
    z3: float = z1
    z4: float = z1

    for (x2, y2, z) in points:
        d = math.hypot(x - x2, y - y2)

        if d < d1:
            d4 = d3
            d3 = d2
            d2 = d1
            d1 = d

            z4 = z3
            z3 = z2
            z2 = z1
            z1 = z
        elif d < d2:
            d4 = d3
            d3 = d2
            d2 = d

            z4 = z3
            z3 = z2
            z2 = z
        elif d < d3:
            d4 = d3
            d3 = d

            z4 = z3
            z3 = z
        elif d < d4:
            d4 = d
            z4 = z

    f1 = math.exp(-d1 / 10.0)
    f2 = math.exp(-d2 / 10.0)
    f3 = math.exp(-d3 / 10.0)
    f4 = math.exp(-d4 / 10.0)

    result = (z1 * f1) + (z2 * f2) + (z3 * f3) + (z4 * f4)
    result = result / (f1 + f2 + f3 + f4)

    return result


class EmptyTileError(Exception):
    pass


class Tile:
    def __init__(self, min_x: float, min_y: float, 
            max_x: float, max_y: float, radius: float):
        self.min_x: float = min_x
        self.min_y: float = min_y
        self.max_x: float = max_x
        self.max_y: float = max_y
        self.proximity_radius = radius
        self.center_x: float = (self.min_x + self.max_x) / 2.0
        self.center_y: float = (self.min_y + self.max_y) / 2.0
        self.points: list[tuple[(float, float, float)]] = []

    def point_in_tile(self, x: float, y: float) -> bool:
        in_x: bool = (x >= self.min_x) and (x < self.max_x)
        in_y: bool = (y >= self.min_y) and (y < self.max_y)

        return in_x and in_y

    def point_close_to_tile(self, x: float, y: float) -> bool:
        d = math.hypot(self.center_x - x, self.center_y - y)
        return d <= self.proximity_radius

    def enough_points(self) -> bool:
        return len(self.points) > 3

    def add_point(self, x: float, y: float, z: float):
        self.points.append((x, y, z))

    def calculate_z_value(self, x: float, y: float) -> float:
        if self.enough_points():
            return calculate_z_value(x, y, self.points)
        else:
            raise EmptyTileError
            # return math.nan

    def set_z_values(self, points):
        z = calculate_z_value(self.min_x, self.min_y, points)
        self.points.append((self.min_x, self.min_y, z))

        z = calculate_z_value(self.min_x, self.max_y, points)
        self.points.append((self.min_x, self.max_y, z))

        z = calculate_z_value(self.max_x, self.min_y, points)
        self.points.append((self.max_x, self.min_y, z))

        z = calculate_z_value(self.max_x, self.max_y, points)
        self.points.append((self.max_x, self.max_y, z))

        z = calculate_z_value(self.center_x, self.center_y, points)
        self.points.append((self.center_x, self.center_y, z))


class Extractor:
    def __init__(self):
        self.tile_x: int = 30
        self.tile_y: int = 30
        self.num_of_tiles: int = self.tile_x * self.tile_y
        self.tiles: list[Tile] = []
        self.points: list[tuple[(float, float, float)]] = []

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
            self.update_tiles()

    def create_tiles(self):
        x1 = self.min_x
        x2 = x1 + self.tile_dx
        y1 = self.min_y
        y2 = y1 + self.tile_dy

        radius = max(self.tile_dx, self.tile_dy) * 2.0

        for _ in range(self.num_of_tiles):
            new_tile = Tile(x1, y1, x2, y2, radius)
            self.tiles.append(new_tile)

            x1 += self.tile_dx
            x2 = x1 + self.tile_dx

            if x1 >= self.max_x:
                x1 = self.min_x
                x2 = x1 + self.tile_dx
                y1 += self.tile_dy
                y2 = y1 + self.tile_dy

    def update_tiles(self):
        for tile in self.tiles:
            #logger.debug(f"   min_x: {tile.min_x}, min_y: {tile.min_y}, max_x: {tile.max_x}, max_y: {tile.max_y}")
            tile.set_z_values(self.points)
            logger.debug(f"Points in tile: {len(tile.points)}")

    def yield_points(self):
        for tile in self.tiles:
            for point in tile.points:
                yield point

    def yield_values_from_file(self, file):
        for line in file:
            if line.startswith("#"):
                continue

            items = line.split()

            x = float(items[0])
            y = float(items[1])
            z = float(items[2])

            yield (x, y, z)

    def find_min_max_values(self, file):
        for (x, y, z) in self.yield_values_from_file(file):
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
        for (x, y, z) in self.yield_values_from_file(file):
            self.points.append((x, y, z))

            for tile in self.tiles:
                if tile.point_close_to_tile(x, y):
                    tile.add_point(x, y, z)


