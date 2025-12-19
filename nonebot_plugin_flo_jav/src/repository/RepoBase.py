import sqlite3 as sql
from pathlib import Path

from nonebot import require

require("nonebot_plugin_localstore")
import nonebot_plugin_localstore as localstore

plugin_data_dir: Path = localstore.get_plugin_data_dir()
plugin_data_file: Path = localstore.get_plugin_data_file("flo_jav.db")


class RepoBase:
    def __init__(self):
        self._database = sql.connect(plugin_data_file)
        self._cursor = self._database.cursor()

    def __del__(self):
        self._cursor.close()
        self._database.close()
