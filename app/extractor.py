import re
import httpx
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from app.config import Config

class DiskWalaExtractor:
    def __init__(self):
        self.client = httpx.AsyncClient(
            timeout=Config.REQUEST_TIMEOUT,
            headers={
                "User-Agent": Config.USER_AGENT,
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                "Accept-Language": "en-US,en;q=0.9",
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
                "message": "Could not extract file ID."
            }

        # Step 1: Visit the share page to get cookies and session
        try:
            page_resp = await self.client.get(share_url, follow_redirects=True)
            if page_resp.status_code != 200:
                return {"success": False, "error": "Page not accessible"}
        except Exception as e:
            return {"success": False, "error": str(e)}

        # Step 2: Parse HTML for video URL
        soup = BeautifulSoup(page_resp.text, "html.parser")

        # Check <video> tag
        video_tag = soup.find("video")
        if video_tag and video_tag.get("src"):
            return {"success": True, "data": {"video_url": video_tag["src"]}}

        # Check <source> tag
        source_tag = soup.find("source")
        if source_tag and source_tag.get("src"):
            return {"success": True, "data": {"video_url": source_tag["src"]}}

        # Search inside <script> tags for .mp4 URLs
        scripts = soup.find_all("script")
        for script in scripts:
            if script.string:
                match = re.search(r'(https?://[^\s"\']+\.mp4[^\s"\']*)', script.string)
                if match:
                    return {"success": True, "data": {"video_url": match.group(1)}}

        # Step 3: If HTML parsing fails, try the metadata API (if accessible)
        api_url = "https://dudadapid.diskwala.com/api/v1/file/temp_info"
        try:
            api_resp = await self.client.post(api_url, json={"id": file_id})
            if api_resp.status_code == 200:
                data = api_resp.json()
                # Look for download URL in known keys – adjust based on actual response
                for key in ["downloadUrl", "url", "video_url", "streamUrl"]:
                    if key in data and data[key]:
                        return {"success": True, "data": {"video_url": data[key]}}
                if "data" in data and isinstance(data["data"], dict):
                    for key in ["downloadUrl", "url"]:
                        if key in data["data"] and data["data"][key]:
                            return {"success": True, "data": {"video_url": data["data"][key]}}
        except:
            pass

        # Final fallback: return the original URL with a warning
        return {
            "success": True,
            "data": {
                "video_url": share_url,
                "warning": "Could not find a direct video URL. Open this link in a browser or app."
            }
        }

    def _extract_file_id(self, url: str) -> Optional[str]:
        match = re.search(r"diskwala\.com/app/([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None

    async def close(self):
        await self.client.aclose()
