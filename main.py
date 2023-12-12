from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from typing import List

# Import your compression strategies
from msms_compression import (
    SpectrumCompressor,
    SpectrumCompressorUrl,
)

app = FastAPI()


class SpectrumData(BaseModel):
    mzs: List[float]
    intensities: List[float]


class CompressedData(BaseModel):
    compressed_data: str


@app.post("/compress/url", status_code=200)
def compress_url(data: SpectrumData):
    compressor = SpectrumCompressorUrl()
    try:
        compressed_data = compressor.compress(data.mzs, data.intensities)
        return {"compressed_data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decompress/url", status_code=200)
def decompress_url(data: CompressedData):
    compressor = SpectrumCompressorUrl()
    try:
        mzs, intensities = compressor.decompress(data.compressed_data)
        return {"mzs": mzs, "intensities": intensities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compress", status_code=200)
def compress(data: SpectrumData):
    compressor = SpectrumCompressor()
    try:
        compressed_data = compressor.compress(data.mzs, data.intensities)
        return {"compressed_data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decompress", status_code=200)
def decompress(data: CompressedData):
    compressor = SpectrumCompressor()
    try:
        mzs, intensities = compressor.decompress(data.compressed_data)
        return {"mzs": mzs, "intensities": intensities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


handler = Mangum(app)
