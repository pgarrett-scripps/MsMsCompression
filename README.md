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
from msms_compression import SpectrumCompressorF32

# Sample data
mz_values, intensity_values = [100.0, 101.0, 102.0], [10.0, 20.0, 30.0]

# Initialize the compressor
compressor = SpectrumCompressorF32()

# Compress data
compressed_data = compressor.compress(mz_values, intensity_values)
print("Compressed Data:", compressed_data)

# Decompress data
decompressed_mz, decompressed_intensity = compressor.decompress(compressed_data)
assert decompressed_mz == mz_values
assert decompressed_intensity == intensity_values
```

# Compression Strategy Comparison

|strategy|Compression Ratio            |Compression Ratio Rank|URL Compression Ratio|URL Compression Ratio Rank|Compression Time  |Compression Time Rank|Decompression Time  |Decompression Time Rank|
|--------|-----------------------------|----------------------|---------------------|--------------------------|------------------|---------------------|--------------------|-----------------------|
|SpectrumCompressorLossy|5.952                        |1                     |5.023                |2                         |0.030             |5                    |0.008               |4                      |
|SpectrumCompressorUrlLossy|5.579                        |2                     |6.926                |1                         |0.030             |4                    |0.007               |1                      |
|SpectrumCompressor|3.890                        |3                     |3.299                |6                         |0.053             |7                    |0.010               |6                      |
|SpectrumCompressorUrl|3.646                        |4                     |4.528                |3                         |0.051             |6                    |0.008               |3                      |
|SpectrumCompressorGzip|3.148                        |5                     |2.658                |7                         |0.023             |2                    |0.009               |5                      |
|SpectrumCompressorUrlGzip|2.951                        |6                     |3.665                |4                         |0.022             |1                    |0.007               |2                      |
|SpectrumCompressorUrlLzstring|2.800                        |7                     |3.418                |5                         |0.026             |3                    |0.097               |7                      |


|scan|strategy                     |original_size|compressed_size|url_encoded_size|compression_ratio |url_compression_ratio|compressed_time     |decompressed_time   |
|----|-----------------------------|-------------|---------------|----------------|------------------|---------------------|--------------------|--------------------|
|0   |SpectrumCompressor           |56124        |14428          |21139           |3.88993623509842  |3.299068073229576    |0.053049564361572266|0.009985208511352539|
|0   |SpectrumCompressorUrl        |56124        |15392          |15401           |3.646309771309771 |4.528212453736771    |0.051015615463256836|0.00789642333984375 |
|0   |SpectrumCompressorGzip       |56124        |17829          |26236           |3.1479050984351336|2.6581414849824667   |0.02299976348876953 |0.009003639221191406|
|0   |SpectrumCompressorUrlGzip    |56124        |19020          |19029           |2.950788643533123 |3.664879920121919    |0.021996021270751953|0.007005453109741211|
|0   |SpectrumCompressorUrlLzstring|56124        |20041          |20402           |2.8004590589291953|3.418243309479463    |0.026098012924194336|0.09739089012145996 |
|0   |SpectrumCompressorLossy      |56124        |9429           |13884           |5.952274896595609 |5.022976087582829    |0.030114173889160156|0.007976055145263672|
|0   |SpectrumCompressorUrlLossy   |56124        |10060          |10069           |5.578926441351888 |6.9261098420895815   |0.030014991760253906|0.006910562515258789|


The method compresses intensity values into two-character hexadecimal strings, offering 256 unique representations. This is a lossy approach, effectively reducing data size. Meanwhile, m/z values are compressed losslessly using delta encoding, maintaining their exact accuracy.