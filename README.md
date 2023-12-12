# MS/MS Data Compression Package

## Description

This Python package is designed for efficient compression of Mass Spectrometry (MS/MS) data. It is based on the MassComp
algorithm, which is described in the following paper: https://doi.org/10.1186/s12859-019-2962-7


## Version

0.1.0

## Features

- **Delta and Hex Encoding**: Efficiently encodes m/z values and intensities to optimize the compression.
- **Brotli Compression**: Utilizes Brotli, a high-performance compression algorithm, offering superior compression ratios and speeds compared to gzip.

## Installation

To install the MS/MS Data Compression package, run:

```
pip install msms-compression
```

## Usage

The package includes the following main compressor classes:

- `SpectrumCompressorUrl`: Utilizes URL-safe Base64 encoding.
- `SpectrumCompressor`: Uses Base85 encoding.

* Note: The m/z values must be sorted in ascending order before compression, and contain only positive values.

### Example:

```python
from msms_compression import SpectrumCompressor

# Sample data
mz_values, intensity_values = [100.0, 101.0, 102.0], [10.0, 20.0, 30.0]

# Initialize the compressor
compressor = SpectrumCompressor()

# Compress data
compressed_data = compressor.compress(mz_values, intensity_values)
print("Compressed Data:", compressed_data)

# Decompress data
decompressed_mz, decompressed_intensity = compressor.decompress(compressed_data)
assert decompressed_mz == mz_values
assert decompressed_intensity == intensity_values
```
