
# Python modules:
import unittest
import logging
import pathlib


# Local modules:
import extractor


logger = logging.getLogger(__name__)


class TestTile(unittest.TestCase):
    def test_point_in_tile(self):
        t = extractor.Tile(0.0, 0.0, 10.0, 10.0)
        self.assertTrue(t.point_in_tile(1.0, 1.0))
        self.assertTrue(t.point_in_tile(0.0, 0.0))
        self.assertTrue(t.point_in_tile(9.0, 0.0))
        self.assertTrue(t.point_in_tile(0.0, 9.0))
        self.assertTrue(t.point_in_tile(9.0, 9.0))
        self.assertFalse(t.point_in_tile(10.0, 10.0))
        self.assertFalse(t.point_in_tile(-1.0, 0.0))
        self.assertFalse(t.point_in_tile(0.0, 11.0))

    def test_add_point(self):
        t = extractor.Tile(0.0, 0.0, 10.0, 10.0)
        t.add_point(1.0, 2.0, 3.0)
        self.assertAlmostEqual(t.points[0][0], 1.0)
        self.assertAlmostEqual(t.points[0][1], 2.0)
        self.assertAlmostEqual(t.points[0][2], 3.0)

    def test_maybe_close_point(self):
        t = extractor.Tile(0.0, 0.0, 10.0, 10.0)

        for i in range(11, 30):
            t.maybe_close_point(5.0, float(i), 25.0)

        self.assertEqual(len(t.maybe_points), 10)

        for i in range(10):
            self.assertAlmostEqual(t.maybe_points[i][1], 5.0)
            self.assertAlmostEqual(t.maybe_points[i][2], 11.0 + float(i))
            self.assertAlmostEqual(t.maybe_points[i][3], 25.0)

    def test_merge_points(self):
        t = extractor.Tile(0.0, 0.0, 10.0, 10.0)
        t.add_point(1.0, 2.0, 3.0)

        for i in range(11, 30):
            t.maybe_close_point(5.0, float(i), 25.0)

        t.merge_points()

        self.assertEqual(len(t.points), 11)

    def test_calculate_z(self):
        t = extractor.Tile(0.0, 0.0, 10.0, 10.0)
        t.add_point(0.0, 0.0, 10.0)
        t.add_point(10.0, 0.0, 8.0)
        t.add_point(0.0, 10.0, 2.0)
        t.add_point(10.0, 10.0, 5.0)

        z = t.calculate_z_value(5.0, 5.0)

        self.assertAlmostEqual(z, 6.25, 2)

if __name__ == "__main__":
    log_file_name: str = "calculation.log"
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=log_format)

    unittest.main()
    p: pathlib.Path = pathlib.Path(log_file_name)
    p.unlink()


