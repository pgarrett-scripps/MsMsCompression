import json
import math
from typing import List, Protocol

from .utils import delta_encode_single_string_float, hex_encode, delta_decode_single_string_float, hex_decode, \
    hex_encode_lossy, hex_decode_lossy, delta_encode_single_string_int, delta_decode_single_string_int


class SpectrumCompressor(Protocol):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        pass

    def decompress(self, s: str) -> (List[float], List[float]):
        pass

    def __str__(self):
        return self.__class__.__name__


class SpectrumCompressorF32(SpectrumCompressor):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        if mzs:
            mz_str = delta_encode_single_string_float(mzs)
        else:
            mz_str = ''

        if intensities:
            intensity_str = hex_encode(intensities)
        else:
            intensity_str = ''
        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        if mz_str:
            mzs = list(delta_decode_single_string_float(mz_str))
        else:
            mzs = []

        if intensity_str:
            intensities = list(hex_decode(intensity_str))
        else:
            intensities = []
        return mzs, intensities


class SpectrumCompressorF32Lossy(SpectrumCompressor):

    def __init__(self, n_bits):
        self.n_bits = n_bits

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        if mzs:
            mz_str = delta_encode_single_string_float(mzs)
        else:
            mz_str = ''

        if intensities:
            intensities = [math.log(x) for x in intensities]
            intensity_str = hex_encode_lossy(intensities, self.n_bits)
        else:
            intensity_str = ''
        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        if mz_str:
            mzs = list(delta_decode_single_string_float(mz_str))
        else:
            mzs = []

        if intensity_str:
            intensities = list(hex_decode_lossy(intensity_str, self.n_bits))
            intensities = [math.exp(x) for x in intensities]

        else:
            intensities = []
        return mzs, intensities

    def __str__(self):
        return self.__class__.__name__ + f'({str(self.n_bits)})'


class SpectrumCompressorString(SpectrumCompressor):

    def __init__(self, mz_precision, intensity_precision):
        self.mz_precision = mz_precision
        self.intensity_precision = intensity_precision

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        if mzs:
            mz_str = ','.join([str(round(x, self.mz_precision)).replace('.', '') for x in mzs])
        else:
            mz_str = ''

        if intensities:
            intensity_str = ','.join([str(round(x, self.intensity_precision)).replace('.', '') for x in intensities])
        else:
            intensity_str = ''
        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        if mz_str:
            mzs = [float(x[:-2] + '.' + x[-2:]) for x in mz_str.split(',')]
        else:
            mzs = []

        if intensity_str:
            intensities = [float(x[:-2] + '.' + x[-2:]) for x in intensity_str.split(',')]
        else:
            intensities = []
        return mzs, intensities

    def __str__(self):
        return self.__class__.__name__ + f'({self.mz_precision}|{self.intensity_precision})'


class SpectrumCompressorStringLossy(SpectrumCompressor):

    def __init__(self, mz_precision, intensity_precision):
        self.mz_precision = mz_precision
        self.intensity_precision = intensity_precision

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        if mzs:
            mz_str = ','.join([f"{x:.{self.mz_precision}f}".replace(".", "") for x in mzs])
        else:
            mz_str = ''

        if intensities:
            intensities = [math.log(x) for x in intensities]
            intensity_str = hex_encode_lossy(intensities)
        else:
            intensity_str = ''
        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        if mz_str:
            mzs = [float(x[:-2] + '.' + x[-2:]) for x in mz_str.split(',')]
        else:
            mzs = []

        if intensity_str:
            intensities = list(hex_decode_lossy(intensity_str))
            intensities = [math.exp(x) for x in intensities]
        else:
            intensities = []
        return mzs, intensities

    def __str__(self):
        return self.__class__.__name__ + f'({self.mz_precision}|{self.intensity_precision})'


class SpectrumCompressorI32(SpectrumCompressor):

    def __init__(self, mz_precision=2, intensity_precision=1):
        self.mz_precision = mz_precision
        self.intensity_precision = intensity_precision

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        if mzs:
            mzs = [round(mz, self.mz_precision) for mz in mzs]
            mzs = [int(x * (10 ** self.mz_precision)) for x in mzs]
            mz_str = delta_encode_single_string_int(mzs)
        else:
            mz_str = ''

        if intensities:
            intensities = [round(i, self.intensity_precision) for i in intensities]
            intensities = [math.log(x) for x in intensities]
            intensity_str = hex_encode_lossy(intensities)
        else:
            intensity_str = ''
        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        if mz_str:
            mzs = list(delta_decode_single_string_int(mz_str))
            mzs = [round(x / (10 ** self.mz_precision), self.mz_precision) for x in mzs]
        else:
            mzs = []

        if intensity_str:
            intensities = list(hex_decode_lossy(intensity_str))
            intensities = [round(math.exp(x), self.intensity_precision) for x in intensities]
        else:
            intensities = []
        return mzs, intensities

    def __str__(self):
        return f'{self.__class__.__name__}({self.mz_precision}|{self.intensity_precision})'
