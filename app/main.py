from fastapi import FastAPI, HTTPException, Query
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
    description="Extract video URLs from DiskWala share links",
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
            "extract": "GET /extract?url=<diskwala_link>",
            "extract_post": "POST /api/extract (JSON body)"
        }
    }

# GET endpoint – URL-based
@app.get("/extract")
async def extract_video_get(url: str = Query(..., description="DiskWala share URL")):
    result = await extractor.extract_video_url(url)
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Extraction failed"))
    return result

# POST endpoint – JSON body (original)
@app.post("/api/extract")
async def extract_video_post(request: ExtractRequest):
    result = await extractor.extract_video_url(str(request.url))
    if not result.get("success"):
        raise HTTPException(status_code=400, detail=result.get("message", "Extraction failed"))
    return result
