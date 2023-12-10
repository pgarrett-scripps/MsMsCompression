import base64
import gzip
import pickle
from typing import List

import numpy as np

from .utils import delta_encode_single_string, hex_encode, delta_decode_single_string, hex_decode, delta_encode, \
    leading_zero_compression, leading_zero_decompression, delta_decode, encode_indexes, decode_indexes


class BaseCompressionStrategy:
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        raise NotImplementedError

    def decompress(self, s: str) -> (List[float], List[float]):
        raise NotImplementedError


class NoCompression(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        return str((mzs, intensities))

    def decompress(self, s: str) -> (List[float], List[float]):
        return eval(s)


class MzSingleStringDeltaCompressionIntensityHex(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_str = hex_encode(intensities)
        return str((mz_str, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = eval(s)
        mzs = list(delta_decode_single_string(mz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class MzDoubleStringDeltaCompressionIntensityHex(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str, lz_str = delta_encode(mzs)
        lz_str_hex = leading_zero_compression(lz_str)
        intensity_str = hex_encode(intensities)
        return str((mz_str, lz_str_hex, intensity_str))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, lz_str_hex, intensity_str = eval(s)
        lz_str = leading_zero_decompression(lz_str_hex)
        mzs = list(delta_decode(mz_str, lz_str))
        intensities = list(hex_decode(intensity_str))
        return mzs, intensities


class MzDoubleStringDeltaCompressionIntensityGzipUrl(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str, lz_str = delta_encode(mzs)
        lz_str_hex = leading_zero_compression(lz_str)
        serialized_intensity = pickle.dumps(intensities)
        compressed_intensity = gzip.compress(serialized_intensity)
        return str((mz_str, lz_str_hex, base64.urlsafe_b64encode(compressed_intensity).decode('utf-8')))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, lz_str_hex, intensity_str = eval(s)
        lz_str = leading_zero_decompression(lz_str_hex)
        mzs = list(delta_decode(mz_str, lz_str))
        decoded_data = base64.urlsafe_b64decode(intensity_str)
        decompressed_data = gzip.decompress(decoded_data)
        intensities = pickle.loads(decompressed_data)
        return mzs, intensities


class MzDoubleStringDeltaCompressionGzipUrl(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzDoubleStringDeltaCompressionIntensityHex().compress(mzs, intensities)
        serialized_data = pickle.dumps(s)
        compressed_data = gzip.compress(serialized_data)
        return base64.urlsafe_b64encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        decoded_data = base64.urlsafe_b64decode(s)
        decompressed_data = gzip.decompress(decoded_data)
        s = pickle.loads(decompressed_data)
        mzs, intensities = MzDoubleStringDeltaCompressionIntensityHex().decompress(s)
        return mzs, intensities


class MzDoubleStringDeltaCompressionGzipB85(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        initial_compressed = MzDoubleStringDeltaCompressionIntensityHex().compress(mzs, intensities)
        serialized_data = pickle.dumps(initial_compressed)
        gzip_compressed_data = gzip.compress(serialized_data)
        return base64.b85encode(gzip_compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        gzip_decompressed_data = gzip.decompress(base64.b85decode(s))
        initial_compressed = pickle.loads(gzip_decompressed_data)
        mzs, intensities = MzDoubleStringDeltaCompressionIntensityHex().decompress(initial_compressed)
        return mzs, intensities


class MzIntensitySingleStringDeltaCompression(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str = delta_encode_single_string(mzs)
        intensity_indexes = list(np.argsort(intensities))
        encoded_indexes = encode_indexes(intensity_indexes)
        intensities = np.array(intensities)[intensity_indexes]
        intensity_str = delta_encode_single_string(intensities)
        return str((mz_str, intensity_str, encoded_indexes))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str, encoded_indexes = eval(s)
        mzs = list(delta_decode_single_string(mz_str))
        decoded_intensities = list(delta_decode_single_string(intensity_str))
        indexes = list(decode_indexes(encoded_indexes))
        original_intensities = np.empty_like(decoded_intensities)
        original_intensities[indexes] = decoded_intensities
        return mzs, list(original_intensities)


class MzIntensityDoubleStringDeltaCompression(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        mz_str, lz_str = delta_encode(mzs)
        lz_str_hex = leading_zero_compression(lz_str)

        intensity_indexes = list(np.argsort(intensities))
        encoded_indexes = encode_indexes(intensity_indexes)
        intensities = np.array(intensities)[intensity_indexes]

        int_str, int_lz_str = delta_encode(intensities)
        int_lz_str_hex = leading_zero_compression(int_lz_str)

        return str((mz_str, lz_str_hex, int_str, int_lz_str_hex, encoded_indexes))

    def decompress(self, s: str) -> (List[float], List[float]):

        mz_str, lz_str_hex, int_str, int_lz_str_hex, encoded_indexes = eval(s)
        lz_str = leading_zero_decompression(lz_str_hex)
        mzs = list(delta_decode(mz_str, lz_str))

        int_lz_str = leading_zero_decompression(int_lz_str_hex)
        ints = list(delta_decode(int_str, int_lz_str))

        indexes = list(decode_indexes(encoded_indexes))
        original_intensities = np.empty_like(ints)
        original_intensities[indexes] = ints

        return mzs, list(original_intensities)


class MzIntensityDoubleStringDeltaCompressionGzipUrl(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzIntensityDoubleStringDeltaCompression().compress(mzs, intensities)
        serialized_data = pickle.dumps(s)
        compressed_data = gzip.compress(serialized_data)
        return base64.urlsafe_b64encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        decoded_data = base64.urlsafe_b64decode(s)
        decompressed_data = gzip.decompress(decoded_data)
        s = pickle.loads(decompressed_data)
        mzs, intensities = MzIntensityDoubleStringDeltaCompression().decompress(s)
        return mzs, intensities


class MzIntensityDoubleStringDeltaCompressionGzipB85(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        s = MzIntensityDoubleStringDeltaCompression().compress(mzs, intensities)
        serialized_data = pickle.dumps(s)
        compressed_data = gzip.compress(serialized_data)
        return base64.b85encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        decoded_data = base64.b85decode(s)
        decompressed_data = gzip.decompress(decoded_data)
        s = pickle.loads(decompressed_data)
        mzs, intensities = MzIntensityDoubleStringDeltaCompression().decompress(s)
        return mzs, intensities


class GzipCompression(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        serialized_data = pickle.dumps((mzs, intensities))
        return base64.b85encode(gzip.compress(serialized_data)).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        decompressed_data = gzip.decompress(base64.b85decode(s))
        mzs, intensities = pickle.loads(decompressed_data)
        return mzs, intensities


class GzipCompressionBase64(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        serialized_data = pickle.dumps((mzs, intensities))
        compressed_data = gzip.compress(serialized_data)
        return base64.b64encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        decoded_data = base64.b64decode(s)
        decompressed_data = gzip.decompress(decoded_data)
        mzs, intensities = pickle.loads(decompressed_data)
        return mzs, intensities


class GzipCompressionBase85(BaseCompressionStrategy):
    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        serialized_data = pickle.dumps((mzs, intensities))
        compressed_data = gzip.compress(serialized_data)
        return base64.b85encode(compressed_data).decode('utf-8')

    def decompress(self, s: str) -> (List[float], List[float]):
        decoded_data = base64.b85decode(s)
        decompressed_data = gzip.decompress(decoded_data)
        mzs, intensities = pickle.loads(decompressed_data)
        return mzs, intensities


class RoundingCompression(BaseCompressionStrategy):
    def __init__(self, mz_precision=4, intensity_precision=2):
        self.mz_precision = mz_precision
        self.intensity_precision = intensity_precision

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        rounded_mzs = [round(mz, self.mz_precision) for mz in mzs]
        rounded_intensities = [round(intensity, self.intensity_precision) for intensity in intensities]
        return str((rounded_mzs, rounded_intensities))

    def decompress(self, s: str) -> (List[float], List[float]):
        return eval(s)


class UrlRoundingCompression(BaseCompressionStrategy):
    def __init__(self, mz_precision=4, intensity_precision=2):
        self.mz_precision = mz_precision
        self.intensity_precision = intensity_precision

    def compress(self, mzs: List[float], intensities: List[float]) -> str:
        rounded_mzs = ';'.join([str(round(mz, self.mz_precision)) for mz in mzs])
        rounded_intensities = ';'.join([str(round(intensity, self.intensity_precision)) for intensity in intensities])
        return str((rounded_mzs, rounded_intensities))

    def decompress(self, s: str) -> (List[float], List[float]):
        mz_str, intensity_str = eval(s)
        mzs = [float(mz) for mz in mz_str.split(';')]
        intensities = [float(intensity) for intensity in intensity_str.split(';')]
        return mzs, intensities
