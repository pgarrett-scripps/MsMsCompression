__version__ = '0.3.0'

from msms_compression.base_compressor import BaseCompressor
from msms_compression.data_compressor import BrotliCompressor, GzipCompressor, SkipCompressor
from msms_compression.encoder import B85Encoder, UrlEncoder, LzStringEncoder, LzStringUriEncoder
from msms_compression.spectrum_compressor import SpectrumCompressorF32, SpectrumCompressorF32Lossy, \
    SpectrumCompressorString, SpectrumCompressorStringLossy, SpectrumCompressorI32

# Compression algorithms
spectrum_compressor_f32 = SpectrumCompressorF32()
spectrum_compressor_f32_lossy2 = SpectrumCompressorF32Lossy(2)
spectrum_compressor_f32_lossy3 = SpectrumCompressorF32Lossy(3)
spectrum_compressor_string = SpectrumCompressorString(2, 1)
spectrum_compressor_string_lossy = SpectrumCompressorStringLossy(2, 1)
spectrum_compressor_i32 = SpectrumCompressorI32(2, 1)
spectrum_compressor_i32_3 = SpectrumCompressorI32(3, 1)

# Data compressors
brotli_compressor = BrotliCompressor()
gzip_compressor = GzipCompressor()
skip_compressor = SkipCompressor()

# Data Encoders
b85_encoder = B85Encoder()
url_encoder = UrlEncoder()
lzstring_encoder = LzStringEncoder()
lzstring_uri_encoder = LzStringUriEncoder()

# Default spectrum compressors (Can make your own by defining a new BaseCompressor)
SpectrumCompressorUrl = BaseCompressor(spectrum_compressor_f32, brotli_compressor, url_encoder)
SpectrumCompressorB85 = BaseCompressor(spectrum_compressor_f32, brotli_compressor, b85_encoder)
SpectrumCompressorF32LzstringUri = BaseCompressor(spectrum_compressor_f32, skip_compressor, lzstring_uri_encoder)


