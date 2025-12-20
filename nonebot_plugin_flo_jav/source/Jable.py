import re
from typing import Optional
from nonebot.log import logger

from .SourceBase import SourceBase
from ..model import AVInfo


class Jable(SourceBase):
    """Jable下载器"""

    def __init__(self, proxy: Optional[str] = None,
                 timeout: int = 15,
                 cookie_retry_times: int = 5,
                 query_retry_times: int = 5,
                 retry_interval: float = 0.5):
        super().__init__(proxy, timeout, cookie_retry_times, query_retry_times, retry_interval)
        self.domain = "jable.tv"

    def get_source_name(self) -> str:
        return "jable"

    async def get_html(self, avid: str) -> Optional[str]:
        avid_upper = avid.upper()
        urls = [
            f"https://{self.domain}/video/{avid_upper}",
        ]
        for url in urls:
            content = await self.fetch_html(url)
            if content:
                logger.info(f"成功获取jable页面: {avid.upper()}")
                return content
        return None

    def parse_html(self, avid: str, html: str) -> Optional[AVInfo]:
        info = AVInfo()

        try:
            # 提取标题 - 优先从 <title> 标签提取
            # 格式: <title>AVID 标题内容 - Jable.TV | ...</title>
            title = None
            # 回退到其他模式
            title_patterns = [
                r'<title>(.+?)\s*-\s*Jable\.TV',
                r'<h4 class="title">([^<]+)</h4>',
                r'<span>标题:</span>\s*<span class="font-medium">([^<]+)</span>',
                r'<span class="font-medium">([^<]+)</span>',
            ]
            for pattern in title_patterns:
                title_match = re.search(pattern, html)
                if title_match:
                    title = title_match.group(1).strip()
                    break

            return info
        except Exception as e:
            logger.error(f"Jable解析失败: {e}")
            return None

    def get_cover_url(self, html: str) -> Optional[str]:
        try:
            match = re.search(r'<meta property="og:image" content="([^"]+)"', html)
            if match:
                return match.group(1)
            return None
        except Exception as e:
            logger.error(f"封面URL提取失败: {e}")
            return None
