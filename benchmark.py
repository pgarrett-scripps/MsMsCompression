import inspect

import numpy as np

import msms_compression
from msms_compression.compression_strategies import *

import urllib.parse


def generate_random_data(size=100):
    """ Generate random mz and intensity values for testing """
    mz_values = np.random.uniform(50, 1000, size).astype(np.float32)
    mz_values.sort()
    intensity_values = np.random.uniform(1, 100, size).astype(np.float32)
    return list(mz_values), list(intensity_values)


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
    print()


# Generate random data
mz_values, intensity_values = generate_random_data()

# Test each compression strategy
# Dynamically get all compression strategies from the module
strategy_classes = [cls for name, cls in inspect.getmembers(msms_compression.compression_strategies)
                    if inspect.isclass(cls) and issubclass(cls, BaseCompressionStrategy) and cls is not BaseCompressionStrategy]

# Test each compression strategy
for strategy_class in strategy_classes:
    strategy = strategy_class()
    test_compression(strategy, mz_values, intensity_values)
