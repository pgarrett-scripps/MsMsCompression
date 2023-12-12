import inspect
import unittest
import numpy as np

import msms_compression
from msms_compression.compression_strategies import BaseCompressionStrategy

mz_values = list(np.array([100.0, 100.0, 200.0, 300.0, 300.0], dtype=np.float32))
intensity_values = list(np.array([50.0, 20.0, 30.0, 20.0, 50.0], dtype=np.float32))


class BaseTestCompressionStrategy(unittest.TestCase):
    strategy_class = None

    def setUp(self):
        if self.strategy_class is not None:
            print(f"Testing {self.strategy_class.__name__}")
            self.strategy = self.strategy_class()

    def test_compress_decompress(self):
        if self.strategy_class is not None:
            compressed = self.strategy.compress(mz_values, intensity_values)
            decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)
            self.assertEqual(mz_values, decompressed_mz)
            self.assertEqual(intensity_values, decompressed_intensity)


# Dynamically create a test class for each strategy
for name, cls in inspect.getmembers(msms_compression.compression_strategies, inspect.isclass):
    if issubclass(cls, BaseCompressionStrategy) and cls is not BaseCompressionStrategy:
        # Create a new test class for the strategy
        new_class = type(f"Test{cls.__name__}", (BaseTestCompressionStrategy,), {"strategy_class": cls})
        # Add the class to the current module's namespace
        globals()[f"Test{cls.__name__}"] = new_class


if __name__ == '__main__':
    unittest.main()
