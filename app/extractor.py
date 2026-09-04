import re
import httpx
import json
from typing import Dict, Any, Optional, List
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
        # List of possible API base URLs – the first one is from your screenshot
        self.api_bases = [
            "https://dudadapid.diskwala.com/api/v1",
            "https://dudaapi.diskwala.com/api/v1",
            "https://api.diskwala.com/api/v1",
            "https://www.diskwala.com/api/v1",
        ]

    async def extract_video_url(self, share_url: str) -> Dict[str, Any]:
        file_id = self._extract_file_id(share_url)
        if not file_id:
            return {
                "success": False,
                "error": "Invalid URL",
                "message": "Could not extract file ID from the share link."
            }

        for base in self.api_bases:
            metadata = await self._get_metadata(base, file_id)
            if metadata.get("success"):
                # We have metadata – try to get a real download URL from the same base
                download_url = await self._get_download_url(base, file_id)
                if download_url:
                    return {
                        "success": True,
                        "data": {
                            "video_url": download_url,
                            "title": metadata.get("name"),
                            "size": metadata.get("size"),
                            "type": metadata.get("type"),
                        }
                    }
                else:
                    # No download endpoint found – construct a fallback URL
                    fallback = f"{base}/file/stream/{file_id}"
                    return {
                        "success": True,
                        "data": {
                            "video_url": fallback,
                            "title": metadata.get("name"),
                            "size": metadata.get("size"),
                            "type": metadata.get("type"),
                            "warning": "Download endpoint not discovered. This constructed URL may require additional headers or a token."
                        }
                    }

        # If we exhausted all API bases
        return {
            "success": False,
            "error": "All API domains failed",
            "message": "Unable to reach DiskWala's backend. The service may be down or the API endpoints have changed."
        }

    def _extract_file_id(self, url: str) -> Optional[str]:
        # Matches https://www.diskwala.com/app/6a9ad1b306ba7ea03dc09688
        match = re.search(r"diskwala\.com/app/([a-f0-9]+)", url, re.IGNORECASE)
        return match.group(1) if match else None

    async def _get_metadata(self, base_url: str, file_id: str) -> Dict[str, Any]:
        """Fetch file info from /file/temp_info."""
        url = f"{base_url}/file/temp_info"
        payload = {"id": file_id}
        try:
            resp = await self.client.post(url, json=payload)
            if resp.status_code == 200:
                data = resp.json()
                info = data.get("fileInfo")
                if info:
                    return {
                        "success": True,
                        "name": info.get("name"),
                        "size": info.get("size"),
                        "type": info.get("type"),
                        "extension": info.get("extension"),
                    }
            return {"success": False}
        except Exception:
            return {"success": False}

    async def _get_download_url(self, base_url: str, file_id: str) -> Optional[str]:
        """Try several common download endpoints to get the signed URL."""
        endpoints = [
            f"{base_url}/file/download",
            f"{base_url}/file/getDownloadUrl",
            f"{base_url}/file/stream",
        ]
        payload = {"id": file_id}
        for endpoint in endpoints:
            try:
                resp = await self.client.post(endpoint, json=payload)
                if resp.status_code == 200:
                    data = resp.json()
                    # Look for a URL in various common keys
                    for key in ["downloadUrl", "url", "link", "video_url", "streamUrl"]:
                        if key in data and data[key]:
                            return data[key]
                    # Sometimes nested inside a 'data' object
                    if "data" in data and isinstance(data["data"], dict):
                        for key in ["downloadUrl", "url", "link"]:
                            if key in data["data"] and data["data"][key]:
                                return data["data"][key]
            except Exception:
                continue
        return None

    async def close(self):
        await self.client.aclose()
