from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from typing import List, Union

# Import your compression strategies
from msms_compression import (
    MsMsUrlCompressor,
    MsMsB85Compressor,
)

app = FastAPI()


class SpectrumData(BaseModel):
    mzs: List[float]
    intensities: List[float]


class CompressedData(BaseModel):
    compressed_data: str


@app.post("/compress/url", status_code=200)
def compress_url(data: SpectrumData):
    compressor = MsMsUrlCompressor()
    try:
        compressed_data = compressor.compress(data.mzs, data.intensities)
        return {"compressed_data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decompress/url", status_code=200)
def decompress_url(data: CompressedData):
    compressor = MsMsUrlCompressor()
    try:
        mzs, intensities = compressor.decompress(data.compressed_data)
        return {"mzs": mzs, "intensities": intensities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compress/b85", status_code=200)
def compress_b85(data: SpectrumData):
    compressor = MsMsB85Compressor()
    try:
        compressed_data = compressor.compress(data.mzs, data.intensities)
        return {"compressed_data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decompress/b85", status_code=200)
def decompress_b85(data: CompressedData):
    compressor = MsMsB85Compressor()
    try:
        mzs, intensities = compressor.decompress(data.compressed_data)
        return {"mzs": mzs, "intensities": intensities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


handler = Mangum(app)
