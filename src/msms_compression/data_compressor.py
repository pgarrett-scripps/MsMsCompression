from typing import Protocol
import brotli
import gzip


class DataCompressor(Protocol):
    def compress(self, s: bytes) -> bytes:
        pass

    def decompress(self, s: bytes) -> bytes:
        pass

    def __str__(self):
        return self.__class__.__name__


class BrotliCompressor(DataCompressor):
    def compress(self, s: bytes) -> bytes:
        return brotli.compress(s)

    def decompress(self, s: bytes) -> bytes:
        return brotli.decompress(s)


class GzipCompressor(DataCompressor):
    def compress(self, s: bytes) -> bytes:
        return gzip.compress(s)

    def decompress(self, s: bytes) -> bytes:
        return gzip.decompress(s)


class SkipCompressor(DataCompressor):
    def compress(self, s: bytes) -> bytes:
        return s

    def decompress(self, s: bytes) -> bytes:
        return s
