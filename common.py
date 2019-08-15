import copy
import os
import time
from contextlib import contextmanager
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
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
