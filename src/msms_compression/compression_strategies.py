import base64
import json
import pickle
from typing import List

import brotli
import numpy as np

from .utils import delta_encode_single_string, hex_encode, delta_decode_single_string, hex_decode, delta_encode, \
    leading_zero_compression, leading_zero_decompression, delta_decode, encode_indexes, decode_indexes, \
    delta_encode_single_string2, delta_decode_single_string2


class BaseCompressionStrategy:
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        raise NotImplementedError

    def decompress(self, s: str) -> (List[float], List[float]):
        raise NotImplementedError


class NoCompression(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        return json.dumps((str(mzs), str(intensities)))

    def decompress(self, s: str) -> (List[float], List[float]):
        mzs, intensities = json.loads(s)
        mzs = eval(mzs)
        intensities = eval(intensities)
        return mzs, intensities


class MzDeltaIntensityHexSingleStringCompression(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = delta_encode_single_string2(mzs, intensities)
        return s

    def decompress(self, s: str) -> (List[float], List[float]):
        vals = list(delta_decode_single_string2(s))
        mzs = vals[::2]
        intensities = vals[1::2]
        return mzs, intensities


class MzDeltaIntensityHexSingleStringCompressionBrotliB85(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzDeltaIntensityHexSingleStringCompression().compress(mzs, intensities)
        s = brotli.compress(s.encode('utf-8'))
        return base64.b85encode(s).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = base64.b85decode(s)
        s = brotli.decompress(s)
        mzs, intensities = MzDeltaIntensityHexSingleStringCompression().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzDeltaIntensityHexSingleStringCompressionBrotliB64Url(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzDeltaIntensityHexSingleStringCompression().compress(mzs, intensities)
        s = brotli.compress(s.encode('utf-8'))
        return base64.urlsafe_b64encode(s).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = base64.urlsafe_b64decode(s)
        s = brotli.decompress(s)
        mzs, intensities = MzDeltaIntensityHexSingleStringCompression().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzSingleStringDeltaCompressionIntensityHex(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_str = hex_encode(intensities)
        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        mzs = list(delta_decode_single_string(mz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class MzSingleStringDeltaCompressionIntensityHexBrotliB85(BaseCompressionStrategy):

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzSingleStringDeltaCompressionIntensityHex().compress(mzs, intensities)
        compressed_data = brotli.compress(s.encode('utf-8'))
        return base64.b85encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.b85decode(s))
        mzs, intensities = MzSingleStringDeltaCompressionIntensityHex().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzSingleStringDeltaCompressionIntensityHexBrotliUrl(BaseCompressionStrategy):

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzSingleStringDeltaCompressionIntensityHex().compress(mzs, intensities)
        compressed_data = brotli.compress(s.encode('utf-8'))
        return base64.urlsafe_b64encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.urlsafe_b64decode(s))
        mzs, intensities = MzSingleStringDeltaCompressionIntensityHex().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzDoubleStringDeltaCompressionIntensityHex(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str, lz_str = delta_encode(mzs)
        lz_str_hex = leading_zero_compression(lz_str)
        intensity_str = hex_encode(intensities)
        return json.dumps((mz_str, lz_str_hex, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, lz_str_hex, intensity_str = json.loads(s)
        lz_str = leading_zero_decompression(lz_str_hex)
        mzs = list(delta_decode(mz_str, lz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class MzDoubleStringDeltaCompressionIntensityHexBrotliUrl(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzDoubleStringDeltaCompressionIntensityHex().compress(mzs, intensities)
        s = brotli.compress(s.encode('utf-8'))
        return base64.urlsafe_b64encode(s).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.urlsafe_b64decode(s))
        mzs, intensities = MzDoubleStringDeltaCompressionIntensityHex().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzDoubleStringDeltaCompressionIntensityHexBrotliB85(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzDoubleStringDeltaCompressionIntensityHex().compress(mzs, intensities)
        s = brotli.compress(s.encode('utf-8'))
        return base64.b85encode(s).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.b85decode(s))
        mzs, intensities = MzDoubleStringDeltaCompressionIntensityHex().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzIntensitySingleStringDeltaCompression(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_indexes = list(np.argsort(intensities))
        encoded_indexes = encode_indexes(intensity_indexes)
        intensities = np.array(intensities)[intensity_indexes]
        intensity_str = delta_encode_single_string(intensities)
        return json.dumps((mz_str, intensity_str, encoded_indexes))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str, encoded_indexes = json.loads(s)
        mzs = list(delta_decode_single_string(mz_str))
        decoded_intensities = list(delta_decode_single_string(intensity_str))
        indexes = list(decode_indexes(encoded_indexes))
        original_intensities = np.empty_like(decoded_intensities)
        original_intensities[indexes] = decoded_intensities
        return mzs, list(original_intensities)


class MzIntensitySingleStringDeltaCompressionBrotliB85(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzIntensitySingleStringDeltaCompression().compress(mzs, intensities)
        s = brotli.compress(s.encode('utf-8'))
        return base64.b85encode(s).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.b85decode(s))
        mzs, intensities = MzIntensitySingleStringDeltaCompression().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzIntensitySingleStringDeltaCompressionBrotliUrl(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzIntensitySingleStringDeltaCompression().compress(mzs, intensities)
        s = brotli.compress(s.encode('utf-8'))
        return base64.urlsafe_b64encode(s).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.urlsafe_b64decode(s))
        mzs, intensities = MzIntensitySingleStringDeltaCompression().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzIntensityDoubleStringDeltaCompression(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str, lz_str = delta_encode(mzs)
        lz_str_hex = leading_zero_compression(lz_str)

        intensity_indexes = list(np.argsort(intensities))
        encoded_indexes = encode_indexes(intensity_indexes)
        intensities = np.array(intensities)[intensity_indexes]

        int_str, int_lz_str = delta_encode(intensities)
        int_lz_str_hex = leading_zero_compression(int_lz_str)

        return json.dumps((mz_str, lz_str_hex, int_str, int_lz_str_hex, encoded_indexes))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, lz_str_hex, int_str, int_lz_str_hex, encoded_indexes = json.loads(s)
        lz_str = leading_zero_decompression(lz_str_hex)
        mzs = list(delta_decode(mz_str, lz_str))

        int_lz_str = leading_zero_decompression(int_lz_str_hex)
        ints = list(delta_decode(int_str, int_lz_str))

        indexes = list(decode_indexes(encoded_indexes))
        original_intensities = np.empty_like(ints)
        original_intensities[indexes] = ints

        return mzs, list(original_intensities)


class MzIntensityDoubleStringDeltaCompressionBrotliUrl(BaseCompressionStrategy):

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzIntensityDoubleStringDeltaCompression().compress(mzs, intensities)
        s = brotli.compress(s.encode('utf-8'))
        return base64.urlsafe_b64encode(s).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.urlsafe_b64decode(s))
        mzs, intensities = MzIntensityDoubleStringDeltaCompression().decompress(s.decode('utf-8'))
        return mzs, intensities


class MzIntensityDoubleStringDeltaCompressionBrotliB85(BaseCompressionStrategy):

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzIntensityDoubleStringDeltaCompression().compress(mzs, intensities)
        s = brotli.compress(s.encode('utf-8'))
        return base64.b85encode(s).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        s = brotli.decompress(base64.b85decode(s))
        mzs, intensities = MzIntensityDoubleStringDeltaCompression().decompress(s.decode('utf-8'))
        return mzs, intensities


class brotliCompressionB85Pickle(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        serialized_data = pickle.dumps((mzs, intensities))
        return base64.b85encode(brotli.compress(serialized_data)).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        decompressed_data = brotli.decompress(base64.b85decode(s))
        mzs, intensities = pickle.loads(decompressed_data)
        return mzs, intensities


class RoundingCompression(BaseCompressionStrategy):
    def __init__(self, mz_precision=4, intensity_precision=2):
        self.mz_precision = mz_precision
        self.intensity_precision = intensity_precision

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        rounded_mzs = str([round(mz, self.mz_precision) for mz in mzs])
        rounded_intensities = str([round(intensity, self.intensity_precision) for intensity in intensities])
        return json.dumps((rounded_mzs, rounded_intensities))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        return eval(mz_str), eval(intensity_str)


class UrlRoundingCompression(BaseCompressionStrategy):
    def __init__(self, mz_precision=4, intensity_precision=2):
        self.mz_precision = mz_precision
        self.intensity_precision = intensity_precision

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        rounded_mzs = ';'.join([str(round(mz, self.mz_precision)) for mz in mzs])
        rounded_intensities = ';'.join([str(round(intensity, self.intensity_precision)) for intensity in intensities])
        return json.dumps((rounded_mzs, rounded_intensities))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)
        mzs = [float(mz) for mz in mz_str.split(';')]
        intensities = [float(intensity) for intensity in intensity_str.split(';')]
        return mzs, intensities


class MzIntensityDoubleStringDeltaCompressionBrotliUrl(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzIntensityDoubleStringDeltaCompression().compress(mzs, intensities)
        serialized_data = pickle.dumps(s)
        compressed_data = brotli.compress(serialized_data)
        return base64.urlsafe_b64encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        decoded_data = base64.urlsafe_b64decode(s)
        decompressed_data = brotli.decompress(decoded_data)
        s = pickle.loads(decompressed_data)
        mzs, intensities = MzIntensityDoubleStringDeltaCompression().decompress(s)
        return mzs, intensities


class MzSingleStringDeltaCompressionIntensityHexSeparate(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_str = hex_encode(intensities)

        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)

        mzs = list(delta_decode_single_string(mz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class MzSingleStringDeltaCompressionIntensityHexSeparateBrotliB85(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_str = hex_encode(intensities)
        mz_str_compressed = brotli.compress(mz_str.encode('utf-8'))
        intensity_str_compressed = brotli.compress(intensity_str.encode('utf-8'))

        mz_str_compressed = base64.b85encode(mz_str_compressed).decode('utf-8')
        intensity_str_compressed = base64.b85encode(intensity_str_compressed).decode('utf-8')

        return json.dumps((mz_str_compressed, intensity_str_compressed))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str_compressed, intensity_str_compressed = json.loads(s)

        mz_str_compressed = base64.b85decode(mz_str_compressed)
        intensity_str_compressed = base64.b85decode(intensity_str_compressed)

        mz_str = brotli.decompress(mz_str_compressed).decode('utf-8')
        intensity_str = brotli.decompress(intensity_str_compressed).decode('utf-8')
        mzs = list(delta_decode_single_string(mz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class MzSingleStringDeltaCompressionIntensityHexSeparateBrotliUrl(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_str = hex_encode(intensities)

        mz_str_compressed = brotli.compress(mz_str.encode('utf-8'))
        intensity_str_compressed = brotli.compress(intensity_str.encode('utf-8'))

        mz_str_compressed = base64.urlsafe_b64encode(mz_str_compressed).decode('utf-8')
        intensity_str_compressed = base64.urlsafe_b64encode(intensity_str_compressed).decode('utf-8')

        return json.dumps((mz_str_compressed, intensity_str_compressed))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str_compressed, intensity_str_compressed = json.loads(s)

        mz_str_compressed = base64.urlsafe_b64decode(mz_str_compressed)
        intensity_str_compressed = base64.urlsafe_b64decode(intensity_str_compressed)

        mz_str = brotli.decompress(mz_str_compressed).decode('utf-8')
        intensity_str = brotli.decompress(intensity_str_compressed).decode('utf-8')

        mzs = list(delta_decode_single_string(mz_str))
        intensities = list(hex_decode(intensity_str))

        return mzs, intensities


class MzIntensityHexSeparate(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = hex_encode(mzs)
        intensity_str = hex_encode(intensities)

        return json.dumps((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = json.loads(s)

        mzs = list(hex_decode(mz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class MzIntensityHexSeparateBrotliB85(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = hex_encode(mzs)
        intensity_str = hex_encode(intensities)

        mz_str_compressed = brotli.compress(mz_str.encode('utf-8'))
        intensity_str_compressed = brotli.compress(intensity_str.encode('utf-8'))

        mz_str_compressed = base64.b85encode(mz_str_compressed).decode('utf-8')
        intensity_str_compressed = base64.b85encode(intensity_str_compressed).decode('utf-8')

        return json.dumps((mz_str_compressed, intensity_str_compressed))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str_compressed, intensity_str_compressed = json.loads(s)

        mz_str_compressed = base64.b85decode(mz_str_compressed)
        intensity_str_compressed = base64.b85decode(intensity_str_compressed)

        mz_str = brotli.decompress(mz_str_compressed).decode('utf-8')
        intensity_str = brotli.decompress(intensity_str_compressed).decode('utf-8')
        mzs = list(hex_decode(mz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class MzIntensityHexSeparateBrotliUrl(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = hex_encode(mzs)
        intensity_str = hex_encode(intensities)

        mz_str_compressed = brotli.compress(mz_str.encode('utf-8'))
        intensity_str_compressed = brotli.compress(intensity_str.encode('utf-8'))

        mz_str_compressed = base64.urlsafe_b64encode(mz_str_compressed).decode('utf-8')
        intensity_str_compressed = base64.urlsafe_b64encode(intensity_str_compressed).decode('utf-8')

        return json.dumps((mz_str_compressed, intensity_str_compressed))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str_compressed, intensity_str_compressed = json.loads(s)

        mz_str_compressed = base64.urlsafe_b64decode(mz_str_compressed)
        intensity_str_compressed = base64.urlsafe_b64decode(intensity_str_compressed)

        mz_str = brotli.decompress(mz_str_compressed).decode('utf-8')
        intensity_str = brotli.decompress(intensity_str_compressed).decode('utf-8')

        mzs = list(hex_decode(mz_str))
        intensities = list(hex_decode(intensity_str))

        return mzs, intensities
