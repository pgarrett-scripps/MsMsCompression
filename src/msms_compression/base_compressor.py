from typing import List

from msms_compression.data_compressor import DataCompressor
from msms_compression.encoder import Encoder
from msms_compression.spectrum_compressor import SpectrumCompressor


class BaseCompressor:

    def __init__(self, _compressor: SpectrumCompressor, _data_compressor: DataCompressor, _encoder: Encoder):
        self._spectrum_compressor: SpectrumCompressor = _compressor
        self._compressor: DataCompressor = _data_compressor
        self._encoder: Encoder = _encoder

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = self._spectrum_compressor.compress(mzs, intensities)
        b = s.encode('utf-8')
        b = self._compressor.compress(b)
        b = self._encoder.encode(b)
        s = b.decode('utf-8')
        return s

    def decompress(self, s: str) -> (List[float], List[float]):
        b = s.encode('utf-8')
        b = self._encoder.decode(b)
        b = self._compressor.decompress(b)
        s = b.decode('utf-8')
        mzs, intensities = self._spectrum_compressor.decompress(s)
        return mzs, intensities

    def __str__(self):
        return f'{str(self._spectrum_compressor)}_{str(self._compressor)}_{str(self._encoder)}'
