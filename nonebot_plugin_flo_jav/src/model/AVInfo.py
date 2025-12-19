from typing import Optional


class AVInfo:
    def __init__(self):
        self._avid: Optional[str] = None
        self._title: Optional[str] = None
        self._source: Optional[str] = None
        self._release_date: Optional[str] = None
        self._duration: Optional[str] = None
        self._director: Optional[str] = None
        self._image_url: Optional[str] = None

    def get_avid(self) -> Optional[str]:
        return self._avid

    def get_title(self) -> Optional[str]:
        return self._title

    def get_source(self) -> Optional[str]:
        return self._source

    def get_release_date(self) -> Optional[str]:
        return self._release_date

    def get_duration(self) -> Optional[str]:
        return self._duration

    def get_directory(self) -> Optional[str]:
        return self._director

    def get_image_url(self) -> Optional[str]:
        return self._image_url

    def update_from_source(self, source_data: dict) -> None:
        self._avid = source_data["avid"]
        self._title = source_data["title"]
        self._source = source_data["source"]
        self._image_url = source_data["image_url"]

    def update_from_scrapper(self, scrape_data: dict) -> None:
        """
        从刮削器数据更新元数据，需要 "release_date", "duration", "director
        :param scrape_data:
        :return:
        """
        if scrape_data.get('release_date'):
            self._release_date = scrape_data['release_date']
        if scrape_data.get('duration'):
            self._duration = scrape_data['duration']
        if scrape_data.get('director'):
            self._director = scrape_data['director']
        if scrape_data.get('image_url') and self._image_url is None:
            self._image_url = scrape_data['image_url']
