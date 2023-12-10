import unittest

mz_values = list(np.array([100.0, 100.0, 200.0, 300.0, 300.0], dtype=np.float32))
intensity_values = list(np.array([50.0, 20.0, 30.0, 20.0, 50.0], dtype=np.float32))


class TestNoCompression(unittest.TestCase):
    def setUp(self):
        self.strategy = NoCompression()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzDeltaCompression(unittest.TestCase):
    def setUp(self):
        self.strategy = MzSingleStringDeltaCompressionIntensityHex()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzDeltaCompression2(unittest.TestCase):
    def setUp(self):
        self.strategy = MzDoubleStringDeltaCompressionIntensityHex()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzDeltaCompression3(unittest.TestCase):
    def setUp(self):
        self.strategy = MzDoubleStringDeltaCompressionIntensityGzipUrl()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzDeltaCompression4(unittest.TestCase):
    def setUp(self):
        self.strategy = MzDoubleStringDeltaCompressionGzipUrl()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzDeltaCompression5(unittest.TestCase):
    def setUp(self):
        self.strategy = MzDoubleStringDeltaCompressionGzipB85()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzIntensityDeltaCompression(unittest.TestCase):
    def setUp(self):
        self.strategy = MzIntensitySingleStringDeltaCompression()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestGzipCompression(unittest.TestCase):
    def setUp(self):
        self.strategy = GzipCompression()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestRoundingCompression(unittest.TestCase):
    def setUp(self):
        self.strategy = RoundingCompression()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestUrlCompression(unittest.TestCase):
    def setUp(self):
        self.strategy = UrlRoundingCompression()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestGzipCompressionBase64(unittest.TestCase):
    def setUp(self):
        self.strategy = GzipCompressionBase64()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestGzipCompressionBase85(unittest.TestCase):
    def setUp(self):
        self.strategy = GzipCompressionBase85()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzIntensityDoubleStringDeltaCompression(unittest.TestCase):
    def setUp(self):
        self.strategy = MzIntensityDoubleStringDeltaCompression()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzIntensityDoubleStringDeltaCompressionGzipUrl(unittest.TestCase):
    def setUp(self):
        self.strategy = MzIntensityDoubleStringDeltaCompressionGzipUrl()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


class TestMzIntensityDoubleStringDeltaCompressionGzipB85(unittest.TestCase):
    def setUp(self):
        self.strategy = MzIntensityDoubleStringDeltaCompressionGzipB85()

    def test_compress_decompress(self):
        compressed = self.strategy.compress(mz_values, intensity_values)
        decompressed_mz, decompressed_intensity = self.strategy.decompress(compressed)

        self.assertEqual(mz_values, decompressed_mz)
        self.assertEqual(intensity_values, decompressed_intensity)


if __name__ == '__main__':
    unittest.main()
