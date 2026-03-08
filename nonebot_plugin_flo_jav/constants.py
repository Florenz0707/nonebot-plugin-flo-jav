"""
常量定义
"""

# 通用请求头
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 "
                  "Safari/537.36 Edg/143.0.0.0",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,"
              "application/signed-exchange;v=b3;q=0.7",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6"
}

IMPERSONATE = "edge"

POSSIBLE_PREFIX = [
    "SSNI", "ABW", "MIDE", "IPX", "MEYD", "CAWD", "PRED", "ABP", "STARS",
    "MIAA", "SSIS", "MIMK", "FSDSS", "MUDR", "DASD", "SDMF", "JUFE", "JUL",
    "PPPD", "PPPE", "HND", "TEK", "JUQ", "SAME", "ADN", "MIAB", "EBWH", "MKBD",
    "WANZ", "MIRD", "JUY", "NMSL", "TPPN", "ROE", "GVH", "START", "DLDSS", "APGH",
    "FNS", "MIFD", "ABF", "ACHJ", "FOCS", "PRST", "CJOD", "MUKC", "MRSS", "FTAV",
    "FFT", "MFYD", "MANX",
]


if __name__ == "__main__":
    prefix = dict()
    for p in POSSIBLE_PREFIX:
        if p in prefix.keys():
            print(p)
        else:
            prefix[p] = True
