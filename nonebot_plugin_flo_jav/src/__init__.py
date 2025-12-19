from nonebot import require

require("nonebot_plugin_alconna")
from nonebot_plugin_alconna import *

require("nonebot_plugin_uninfo")
from nonebot_plugin_uninfo import *

from .source.SourceManager import source_manager

__plugin_meta__ = PluginMetadata(
    name="nonebot-plugin-flo-jav",
    description="nonebot-plugin-flo-jav",
    usage="""

    """,
    homepage="https://github.com/Florenz0707/nonebot-plugin-flo-jav",
    type="application",
    config=Config,
    supported_adapters={"~onebot.v11"},
    extra={
        "author": "florenz0707",
    }
)

query = on_alconna(
    Alconna(
        "jav.q",
        Args["avid", str],
    ),
    use_cmd_start=True,
)


@query.handle()
async def abstract_handler(
        avid: Match[str] = AlconnaMatch("avid")):
    if not avid.available:
        await UniMessage.text("听不懂哦~ 再试一次吧~").finish()
    avid = avid.result.upper()
    info = await source_manager.get_info_from_any_source(avid)
    if info is None:
        await UniMessage.text("获取失败了！").finish()
    await UniMessage.finish(info.to_string())
