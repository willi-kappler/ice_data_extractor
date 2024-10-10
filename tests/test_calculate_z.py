
# Python modules:
import unittest
import logging
import pathlib


# Local modules:
import extractor


logger = logging.getLogger(__name__)


class TestZCalculation(unittest.TestCase):
    def test_calculation1(self):
        points = [(0.0, 0.0, 10.0), (1.0, 0.0, 10.0), (0.0, 1.0, 10.0), (1.0, 1.0, 10.0)]
        z = extractor.calculate_z_value(0.5, 0.5, points)
        self.assertAlmostEqual(z, 10.0)

        z = extractor.calculate_z_value(0.8, 0.3, points)
        self.assertAlmostEqual(z, 10.0)

    def test_calculation2(self):
        points = [(0.0, 0.0, 10.0), (10.0, 0.0, 10.0), (0.0, 10.0, 10.0), (10.0, 10.0, 10.0)]
        z = extractor.calculate_z_value(5.0, 5.0, points)
        self.assertAlmostEqual(z, 10.0)

        z = extractor.calculate_z_value(9.0, 4.0, points)
        self.assertAlmostEqual(z, 10.0)

    def test_calculation3(self):
        points = [(0.0, 0.0, 10.0), (100.0, 0.0, 10.0), (0.0, 100.0, 10.0), (100.0, 100.0, 10.0)]
        z = extractor.calculate_z_value(50.0, 50.0, points)
        self.assertAlmostEqual(z, 10.0)

        z = extractor.calculate_z_value(78.0, 65.0, points)
        self.assertAlmostEqual(z, 10.0)

    def test_calculation4(self):
        points = [(0.0, 0.0, 10.0), (1.0, 0.0, 10.0), (0.0, 1.0, 10.0), (1.0, 1.0, 10.0)]
        z = extractor.calculate_z_value(1.0, 0.0, points)
        self.assertAlmostEqual(z, 10.0)

    def test_calculation5(self):
        points = [(0.0, 0.0, 10.0), (10.0, 0.0, 10.0), (0.0, 10.0, 10.0), (10.0, 10.0, 10.0)]
        z = extractor.calculate_z_value(10.0, 0.0, points)
        self.assertAlmostEqual(z, 10.0)

    def test_calculation6(self):
        points = [(0.0, 0.0, 10.0), (10.0, 0.0, 8.0), (0.0, 10.0, 2.0), (10.0, 10.0, 5.0)]
        z = extractor.calculate_z_value(0.0, 0.0, points)
        self.assertAlmostEqual(z, 10.0, 2)

        z = extractor.calculate_z_value(10.0, 0.0, points)
        self.assertAlmostEqual(z, 8.0, 2)

        z = extractor.calculate_z_value(0.0, 10.0, points)
        self.assertAlmostEqual(z, 2.0, 2)

        z = extractor.calculate_z_value(10.0, 10.0, points)
        self.assertAlmostEqual(z, 5.0, 2)

        z = extractor.calculate_z_value(5.0, 5.0, points)
        self.assertAlmostEqual(z, 6.25, 2)

    def test_calculation7(self):
        points = [(0.0, 0.0, 10.0), (100.0, 0.0, 8.0), (0.0, 100.0, 2.0), (100.0, 100.0, 5.0)]
        z = extractor.calculate_z_value(100.0, 0.0, points)
        self.assertAlmostEqual(z, 8.0)

        z = extractor.calculate_z_value(50.0, 50.0, points)
        self.assertAlmostEqual(z, 6.25)

    def test_calculation8(self):
        points = [(0.0, 0.0, 10.0), (10.0, 0.0, 8.0), (0.0, 10.0, 2.0), (10.0, 10.0, 5.0)]
        z = extractor.calculate_z_value(100.0, 200.0, points)
        self.assertAlmostEqual(z, 4.966, 2)


if __name__ == "__main__":
    log_file_name: str = "calculation.log"
    log_format = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
    logging.basicConfig(filename=log_file_name, level=logging.DEBUG, format=log_format)

    try:
        unittest.main()
    finally:
        p: pathlib.Path = pathlib.Path(log_file_name)
        p.unlink()

