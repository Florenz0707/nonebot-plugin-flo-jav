import re
from typing import Optional

from nonebot.log import logger

from ..model import AVInfo
from .SourceBase import SourceBase


class Avtoday(SourceBase):
    """Avtoday下载器"""

    def __init__(self, proxy: Optional[str] = None,
                 timeout: int = 15,
                 cookie_retry_times: int = 5,
                 query_retry_times: int = 5,
                 retry_interval: float = 0.5):
        super().__init__(proxy, timeout, cookie_retry_times, query_retry_times, retry_interval)
        self.domain = "avtoday.io"

    def get_source_name(self) -> str:
        return "avtoday"

    async def get_html(self, avid: str) -> Optional[str]:
        avid_upper = avid.upper()
        urls = [
            f"https://{self.domain}/video/{avid_upper}",
        ]
        for url in urls:
            content = await self.fetch_html(url)
            if content:
                logger.info(f"成功获取avtoday页面: {avid.upper()}")
                return content
        return None

    def parse_html(self, avid: str, html: str) -> Optional[AVInfo]:
        info = AVInfo()
        try:
            # 提取标题
            title = None
            title_patterns = [
                r'<meta property="og:title" content="([^"]+)"',
                r'<span>标题:</span>\s*<span>([^<]+)</span>',
            ]
            for pattern in title_patterns:
                match = re.search(pattern, html)
                if match:
                    title = match.group(1).strip()
                    logger.debug(f"Title: {title}")
                    break
            if title is None:
                return None

            # 提取封面url
            image_url = None
            image_url_patterns = [
                r'<meta property="og:image" content="([^"]+)"',
            ]
            for pattern in image_url_patterns:
                match = re.search(pattern, html)
                if match:
                    image_url = match.group(1).strip()
                    logger.debug(f"Image URL: {image_url}")
                    break
            if image_url is None:
                return None

            info.update_from_source({
                "source": self.get_source_name(),
                "title": title,
                "avid": avid,
                "image_url": image_url,
            })

            return info
        except Exception as e:
            logger.error(f"Avtoday解析失败: {e}")
            return None
