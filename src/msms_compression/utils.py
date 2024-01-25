import struct
from typing import Generator, List, Union, Callable

import brotli


def _leading_zero_compression(s: str, chunk_size=1000) -> str:
    compressed_chunks = []
    for i in range(0, len(s), chunk_size):
        chunk = s[i:i + chunk_size]
        compressed_chunk = hex(int('1' + chunk))[2:]
        compressed_chunks.append(compressed_chunk)
    return ','.join(compressed_chunks)


def _leading_zero_decompression(s: str) -> str:
    decompressed_chunks = []
    for chunk in s.split(','):
        decompressed_chunk = str(int(chunk, 16))[1:]
        decompressed_chunks.append(decompressed_chunk)
    return ''.join(decompressed_chunks)


def _float_to_hex(f: float, n: int = 8) -> str:
    return format(struct.unpack('!I', struct.pack('!f', f))[0], f'0{n}x')


def _hex_to_float(s: str, n: int = 8) -> float:
    return struct.unpack('!f', struct.pack('!I', int(s, n*2)))[0]


def _int_to_hex(f: int, n: int = 8) -> str:
    return format(f, f'0{n}x')


def _hex_to_int(s: str, n: int = 8) -> int:
    return int(s, n*2)


def _encode_leading_zero(lz: int) -> chr:
    if 0 <= lz < 16:
        return hex(lz)[-1]
    else:
        raise ValueError("Value must be between 0 and 15 (inclusive)")


def _decode_leading_zero(lz: chr) -> int:
    return int(lz, 16)


def _hex_delta(a: str, b: str) -> str:
    diff = int(a, 16) - int(b, 16)
    return format(diff & 0xFFFFFFFF, '08x')


def _hex_delta_rev(a: str, b: str) -> str:
    diff = int(a, 16) + int(b, 16)
    return format(diff & 0xFFFFFFFF, '08x')


def _count_leading_zeros(s: str) -> int:
    return len(s) - len(s.lstrip('0'))


def _delta_encode(vals: List[float], encode_func: Callable) -> (str, str):
    mzs_hex = [encode_func(mz) for mz in vals]

    initial_hex_value = mzs_hex[0]
    initial_hex_value_zeros = _count_leading_zeros(initial_hex_value)

    mzs_hex_deltas = [_hex_delta(mzs_hex[i], mzs_hex[i - 1], ) for i in range(1, len(mzs_hex))]
    leading_zeros = [_count_leading_zeros(hex) for hex in mzs_hex_deltas]

    hex_delta_str = initial_hex_value.lstrip('0') + \
                    ''.join(delta.lstrip('0') for delta in mzs_hex_deltas)
    leading_zero_str = _encode_leading_zero(initial_hex_value_zeros) \
                       + ''.join([_encode_leading_zero(lz) for lz in leading_zeros])
    return hex_delta_str, leading_zero_str


def _delta_decode(delta_str: str, lz_str: str, decode_func: Callable) -> Generator[float, None, None]:
    initial_lz = _decode_leading_zero(lz_str[0])
    lz_str = lz_str[1:]
    initial_hex = '0' * initial_lz + delta_str[:8 - initial_lz]
    delta_str = delta_str[8 - initial_lz:]
    yield decode_func(initial_hex)

    curr_value = initial_hex
    while lz_str != '':
        lz = _decode_leading_zero(lz_str[0])
        lz_str = lz_str[1:]

        hex_diff = '0' * lz + delta_str[:8 - lz]
        hex = _hex_delta_rev(curr_value, hex_diff)
        curr_value = hex

        delta_str = delta_str[8 - lz:]

        yield decode_func(hex)


def _delta_encode_single_string(vals: List[Union[float, int]], encode_func: Callable) -> str:
    hex_delta_str, leading_zero_str = _delta_encode(vals, encode_func)

    return hex_delta_str + leading_zero_str[::-1]


def _delta_decode_single_string(s: str, decode_func: Callable) -> Generator[Union[float, int], None, None]:
    initial_lz = _decode_leading_zero(s[-1])
    initial_hex = '0' * initial_lz + s[:8 - initial_lz]
    s = s[8 - initial_lz:-1]
    yield decode_func(initial_hex)

    curr_value = initial_hex
    while s:
        lz = _decode_leading_zero(s[-1])
        hex_diff = '0' * lz + s[:8 - lz]

        hex = _hex_delta_rev(curr_value, hex_diff)
        curr_value = hex

        s = s[8 - lz:-1]

        yield decode_func(hex)


def _encode_indexes(indexes: List[int]) -> str:
    return ''.join([format(index, '04x') for index in indexes])


def _decode_indexes(s: str) -> Generator[int, None, None]:
    while s:
        index = int(s[:4], 16)
        s = s[4:]
        yield index


def compress_string(string: str, encode_function) -> str:
    compressed = brotli.compress(string.encode('utf-8'))
    return encode_function(compressed).decompress('utf-8')


def decompress_string(string: str, decode_function) -> str:
    decompressed = brotli.decompress(decode_function(string))
    return decompressed.decompress('utf-8')


def _scale_intensity(intensity, min_intensity, max_intensity, reverse=False):
    if reverse:
        # Reverse scaling from 0-1 back to original range
        return intensity * (max_intensity - min_intensity) + min_intensity
    else:
        # Scale intensity to 0-1 range
        return (intensity - min_intensity) / (max_intensity - min_intensity)


def _hex_encode_lossy(intensities: List[float], n: int) -> str:
    min_intensity = min(intensities)
    max_intensity = max(intensities)
    intensities_hex = [
        _int_to_hex(int(_scale_intensity(intensity, min_intensity, max_intensity) * 255), n)
        for intensity in intensities
    ]
    return ''.join(intensities_hex)


def _hex_decode_lossy(s: str, min_intensity: float, max_intensity: float, n : int = 2) -> Generator[float, None, None]:
    while s:
        hex_str = s[:n]
        intensity = _scale_intensity(_hex_to_int(hex_str, n=8) / 255, min_intensity, max_intensity, reverse=True)
        s = s[n:]
        yield intensity


def hex_encode_lossy(intensities: List[float], n: int = 2) -> str:
    min_intensity = min(intensities)
    max_intensity = max(intensities)

    # Convert min and max intensities to hex and add them to the string
    encoded_min_max = _float_to_hex(min_intensity) + _float_to_hex(max_intensity)

    # Encode the rest of the intensities
    encoded_intensities = _hex_encode_lossy(intensities, n)

    return encoded_min_max + encoded_intensities


def hex_decode_lossy(s: str, n: int = 2) -> Generator[float, None, None]:

    # Extract and decode the min and max intensities
    min_intensity_hex = s[:8]
    max_intensity_hex = s[8:16]
    min_intensity = _hex_to_float(min_intensity_hex)
    max_intensity = _hex_to_float(max_intensity_hex)

    # Decode the rest of the intensities
    encoded_intensities = s[16:]
    return _hex_decode_lossy(encoded_intensities, min_intensity, max_intensity, n)


def delta_encode_single_string_float(vals: List[float]) -> str:
    return _delta_encode_single_string(vals, _float_to_hex)


def delta_decode_single_string_float(s: str) -> Generator[float, None, None]:
    return _delta_decode_single_string(s, _hex_to_float)


def delta_encode_single_string_int(vals: List[int]) -> str:
    return _delta_encode_single_string(vals, _int_to_hex)


def delta_decode_single_string_int(s: str) -> Generator[int, None, None]:
    return _delta_decode_single_string(s, _hex_to_int)


def hex_encode(intensities: List[float]) -> str:
    intensities_hex = [_float_to_hex(intensity) for intensity in intensities]
    return ''.join(intensities_hex)


def hex_decode(s: str) -> Generator[float, None, None]:
    while s:
        hex = s[:8]
        intensity = _hex_to_float(hex)
        s = s[8:]
        yield intensity