import os
import time
import json
import random
import logging
import requests
import exifread
from conf import config
from log import info, warning, success, error
from common import gps_format, jpg_walk, checkPath
from exporter import create_json
import trio
import asks
import click
import hashlib

asks.init("trio")


class Finder:
    def __init__(self):
        self.limit = trio.CapacityLimiter(config.conns * 5)
        self.address_details_url = (
            "http://restapi.amap.com/v3/geocode/regeo?key={}&s=rsv3&location={},{}"
        )
        self.image_pools = {}
        self.res_pools = {}
        self.target_path = config.target_path
        self.save_path = config.save_path

    async def init_session(self):
        self.session = asks.Session(connections=config.conns)
        self.session.header = {
            "User-Agent": random.choice(config.ua_list),
            "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "zh-CN,zh;q=0.8",
            "Referer": "http://www.gpsspg.com",
        }

    def get_exif_datas(self, path):
        with open(path, "rb") as files:
            info = {"path": path}
            tags = None
            try:
                tags = exifread.process_file(files, strict=True)
            except KeyError:
                return
            except Exception as e:
                return
                error(e)

            if not tags:
                return

            if tags:
                tag_keys = tags.keys()
                if (
                    len(set(tag_keys) & set(config.x_and_y_list)) == 2
                    and gps_format(str(tags["GPS GPSLongitude"])) != 0.0
                ):
                    for tag in sorted(tag_keys):
                        if tag in config.show_list:
                            info[tag.split()[-1]] = str(tags[tag]).strip()
                    # 经纬度取值
                    info["GPS"] = (
                        gps_format(str(tags["GPS GPSLatitude"]))
                        * float(
                            1.0
                            if str(tags.get("GPS GPSLatitudeRef", "N")) == "N"
                            else -1.0
                        ),
                        gps_format(str(tags["GPS GPSLongitude"]))
                        * float(
                            1.0
                            if str(tags.get("GPS GPSLongitudeRef", "E")) == "E"
                            else -1.0
                        ),
                    )
                    # 获取实体地址
                    # info["address"] = address(info["GPS"])
                    # 获取照片海拔高度
                    if "GPS GPSAltitudeRef" in tag_keys:
                        try:
                            info["GPSAltitude"] = eval(info["GPSAltitude"])
                        except ZeroDivisionError:
                            info["GPSAltitude"] = 0
                        info["GPSAltitude"] = "距%s%.2f米" % (
                            "地面" if int(info["GPSAltitudeRef"]) == 1 else "海平面",
                            info["GPSAltitude"],
                        )
                        del info["GPSAltitudeRef"]

                    time_item = list(set(config.time_list) & set(tag_keys))
                    if time_item:
                        info["Dates"] = str(tags[time_item[0]])
                else:
                    return
            else:
                return
        self.res_pools[hashlib.new("md5", path.encode()).hexdigest()] = info

    async def find_address(self, key: str, item: dict) -> None:
        async with self.limit:
            gps = item["GPS"]
            resp = await self.session.get(
                self.address_details_url.format(config.key, gps[1], gps[0])
            )
            datas = resp.json()
            # success(datas)
            if datas and datas["status"] == "1" and datas["info"].lower() == "ok":
                self.res_pools[key]["address"] = datas.get("regeocode", {}).get(
                    "formatted_address", ""
                )

    async def find_all_address(self):
        info("find all address")
        async with trio.open_nursery() as nursery:
            for key, item in self.res_pools.items():
                nursery.start_soon(self.find_address, key, item)

    def run(self):
        if not self.target_path:
            error("none target path")
            exit()
        elif checkPath(self.target_path):
            self.image_pools = jpg_walk(self.target_path, config.types_filter)
            while self.image_pools:
                self.get_exif_datas(self.image_pools.pop())
            if config.location and config.key:
                trio.run(self.init_session)
                trio.run(self.find_all_address)
            create_json(
                list(
                    sorted(
                        [item for _, item in self.res_pools.items()],
                        key=lambda item: item["Dates"],
                    )
                )
            )


@click.command()
@click.option("-t", "--target_path", default=None)
@click.option("-s", "--save_path", default=None)
@click.option("-l", "--location", is_flag=True)
def main(target_path: str, save_path: str, location: bool):
    if target_path:
        click.echo(f"搜索路径={target_path}")
        config.target_path = target_path
    if save_path:
        click.echo(f"保存路径={save_path}")
        config.save_path = save_path
    if location:
        click.echo(f"是否定位地址={location}")
        config.location = location
    Finder().run()


if __name__ == "__main__":
    main()
