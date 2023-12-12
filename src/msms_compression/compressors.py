import base64
import json
from typing import List

from .utils import delta_encode_single_string, hex_encode, delta_decode_single_string, hex_decode, compress_string, \
    decompress_string


class BaseCompressor:
    encode_function = None
    decode_function = None

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_str = hex_encode(intensities)

        mz_str_compressed = compress_string(mz_str, self.encode_function)
        intensity_str_compressed = compress_string(intensity_str, self.encode_function)

        return json.dumps((mz_str_compressed, intensity_str_compressed))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str_compressed, intensity_str_compressed = json.loads(s)

        mz_str = decompress_string(mz_str_compressed, self.decode_function)
        intensity_str = decompress_string(intensity_str_compressed, self.decode_function)

        mzs = list(delta_decode_single_string(mz_str))
        intensities = list(hex_decode(intensity_str))

        return mzs, intensities


class SpectrumCompressor(BaseCompressor):
    encode_function = staticmethod(base64.b85encode)
    decode_function = staticmethod(base64.b85decode)


class SpectrumCompressorUrl(BaseCompressor):
    encode_function = staticmethod(base64.urlsafe_b64encode)
    decode_function = staticmethod(base64.urlsafe_b64decode)
