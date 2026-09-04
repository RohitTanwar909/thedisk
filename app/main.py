from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.models import ExtractRequest, ExtractResponse, VideoData
from app.extractor import DiskWalaExtractor

extractor = DiskWalaExtractor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await extractor.close()

app = FastAPI(
    title="DiskWala URL to MP4 Converter API",
    description="Extract video URLs from DiskWala share links using the official backend API",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "service": "DiskWala URL to MP4 Converter",
        "endpoints": {
            "extract": "POST /api/extract"
        }
    }

@app.post("/api/extract", response_model=ExtractResponse)
async def extract_video(request: ExtractRequest):
    result = await extractor.extract_video_url(str(request.url))
    if not result.get("success"):
        raise HTTPException(
            status_code=400,
            detail=result.get("message", "Extraction failed")
        )
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
