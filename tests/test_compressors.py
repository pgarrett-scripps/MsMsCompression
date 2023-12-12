import unittest
import numpy as np

from msms_compression.compressors import SpectrumCompressor, SpectrumCompressorUrl

mz_values = list(np.array([100.0, 100.0, 200.0, 300.0, 300.0], dtype=np.float32))
intensity_values = list(np.array([50.0, 20.0, 30.0, 20.0, 50.0], dtype=np.float32))


class TestCompressor(unittest.TestCase):
    def test_compress_decompress(self):

        compressed = SpectrumCompressor().compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = SpectrumCompressor().decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)

    def test_compress_decompress_url(self):
        compressed = SpectrumCompressorUrl().compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = SpectrumCompressorUrl().decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


if __name__ == '__main__':
    unittest.main()
