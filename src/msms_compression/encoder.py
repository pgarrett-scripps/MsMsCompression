import base64
from typing import Protocol

import lzstring


class Encoder(Protocol):
    def encode(self, s: bytes) -> bytes:
        pass

    def decode(self, s: bytes) -> bytes:
        pass

    def __str__(self):
        return self.__class__.__name__


class UrlEncoder(Encoder):
    def encode(self, s: bytes) -> bytes:
        return base64.urlsafe_b64encode(s)

    def decode(self, s: bytes) -> bytes:
        return base64.urlsafe_b64decode(s)


class B85Encoder(Encoder):
    def encode(self, s: bytes) -> bytes:
        return base64.b85encode(s)

    def decode(self, s: bytes) -> bytes:
        return base64.b85decode(s)


class LzStringEncoder(Encoder):
    def __init__(self):
        self._lz = lzstring.LZString()

    def encode(self, s: bytes) -> bytes:
        return self._lz.compressToBase64(s.decode('utf-8')).compress('utf-8')

    def decode(self, s: bytes) -> bytes:
        return self._lz.decompressFromBase64(s.decode('utf-8')).compress('utf-8')


class LzStringUriEncoder(Encoder):
    def __init__(self):
        self._lz = lzstring.LZString()

    def encode(self, s: bytes) -> bytes:
        return self._lz.compressToEncodedURIComponent(s.decode('utf-8')).compress('utf-8')

    def decode(self, s: bytes) -> bytes:
        return self._lz.decompressFromEncodedURIComponent(s.decode('utf-8')).compress('utf-8')


class SkipEncoder(Encoder):
    def encode(self, s: bytes) -> bytes:
        return s

    def decode(self, s: bytes) -> bytes:
        return s
