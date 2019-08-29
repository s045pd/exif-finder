import copy
import os
import time
from contextlib import contextmanager
import moment

from conf import config
from log import info, error


@contextmanager
def checkTimes(msg="", level=3):
    timeStart = time.time()
    yield
    info(f"{msg} cost times: {round(time.time()-timeStart,level)}s")


# 获取指导目录全部的图片路径
def jpg_walk(path: str, types: list):
    with checkTimes("image walker"):
        pools = []
        for root, dirs, files in os.walk(path):
            pools.extend(
                [
                    root.replace("\\", "/") + "/" + item
                    for item in files
                    if item.split(".")[-1].lower() in types and "$" not in root
                ]
            )
        info(f"image find: {len(pools)}")
        return pools


def gps_format(i):
    try:
        _ = [float(eval(x)) for x in i[1:][:-1].split(", ")]
        return _[0] + _[1] / 60 + _[2] / 3600
    except ZeroDivisionError:
        return 0


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


def addsucess():
    config.status["success"] += 1


def addfailed():
    config.status["failed"] += 1


def addtotal():
    config.status["total"] += 1


def addupdate():
    config.status["updated"] += 1


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
    #     "Dates": "2017:09:28",
    #     "GPSAltitude": "距海平面0.00米",
    #     "Make": "Xiaomi",
    #     "Model": "Redmi Note 4",
    #     "Software": "MediaTek Camera Application",
    #     "GPS": [
    #         39.91360472222222,
    #         116.55191038888888
    #     ],
    #     "address": "北京市朝阳区三间房镇定福庄西里1号院定福庄西里1号院南区"
    # },
    html = ""
    cols = (
        ("address", "地址"),
        ("Make", "设备"),
        ("Model", "型号"),
        ("Software", "编辑软件"),
        ("GPSAltitude", "高度"),
    )
    if "path" in item:
        html += '<center><p> <a href="{}">{}</a ></p></center>'.format(
            item["path"], item["path"]
        )
    if "date" in item:
        html += f"<center><p>{item['date']}</p></center>"
    # if "GPS" in item:
    #     html += f"<p>{item['GPS']}</p>"
    if "path" in item:
        html += "<img src='{}' height='240' width='240' />".format(item["path"])
    html += "".join([add_normal(_, item) for _ in cols])
    return html
