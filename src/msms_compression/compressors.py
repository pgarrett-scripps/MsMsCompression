import base64
import json
from typing import List

import brotli
import gzip

from .utils import delta_encode_single_string, hex_encode, delta_decode_single_string, hex_decode


class BaseCompressor:
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_str = hex_encode(intensities)
        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        mzs = list(delta_decode_single_string(mz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class SpectrumCompressor:

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = BaseCompressor().compress(mzs, intensities)
        compressed_data = brotli.compress(s.encode('utf-8'))
        return base64.b85encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.b85decode(s))
        mzs, intensities = BaseCompressor().decompress(s.decode('utf-8'))
        return mzs, intensities


class SpectrumCompressorUrl:

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = BaseCompressor().compress(mzs, intensities)
        compressed_data = brotli.compress(s.encode('utf-8'))
        return base64.urlsafe_b64encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.urlsafe_b64decode(s))
        mzs, intensities = BaseCompressor().decompress(s.decode('utf-8'))
        return mzs, intensities


class SpectrumCompressorGzip:

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = BaseCompressor().compress(mzs, intensities)
        compressed_data = gzip.compress(s.encode('utf-8'))
        return base64.b85encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = gzip.decompress(base64.b85decode(s))
        mzs, intensities = BaseCompressor().decompress(s.decode('utf-8'))
        return mzs, intensities


class SpectrumCompressorUrlGzip:

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = BaseCompressor().compress(mzs, intensities)
        compressed_data = gzip.compress(s.encode('utf-8'))
        return base64.urlsafe_b64encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = gzip.decompress(base64.urlsafe_b64decode(s))
        mzs, intensities = BaseCompressor().decompress(s.decode('utf-8'))
        return mzs, intensities
