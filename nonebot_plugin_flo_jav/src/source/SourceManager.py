from pathlib import Path
from typing import Dict, Optional

from nonebot.log import logger

from ..config import data_dir, jav_config

from .Avtoday import Avtoday
from .SourceBase import SourceBase
from ..model.AVInfo import AVInfo
from ..model.SourceCookie import SourceCookie
from ..repository.AVInfoRepo import AVInfoRepo, avinfo_repo
from ..repository.CookieRepo import CookieRepo, cookie_repo
from ..scraper.ScraperManager import ScraperManager


class SourceManager:
    """下载器管理器"""

    # 下载器实例映射
    SOURCE_INSTANCES = {
        "avtoday": Avtoday
    }

    def __init__(self,
                 scraper: ScraperManager,
                 proxy: Optional[str] = None):
        self.proxy = proxy
        self.image_dir: Path = Path(data_dir) / "images"
        if not self.image_dir.exists():
            self.image_dir.mkdir(parents=True, exist_ok=True)

        self._scraper_manager: ScraperManager = scraper
        self._avinfo_repo: AVInfoRepo = avinfo_repo
        self._cookie_repo: CookieRepo = cookie_repo
        self._sources: Dict[str, SourceBase] = {}

        for source_name, source_class in self.SOURCE_INSTANCES.items():
            source = source_class(self.proxy)
            logger.info(f"注册下载器: {source.get_source_name()}")
            self._sources[source.get_source_name()] = source

        # 从数据库加载 cookie
        self._load_cookies_from_db()

    def _load_cookies_from_db(self):
        """从数据库加载所有源的 cookie"""
        try:
            for name, source in self._sources.items():
                if (source_cookie := cookie_repo.get_source_cookie(name)) is not None:
                    source.set_cookie(source_cookie.cookie)
                    logger.info(f"从数据库加载 {name} 的 Cookie")
        except Exception as e:
            logger.warning(f"从数据库加载 Cookie 失败: {e}")

    def set_source_cookie(self, source_name: str, cookie: str) -> bool:
        """
        设置指定源的 cookie，同时更新内存和数据库
        返回是否设置成功
        """
        actual_name = None
        target_source: Optional[SourceBase] = None
        if source_name.lower() in self._sources.keys():
            actual_name = source_name.lower()
            target_source = self._sources.get(actual_name)

        if not target_source:
            logger.warning(f"未找到源 {source_name}")
            return False

        # 更新内存中的 cookie
        target_source.set_cookie(cookie)

        # 更新数据库
        try:
            cookie_repo.create_or_update_source_cookie({
                SourceCookie.generate_from_source({
                    "source": actual_name,
                    "cookie": cookie
                })
            })
            logger.info(f"已保存 {actual_name} 的 Cookie 到数据库 ")
            return True
        except Exception as e:
            logger.error(f"保存 Cookie 到数据库 ({actual_name}) 失败: {e}")
            return False

    async def get_info_from_any_source(self, avid: str) -> Optional[AVInfo]:
        """
        遍历所有源获取信息
        返回: AVInfo
        """
        # 数据库缓存
        if (info := self._avinfo_repo.get_from_source(avid)) is not None:
            return info

        for name, source in self._sources.items():
            logger.info(f"尝试从 {name} 获取 {avid}")
            if (html := await source.get_html(avid)) is not None:
                if (info := source.parse_html(html)) is not None:
                    return info
        return None

    async def get_info_from_source(self, avid: str, source_str: str) -> Optional[AVInfo]:
        """
        从指定源获取信息
        返回: (info, source, html) 或 None
        """
        # 查找对应的下载器（不区分大小写）
        source = None
        for name, possible_source in self._sources.items():
            if name.lower() == source_str.lower():
                source = possible_source
                break

        if (info := self._avinfo_repo.get_from_source(avid, source)) is not None:
            return info

        if not source:
            logger.warning(f"未找到源 {source_str} 对应的下载器")
            return None

        if (html := await source.get_html(avid)) is not None:
            logger.info(f"成功从源 {source_str} 获取 html")
            if (info := source.parse_html(html)) is not None:
                return info

        return None

    async def save_all_resources(self, info: AVInfo) -> None:
        """
        一次性保存所有资源到 resource/{avid}/ 目录
        包括: HTML缓存、封面、元数据
        返回保存状态
        """

        # 下载封面
        avid = info.get_avid()
        source = self._sources.get(info.get_source())
        image_url = info.get_image_url()
        if image_url:
            logger.info(f"封面下载地址: {image_url}")
            cover_path = self.get_image_path(avid)
            if not await source.download_file(image_url, str(cover_path)):
                logger.warning(f"封面下载失败: {avid}")
        else:
            logger.warning(f"未找到封面URL: {avid}")

        # 从刮削器获取额外元数据
        scraped_data = self._scraper_manager.scrape(avid)
        if scraped_data:
            info.update_from_scrapper(scraped_data)
            logger.info(f"已从刮削器获取 {avid} 的额外元数据")

        # 保存到数据库
        avinfo_repo.create_or_update_avinfo(info)

    def get_image_path(self, avid: str) -> Optional[Path]:
        image_path = self.image_dir / f"{avid.upper()}.jpg"
        if not image_path.exists():
            return None
        return image_path


source_manager = SourceManager(
    ScraperManager(jav_config.jav_proxy),
    proxy=jav_config.jav_proxy,
)
