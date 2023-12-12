# MS/MS Data Compression Package

## Description

This Python package is designed for efficient compression of Mass Spectrometry/Mass Spectrometry (MS/MS) data. It provides various strategies to compress and decompress mass-to-charge ratio (m/z) and intensity values, leveraging advanced encoding and compression algorithms.

## Version

0.0.1

## Features

- **Delta and Hex Encoding**: Efficiently encodes m/z values and intensities to optimize the compression.
- **Brotli Compression**: Utilizes Brotli, a high-performance compression algorithm, offering superior compression ratios and speeds.
- **Multiple Encoding Formats**: Supports Base64 and Base85 encoding, ensuring compatibility and safe transmission over various platforms.

## Installation

To install the MS/MS Data Compression package, run:

```
pip install msms-compression
```

## Usage

The package includes the following main compressor classes:

- `MsMsUrlCompressor`: Utilizes URL-safe Base64 encoding.
- `MsMsB85Compressor`: Uses Base85 encoding.

* Note: The m/z values must be sorted in ascending order before compression, and contain only positive values.

### Example:

```python
from msms_compression import MsMsB85Compressor

# Sample data
mz_values, intensity_values = [100.0, 101.0, 102.0], [10.0, 20.0, 30.0]

# Initialize the compressor
compressor = MsMsB85Compressor()

# Compress data
compressed_data = compressor.compress(mz_values, intensity_values)
print("Compressed Data:", compressed_data)

# Decompress data
decompressed_mz, decompressed_intensity = compressor.decompress(compressed_data)
assert decompressed_mz == mz_values
assert decompressed_intensity == intensity_values
```
