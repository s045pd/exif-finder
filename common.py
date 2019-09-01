import copy
import itertools
import os
import pathlib
import time
from contextlib import contextmanager
from fractions import Fraction

import moment

from conf import config
from log import error, info


def error_log(target="", default=None, raise_err=False, raise_exit=False):
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except KeyboardInterrupt:
                exit()
            except Exception as e:
                error(
                    f"[{target} {  func.__name__  if '__name__' in dir(func) else ''  }]: {e}"
                )
                if raise_exit:
                    exit()
                elif raise_err:
                    raise e
                return default

        return wrapper

    return decorator


@contextmanager
def checkTimes(msg: str = "", level: int = 3):
    """
        检查处理花费时间
    """
    timeStart = time.time()
    yield
    info(f"{msg} cost times: {round(time.time()-timeStart,level)}s")


@error_log()
def jpg_walk(path: str, filter_types: list) -> list:
    """
        获取指导目录全部的图片路径
    """
    with checkTimes("image walker"):
        pools = list(
            itertools.chain(
                *[
                    list(pathlib.Path(path).glob(f"**/*.{types}"))
                    for types in filter_types
                ]
            )
        )
        info(f"image find: {len(pools)}")
        return pools


@error_log()
def radio_format(data):
    """
        强制转分数
    """
    return [Fraction(item.num, item.den) for item in data]


@error_log()
def gps_format(loc: list) -> float:
    """
        经纬度格式转换 度分秒转小数
    """
    loc = radio_format(loc)
    return float(loc[0] + Fraction(loc[1], 60) + Fraction(loc[2], 3600))


@error_log()
def ref_format(ref):
    """
        方向转换
    """
    return 1 if ref.upper() in ["N", "E"] else -1


@error_log()
def real_gps(tags):
    """
        获取经纬度
    """
    for lat, lon in config.gps_tag:
        if all(map(lambda item: item in tags, itertools.chain(lat, lon))):
            gps = [
                gps_format(tags[lat[0]].values) * ref_format(tags[lat[1]].values),
                gps_format(tags[lon[0]].values) * ref_format(tags[lon[1]].values),
            ]
            if gps:
                return gps


@error_log()
def real_time(tags):
    """
        获取特定时间
    """
    tag_keys = tags.keys()
    items = list(set(config.time_list) & set(tag_keys))
    if items:
        dates = str(tags[items[0]]).split()
        dates[0] = dates[0].replace(":", "-")
        return " ".join(dates)
    else:
        return ""


@error_log()
def real_alt(tags):
    """
        获取高度
    """
    default_alt = (0.0, "海平面")
    tag_keys = tags.keys()
    alt, ref = config.alt_tag
    if alt in tag_keys:
        try:
            alt_num = eval(str(tags[alt].values[0]))
        except ZeroDivisionError:
            alt_num = 0
        default_alt = (
            round(alt_num, 2),
            ("地面" if radio_format(tags[ref].values)[0] == 1 else "海平面"),
        )
    return default_alt


def checkPath(path):
    return os.path.exists(path)


def initPath(path):
    if not checkPath(path):
        os.makedirs(path)
        path += " [created!]"
    return path


def make_chunk(datas, length=512):
    data = True
    while data:
        chunk = []
        while len(chunk) < length:
            try:
                data = next(datas)
                chunk.append(data)
            except Exception as e:
                data = None
                break
        yield chunk


def make_popup(item):

    add_normal = (
        lambda data, dicts: f"<p>{data[1]}: {dicts[data[0]]}</p>"
        if data[0] in dicts
        else ""
    )
    # {
    #     "path": "/Users/s045pd/Desktop/Dress-master/G4Y8u9/11.jpg",
    #     "date": "2017:09:28",
    #     "alt": "距海平面0.00米",
    #     "make": "Xiaomi",
    #     "model": "Redmi Note 4",
    #     "soft": "MediaTek Camera Application",
    #     "GPS": [
    #         39.91360472222222,
    #         116.55191038888888
    #     ],
    #     "address": "北京市朝阳区三间房镇定福庄西里1号院定福庄西里1号院南区"
    # },
    html = ""
    cols = (("address", "地址"), ("make", "设备"), ("model", "型号"), ("soft", "编辑软件"))

    if "path" in item:
        html += '<center><p> <a href="{}">{}</a ></p></center>'.format(
            item["path"], item["path"]
        )
    if "date" in item:
        html += f"<center><p>{item['date']}</p></center>"
    # if "gps" in item:
    #     html += f"<p>{item['gps']}</p>"
    if "path" in item:
        html += "<img src='{}' height='240' width='240' />".format(item["path"])

    html += "".join([add_normal(_, item) for _ in cols])
    if "alt" in item and item["alt"][0] > 0.0:
        html += "<p>高度: {1} {0}米</p>".format(*item["alt"])
    return html
