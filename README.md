# MS/MS Data Compression Package

## Description

This Python package is designed for efficient compression of Mass Spectrometry (MS/MS) data. It is based on the MassComp
algorithm, which is described in the following paper: https://doi.org/10.1186/s12859-019-2962-7


## Version

0.2.0

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

# Compression Strategy Comparison

|strategy                     |Compression Ratio|Compression Ratio Rank|URL Compression Ratio|URL Compression Ratio Rank|Compression Time|Compression Time Rank|Decompression Time|Decompression Time Rank|
|-----------------------------|-----------------|----------------------|---------------------|--------------------------|----------------|---------------------|------------------|-----------------------|
|SpectrumCompressorLossy      |5.952            |1                     |5.023                |1                         |0.030           |3                    |0.008             |1                      |
|SpectrumCompressor           |3.890            |2                     |3.299                |5                         |0.054           |5                    |0.009             |3                      |
|SpectrumCompressorUrl        |3.646            |3                     |4.528                |2                         |0.057           |6                    |0.008             |2                      |
|SpectrumCompressorGzip       |3.148            |4                     |2.658                |6                         |0.026           |2                    |0.009             |5                      |
|SpectrumCompressorUrlGzip    |2.951            |5                     |3.665                |3                         |0.024           |1                    |0.009             |4                      |
|SpectrumCompressorUrlLzstring|2.800            |6                     |3.418                |4                         |0.031           |4                    |0.109             |6                      |

The lossy compression strategy converts each intensity to a 2 character hex string (which offers 256 unique values).
This strategy is lossy, but offers the best compression ratio. 
M/Z values are losslessly compressed using delta encoding for all strategies, including lossy.