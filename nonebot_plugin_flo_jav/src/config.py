from pydantic import BaseModel
from pathlib import Path

from nonebot import require, get_plugin_config

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as localstore

data_dir: Path = localstore.get_plugin_data_dir()
database_file: Path = localstore.get_plugin_data_file("flo_jav.db")


class Config(BaseModel):
    jav_proxy: str = None


jav_config = get_plugin_config(Config)
