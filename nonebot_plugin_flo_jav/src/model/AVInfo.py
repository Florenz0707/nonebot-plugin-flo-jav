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

    def get_director(self) -> Optional[str]:
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

    @classmethod
    def generate_from_db(cls, data: tuple[str, str, str, str, str, str, str]):
        result = AVInfo()
        result._avid = data[0]
        result._title = data[1]
        result._source = data[2]
        result._release_date = data[3]
        result._duration = data[4]
        result._director = data[5]
        result._image_url = data[6]
        return result

    def to_string(self):
        return f"AVID：{self._avid}\n标题：{self._title}\n来源：{self._source}\n发行日期：{self._release_date}\n" \
                f"时长：{self._duration}\n导演：{self._director}"
