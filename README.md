# DiskWala URL to MP4 Converter API

A FastAPI service that extracts the direct MP4 video URL from any DiskWala share link.

## Deploy on Render

1. Push this code to a GitHub repository.
2. On Render.com, create a new **Web Service** and connect your repo.
3. Use the following settings:
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables** (optional):
     - `REQUEST_TIMEOUT=10`

## Usage

Send a POST request to `/api/extract` with JSON:

```json
{
  "url": "https://www.diskwala.com/app/6a9ad1b306ba7ea03dc09688"
}
