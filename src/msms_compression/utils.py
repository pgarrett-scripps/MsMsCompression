import struct
import urllib
from typing import Generator, List

def leading_zero_compression(s: str, chunk_size=1000) -> str:
    compressed_chunks = []
    for i in range(0, len(s), chunk_size):
        chunk = s[i:i + chunk_size]
        compressed_chunk = hex(int('1' + chunk))[2:]
        compressed_chunks.append(compressed_chunk)
    return ','.join(compressed_chunks)

def leading_zero_decompression(s: str) -> str:
    decompressed_chunks = []
    for chunk in s.split(','):
        decompressed_chunk = str(int(chunk, 16))[1:]
        decompressed_chunks.append(decompressed_chunk)
    return ''.join(decompressed_chunks)


def float_to_hex(f: float) -> str:
    """Convert a floating point number to its hexadecimal representation."""
    return format(struct.unpack('!I', struct.pack('!f', f))[0], '08x')


def hex_to_float(s: str) -> float:
    """Convert a hexadecimal number to its floating-point representation."""
    return struct.unpack('!f', struct.pack('!I', int(s, 16)))[0]


def encode_leading_zero(lz: int) -> chr:
    if 0 <= lz < 16:
        return hex(lz)[-1]
    else:
        raise ValueError("Value must be between 0 and 15 (inclusive)")


def decode_leading_zero(lz: chr) -> int:
    return int(lz, 16)


def hex_delta(a: str, b: str) -> str:
    """Calculate differences between adjacent hexadecimal values."""
    diff = int(a, 16) - int(b, 16)
    return format(diff & 0xFFFFFFFF, '08x')


def hex_delta_rev(a: str, b: str) -> str:
    """Calculate differences between adjacent hexadecimal values."""
    diff = int(a, 16) + int(b, 16)
    return format(diff & 0xFFFFFFFF, '08x')


def count_leading_zeros(s: str) -> int:
    """Count the number of leading zeros in each hexadecimal difference."""
    return len(s) - len(s.lstrip('0'))


def delta_encode(vals: List[float]) -> (str, str):
    """Encode a list of m/z values using a delta encoding scheme and return the encoded values."""
    mzs_hex = [float_to_hex(mz) for mz in vals]

    initial_hex_value = mzs_hex[0]
    initial_hex_value_zeros = count_leading_zeros(initial_hex_value)

    mzs_hex_deltas = [hex_delta(mzs_hex[i], mzs_hex[i - 1]) for i in range(1, len(mzs_hex))]
    leading_zeros = [count_leading_zeros(hex) for hex in mzs_hex_deltas]

    hex_delta_str = initial_hex_value.lstrip('0') + \
                    ''.join(delta.lstrip('0') for delta in mzs_hex_deltas)
    leading_zero_str = encode_leading_zero(initial_hex_value_zeros) \
                       + ''.join([encode_leading_zero(lz) for lz in leading_zeros])
    return hex_delta_str, leading_zero_str


def delta_decode(delta_str: str, lz_str: str) -> Generator[float, None, None]:
    initial_lz = decode_leading_zero(lz_str[0])
    lz_str = lz_str[1:]
    initial_hex = '0' * initial_lz + delta_str[:8 - initial_lz]
    delta_str = delta_str[8 - initial_lz:]
    yield hex_to_float(initial_hex)

    curr_value = initial_hex
    while lz_str != '':
        lz = decode_leading_zero(lz_str[0])
        lz_str = lz_str[1:]

        hex_diff = '0' * lz + delta_str[:8 - lz]
        hex = hex_delta_rev(curr_value, hex_diff)
        curr_value = hex

        delta_str = delta_str[8 - lz:]

        yield hex_to_float(hex)


def delta_encode_single(vals: List[float], ints: List[float]) -> (str, str):
    """Encode a list of m/z values using a delta encoding scheme and return the encoded values."""
    mzs_hex = [float_to_hex(mz) for mz in vals]

    initial_hex_value = mzs_hex[0]
    initial_hex_value_zeros = count_leading_zeros(initial_hex_value)

    ints_hex = [float_to_hex(i) for i in ints]

    mzs_hex_deltas = [hex_delta(mzs_hex[i], mzs_hex[i - 1]) for i in range(1, len(mzs_hex))]
    leading_zeros = [count_leading_zeros(hex) for hex in mzs_hex_deltas]

    mz_ints = []
    for i in range(len(mzs_hex_deltas)):
        mz_ints.append(ints_hex[i])
        mz_ints.append(mzs_hex_deltas[i].lstrip('0'))

    mz_ints.append(ints_hex[-1])

    hex_delta_str = initial_hex_value.lstrip('0') + ''.join(mz_ints)
    leading_zero_str = encode_leading_zero(initial_hex_value_zeros) \
                       + ''.join([encode_leading_zero(lz) for lz in leading_zeros])
    return hex_delta_str, leading_zero_str


def delta_decode_single(delta_str: str, lz_str: str) -> Generator[float, None, None]:
    initial_lz = decode_leading_zero(lz_str[0])
    lz_str = lz_str[1:]
    initial_hex = '0' * initial_lz + delta_str[:8 - initial_lz]
    delta_str = delta_str[8 - initial_lz:]
    yield hex_to_float(initial_hex)

    initial_int_hex = delta_str[:8]
    yield hex_to_float(initial_int_hex)
    delta_str = delta_str[8:]

    curr_value = initial_hex
    while lz_str != '':
        lz = decode_leading_zero(lz_str[0])
        lz_str = lz_str[1:]

        hex_diff = '0' * lz + delta_str[:8 - lz]
        hex = hex_delta_rev(curr_value, hex_diff)
        curr_value = hex

        delta_str = delta_str[8 - lz:]

        yield hex_to_float(hex)

        int_hex = delta_str[:8]
        delta_str = delta_str[8:]
        yield hex_to_float(int_hex)

def delta_encode_single_string(vals: List[float]) -> str:
    hex_delta_str, leading_zero_str = delta_encode(vals)

    # compressed_leading_zero_str = leading_zero_compression(leading_zero_str[::-1])
    # print(len(compressed_leading_zero_str), len(leading_zero_str[::-1]))

    return hex_delta_str + leading_zero_str[::-1]


def delta_decode_single_string(s: str) -> Generator[float, None, None]:
    initial_lz = decode_leading_zero(s[-1])
    initial_hex = '0' * initial_lz + s[:8 - initial_lz]
    s = s[8 - initial_lz:-1]
    yield hex_to_float(initial_hex)

    curr_value = initial_hex
    while s:
        lz = decode_leading_zero(s[-1])
        hex_diff = '0' * lz + s[:8 - lz]

        hex = hex_delta_rev(curr_value, hex_diff)
        curr_value = hex

        s = s[8 - lz:-1]

        yield hex_to_float(hex)


def delta_encode_single_string2(vals: List[float], ints: List[float]) -> str:
    hex_delta_str, leading_zero_str = delta_encode_single(vals, ints)

    # compressed_leading_zero_str = leading_zero_compression(leading_zero_str[::-1])
    # print(len(compressed_leading_zero_str), len(leading_zero_str[::-1]))

    return hex_delta_str + leading_zero_str[::-1]


def delta_decode_single_string2(s: str) -> Generator[float, None, None]:

    initial_lz = decode_leading_zero(s[-1])
    initial_hex = '0' * initial_lz + s[:8 - initial_lz]
    s = s[8 - initial_lz:-1]
    yield hex_to_float(initial_hex)

    yield hex_to_float(s[:8])
    s = s[8:]

    curr_value = initial_hex
    while s:

        lz = decode_leading_zero(s[-1])
        hex_diff = '0' * lz + s[:8 - lz]

        hex = hex_delta_rev(curr_value, hex_diff)
        curr_value = hex

        s = s[8 - lz:-1]

        yield hex_to_float(hex)


        yield hex_to_float(s[:8])
        s = s[8:]


def hex_encode(intensities: List[float]) -> str:
    intensities_hex = [float_to_hex(intensity) for intensity in intensities]
    return ''.join(intensities_hex)


def hex_decode(s: str) -> Generator[float, None, None]:
    while s:
        hex = s[:8]
        intensity = hex_to_float(hex)
        s = s[8:]
        yield intensity


def url_encode_spectrum(mz_array: List[float], intensity_array: List[float]) -> str:
    return urllib.parse.urlencode(
        {'mz': delta_encode_single_string(mz_array),
         'i': hex_encode(intensity_array)
         }
    )


def dumb_encode_spectrum(mz_array: List[float], intensity_array: List[float]) -> str:
    rounded_mzs = ''.join([str(round(mz, 4)) for mz in mz_array])
    rounded_intensities = ''.join([str(round(intensity, 2)) for intensity in intensity_array])
    return urllib.parse.urlencode(
        {'mz': rounded_mzs,
         'i': rounded_intensities
         }
    )


def encode_indexes(indexes: List[int]) -> str:
    """
    Encode as a uint16 array
    :param indexes:
    :return:
    """
    return ''.join([format(index, '04x') for index in indexes])


def decode_indexes(s: str) -> Generator[int, None, None]:
    while s:
        index = int(s[:4], 16)
        s = s[4:]
        yield index
