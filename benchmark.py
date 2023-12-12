from msms_compression import SpectrumCompressor, SpectrumCompressorUrl

import urllib.parse
import random

from msms_compression.compressors import SpectrumCompressorGzip, SpectrumCompressorUrlGzip, SpectrumCompressorLzstring, \
    SpectrumCompressorUrlLzstring

print(SpectrumCompressorUrl().compress([100.0, 200.0, 300.0], [10.0, 20.0, 30.0]))
def generate_random_data(size=100):
    """ Generate random mz and intensity values for testing """
    mz_values = []
    intensity_values = []

    for i in range(size):
        mz_values.append(random.random() * 1000)
        intensity_values.append(random.random() * 1000)

    return mz_values, intensity_values


def calculate_compression_stats(original_data, compressed_data):
    original_size = len(str(original_data))
    original_url_size = len(urllib.parse.urlencode({'data': original_data}))
    compressed_size = len(compressed_data)
    url_encoded_size = len(urllib.parse.urlencode({'data': compressed_data}))
    compression_ratio = original_size / compressed_size
    url_compression_ratio = original_url_size / url_encoded_size
    return original_size, compressed_size, url_encoded_size, compression_ratio, url_compression_ratio


def test_compression(strategy, mz_values, intensity_values):
    print(f"Testing {strategy.__class__.__name__}...")
    compressed = strategy.compress(mz_values, intensity_values)
    decompressed_mz, decompressed_intensity = strategy.decompress(compressed)

    original_size, compressed_size, url_encoded_size, compression_ratio, url_compression_ratio = calculate_compression_stats(
        (mz_values, intensity_values), compressed)

    print(f"Original Size: {original_size} bytes")
    print(f"Compressed Size: {compressed_size} bytes")
    print(f"URL Encoded Size: {url_encoded_size} bytes")
    print(f"Compression Ratio: {compression_ratio:.2f}")
    print(f"URL Compression Ratio: {url_compression_ratio:.2f}")
    print(f"compressed spectrum: {compressed}")
    print()


# Generate random data
mz_values, intensity_values = generate_random_data()

for strategy in [SpectrumCompressor(), SpectrumCompressorUrl(),
                 SpectrumCompressorGzip(), SpectrumCompressorUrlGzip(),
                 SpectrumCompressorUrlLzstring()]:

    print(f"Testing {strategy.__class__.__name__}...")
    test_compression(strategy, mz_values, intensity_values)
