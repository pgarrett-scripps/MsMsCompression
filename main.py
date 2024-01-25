import hashlib

import aiosqlite
from fastapi import FastAPI, HTTPException
from mangum import Mangum
from pydantic import BaseModel
from typing import List

# Import your compression strategies
from msms_compression import SpectrumCompressorB85, SpectrumCompressorUrl

app = FastAPI()


class SpectrumData(BaseModel):
    mzs: List[float]
    intensities: List[float]


class CompressedData(BaseModel):
    compressed_data: str


compressor = SpectrumCompressorB85
compressor_url = SpectrumCompressorUrl

# Database setup
DB_FILE = "spectra.db"


async def init_db():
    async with aiosqlite.connect(DB_FILE) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS spectra (
                id TEXT PRIMARY KEY,
                compressed_data TEXT NOT NULL
            )
        """)
        await db.commit()

@app.on_event("startup")
async def startup_event():
    await init_db()


@app.post("/compress/url", status_code=200)
def compress_url(data: SpectrumData):
    try:
        compressed_data = compressor_url.compress(data.mzs, data.intensities)
        return {"compressed_data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decompress/url", status_code=200)
def decompress_url(data: CompressedData):
    try:
        mzs, intensities = compressor_url.decompress(data.compressed_data)
        return {"mzs": mzs, "intensities": intensities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/compress", status_code=200)
def compress(data: SpectrumData):
    try:
        # Sort the mzs and intensities together based on mzs
        sorted_pairs = sorted(zip(data.mzs, data.intensities), key=lambda pair: pair[0])
        sorted_mzs, sorted_intensities = zip(*sorted_pairs)

        compressed_data = compressor.compress(list(sorted_mzs), list(sorted_intensities))
        return {"compressed_data": compressed_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/decompress", status_code=200)
def decompress(data: CompressedData):
    try:
        mzs, intensities = compressor.decompress(data.compressed_data)
        return {"mzs": mzs, "intensities": intensities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


async def store_compressed_data(compressed_data: str) -> str:
    # Generate a key using a hash of the compressed data
    key = hashlib.sha256(compressed_data.encode()).hexdigest()

    async with aiosqlite.connect(DB_FILE) as db:
        # Check if the key already exists
        async with db.execute("SELECT 1 FROM spectra WHERE id = ?", (key,)) as cursor:
            if await cursor.fetchone() is None:
                # Insert new entry if key does not exist
                await db.execute("INSERT INTO spectra (id, compressed_data) VALUES (?, ?)", (key, compressed_data))
                await db.commit()

    return key


@app.post("/store", status_code=200)
async def store_spectrum(data: SpectrumData):
    try:
        # Sort the mzs and intensities together based on mzs
        sorted_pairs = sorted(zip(data.mzs, data.intensities), key=lambda pair: pair[0])
        sorted_mzs, sorted_intensities = zip(*sorted_pairs)
        # Compress the data first
        compressed_data = compressor.compress(sorted_mzs, sorted_intensities)
        # Then store the compressed data
        key = await store_compressed_data(compressed_data)
        return {"key": key}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/retrieve/{key}", status_code=200)
async def retrieve_spectrum(key: str):
    try:
        async with aiosqlite.connect(DB_FILE) as db:
            async with db.execute("SELECT compressed_data FROM spectra WHERE id = ?", (key,)) as cursor:
                row = await cursor.fetchone()
                if row is None:
                    raise HTTPException(status_code=404, detail="Key not found")

        compressed_data = row[0]
        mzs, intensities = compressor.decompress(compressed_data)
        return {"mzs": mzs, "intensities": intensities}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

handler = Mangum(app)
