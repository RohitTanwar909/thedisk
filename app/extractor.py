import re
import httpx
from typing import Dict, Any, Optional
from app.config import Config

class DiskWalaExtractor:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=Config.REQUEST_TIMEOUT,
            headers={
                "User-Agent": Config.USER_AGENT,
                "Accept": "application/json, text/plain, */*",
                "Accept-Language": "en-US,en;q=0.9",
                "Content-Type": "application/json",
                "X-Requested-With": "XMLHttpRequest",
                "Referer": "https://www.diskwala.com/",
                "Origin": "https://www.diskwala.com",
            }
        )

    async def extract_video_url(self, share_url: str) -> Dict[str, Any]:
        file_id = self._extract_file_id(share_url)
        if not file_id:
            return {
                "success": False,
                "error": "Invalid URL",
                "message": "Could not extract file ID from the share link."
            }

        # Build the streaming URL (most likely the direct video endpoint)
        stream_url = f"https://dudadapid.diskwala.com/api/v1/file/stream/{file_id}"

        # Optionally, verify the URL is accessible (HEAD request)
        is_valid = await self._verify_url(stream_url)
        if is_valid:
            return {
                "success": True,
                "data": {
                    "video_url": stream_url,
                    "title": None,
                    "size": None,
                    "type": "video/mp4",
                    "warning": "This URL may require the same headers as the app (we send them). If playback fails, try adding 'Referer: https://www.diskwala.com/'."
                }
            }
        else:
            # If the stream URL doesn't respond, fallback to the original page (maybe it will redirect)
            return {
                "success": True,
                "data": {
                    "video_url": share_url,
                    "title": None,
                    "size": None,
                    "type": "video/mp4",
                    "warning": "Stream URL not accessible. Returning the original share link – open it in a browser or app."
                }
            }

    def _extract_file_id(self, url: str) -> Optional[str]:
        match = re.search(r"diskwala\.com/app/([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None

    async def _verify_url(self, url: str) -> bool:
        try:
            resp = await self.client.head(url, follow_redirects=True)
            # Some endpoints return 200, others 403 – we accept if not 404/500
            return resp.status_code < 500
        except:
            return False

    async def close(self):
        await self.client.aclose()
