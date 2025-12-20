import os
import time
from typing import Optional

from nonebot.log import logger

from curl_cffi import requests
from curl_cffi.requests.exceptions import HTTPError

from ..model import AVInfo
from ..model import SourceCookie

from ..repository.CookieRepo import CookieRepo, cookie_repo

from ..constants import HEADERS, IMPERSONATE


class SourceBase:
    def __init__(
            self, proxy: Optional[str] = None,
            timeout: int = 15,
            cookie_retry_times: int = 5,
            query_retry_times: int = 5,
            retry_interval: float = 0.5):
        self.repo: CookieRepo = cookie_repo
        self.domain: str = ""
        self.proxy: str = proxy
        self.proxies: dict = {'http': proxy, 'https': proxy} if proxy else None
        self.timeout: int = timeout
        self.cookie: Optional[str] = None
        self.cookie_retry_times: int = cookie_retry_times
        self.query_retry_times: int = query_retry_times
        self.retry_interval: float = retry_interval

    def set_domain(self, domain: str) -> None:
        self.domain = domain

    def set_cookie(self, cookie: str) -> None:
        self.cookie = cookie

    def get_source_name(self) -> str:
        raise NotImplementedError

    def _get_home_url(self) -> str:
        if not self.domain:
            raise ValueError(f"{self.get_source_name()} 未设置domain")
        return f"https://{self.domain}/"

    def set_cookie_auto(self) -> bool:
        source_name = self.get_source_name()

        home_url = self._get_home_url()
        headers = HEADERS.copy()
        for i in range(self.cookie_retry_times):
            time.sleep(self.retry_interval)
            session = requests.Session()
            logger.info(f"{source_name}: 正在自动获取cookie... 重试: {i + 1}/{self.cookie_retry_times}")
            response = session.get(
                home_url,
                proxies=self.proxies,
                headers=headers,
                timeout=self.timeout,
                impersonate=IMPERSONATE,
            )
            try:
                response.raise_for_status()
            except HTTPError:
                continue

            # 获取cookie字符串
            cookies = session.cookies.get_dict()
            if cookies is not None:
                cookie_str = '; '.join([f"{k}={v}" for k, v in cookies.items()])
                source_cookie = SourceCookie.generate_from_source({
                    "source": self.get_source_name(),
                    "cookie": cookie_str,
                })
                self.repo.create_or_update_source_cookie(source_cookie)
                self.cookie = cookie_str
                return True

        return False

    def _load_cookie_from_db(self) -> bool:
        """
        从数据库加载cookie

        Returns:
            bool: 是否成功加载
        """
        try:
            source_name = self.get_source_name()
            source_cookie = self.repo.get_source_cookie(source_name)
            self.cookie = source_cookie.get_cookie()
            return True
        except Exception as e:
            logger.error(f"{self.get_source_name()}: 从数据库加载cookie失败: {str(e)}")
            return False

    async def get_html(self, avid: str) -> Optional[str]:
        raise NotImplementedError

    def parse_html(self, avid: str, html: str) -> Optional[AVInfo]:
        raise NotImplementedError

    async def fetch_html(self, url: str, referer: str = "") -> Optional[str]:
        logger.info(f"fetch url: {url}")
        try:
            headers = HEADERS.copy()
            if referer:
                headers["Referer"] = referer
            if self.cookie:
                headers["Cookie"] = self.cookie
            response = requests.get(
                url,
                proxies=self.proxies,
                headers=headers,
                timeout=self.timeout,
                impersonate=IMPERSONATE,
            )
            response.raise_for_status()
            return response.text
        except Exception as e:
            logger.error(f"请求失败: {str(e)}")
            return None

    async def download_file(self, url: str, save_path: str, referer: str = "") -> bool:
        """下载文件到指定路径"""
        try:
            headers = HEADERS.copy()
            if referer:
                headers["Referer"] = referer
            if self.cookie:
                headers["Cookie"] = self.cookie
            response = requests.get(
                url,
                stream=True,
                impersonate=IMPERSONATE,
                proxies=self.proxies,
                headers=headers,
                timeout=self.timeout,
                allow_redirects=True
            )
            response.raise_for_status()

            os.makedirs(os.path.dirname(save_path), exist_ok=True)
            with open(save_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
            return True
        except Exception as e:
            logger.error(f"下载失败: {e}")
            return False
