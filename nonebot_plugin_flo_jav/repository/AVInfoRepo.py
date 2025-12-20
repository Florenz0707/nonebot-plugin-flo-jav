import sqlite3 as sql

from typing import Optional

from nonebot.log import logger

from ..repository import RepoBase
from ..model import AVInfo


class AVInfoRepo(RepoBase):
    def __init__(self):
        super().__init__()
        create_table_cmd = """
                           CREATE TABLE IF NOT EXISTS AVInfo
                           (
                               avid
                               text
                               NOT
                               NULL,
                               title
                               text
                               NOT
                               NULL,
                               source
                               text
                               NOT
                               NULL,
                               release_date
                               text
                               NOT
                               NULL,
                               duration
                               text
                               NOT
                               NULL,
                               director
                               text
                               NOT
                               NULL,
                               image_url
                               text
                               NOT
                               NULL,
                               primary
                               key
                           (
                               avid,
                               source
                           )
                               ) \
                           """
        self._cursor.execute(create_table_cmd)
        self._database.commit()

    def get_from_source(self, avid: str, source: Optional[str] = None) -> Optional[AVInfo]:
        if source is None:
            self._cursor.execute("""
                                 select avid, title, source, duration, release_date, director, image_url
                                 from AVInfo
                                 where avid = ?
                                 """, (avid,))
        else:
            self._cursor.execute("""
                                 select avid, title, source, duration, release_date, director, image_url
                                 from AVInfo
                                 where avid = ?
                                   and source = ?
                                 """, (avid, source))

        result = self._cursor.fetchone()
        return AVInfo.generate_from_db(result) if result else None

    def create_or_update_avinfo(self, avinfo: AVInfo) -> bool:
        avid = avinfo.get_avid()
        title = avinfo.get_title()
        source = avinfo.get_source()
        duration = avinfo.get_duration()
        release_date = avinfo.get_release_date()
        director = avinfo.get_director()
        image_url = avinfo.get_image_url()
        try:
            self._cursor.execute("""
                                 select avid, source
                                 from AVInfo
                                 where avid = ?
                                   and source = ?
                                 """, (avinfo.get_avid(), avinfo.get_source()))
            if self._cursor.fetchone() is None:
                self._cursor.execute("""
                                     insert into AVInfo(avid, title, source, duration, release_date, director, image_url)
                                     values (?, ?, ?, ?, ?, ?, ?)
                                     """, (avid, title, source, duration, release_date, director, image_url))
            else:
                self._cursor.execute("""
                                     update AVInfo
                                     set title        = ?,
                                         duration     = ?,
                                         release_date = ?,
                                         director     = ?,
                                         image_url    = ?
                                     where avid = ?
                                       and source = ?
                                     """, (title, duration, release_date, director, image_url, avid, source))
            self._database.commit()
        except sql.OperationalError as e:
            logger.error(f"Error in create_or_update_avinfo: {e}")
            return False
        return True


avinfo_repo = AVInfoRepo()
