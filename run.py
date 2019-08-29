import os
import time
import json
import random
import logging
import requests
import exifread
from conf import config
from log import info, warning, success, error
from common import gps_format, jpg_walk, checkPath, initPath
from exporter import create_json, analysis
import trio
import asks
import click
import hashlib
import moment


import pathlib
import shutil


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
        self.event_path = f"events/{moment.now().format('YYYY-MM-DD hh:mm:ss')}"
        info(f"event path: {initPath(self.event_path)}")
        self.save_image = config.save_image
        self.image_path = os.path.join(self.event_path, "images")
        if self.save_image:
            info(f"image path: {initPath(self.image_path)}")

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
        try:
            with open(path, "rb") as files:
                info = {"path": path, "date": ""}
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
                        # 获取照片海拔高度
                        if "GPS GPSAltitudeRef" in tag_keys:
                            try:
                                info["GPSAltitude"] = eval(info["GPSAltitude"])
                            except ZeroDivisionError:
                                info["GPSAltitude"] = 0
                            info["GPSAltitude"] = "距%s%.2f米" % (
                                "地面"
                                if int(eval(str(info["GPSAltitudeRef"]))) == 1
                                else "海平面",
                                info["GPSAltitude"],
                            )
                            del info["GPSAltitudeRef"]

                        time_item = list(set(config.time_list) & set(tag_keys))
                        if time_item:
                            info["date"] = str(tags[time_item[0]]).split()
                            info["date"][0] = info["date"][0].replace(":", "-")
                            info["date"] = " ".join(info["date"])
                    else:
                        return
                else:
                    return
            self.res_pools[hashlib.new("md5", path.encode()).hexdigest()] = info
        except Exception as e:
            error(e)

    async def find_address(self, key: str, item: dict) -> None:
        async with self.limit:
            gps = item["GPS"]
            resp = await self.session.get(
                self.address_details_url.format(config.key, gps[1], gps[0])
            )
            datas = resp.json()
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
            if config.save_image:
                info("copy images")
                for index, (key, item) in enumerate(self.res_pools.items()):
                    to_file = pathlib.Path(
                        self.image_path,
                        ".".join(
                            [str(index), pathlib.Path(item["path"]).name.split(".")[-1]]
                        ),
                    )
                    my_file = pathlib.Path(item["path"])
                    shutil.copy(str(my_file), str(to_file))
                    self.res_pools[key]["path"] = "/".join(str(to_file).split("/")[2:])
            datas = list(
                sorted(
                    [item for _, item in self.res_pools.items()],
                    key=lambda item: item["date"],
                )
            )
            if config.analysis:
                analysis(datas, f"{self.event_path}/res.html")
            create_json(datas, f"{self.event_path}/res.json")


@click.command()
@click.option("-t", "--target_path", default=None)
@click.option("-s", "--save_image", is_flag=True)
@click.option("-l", "--location", is_flag=True)
@click.option("-a", "--analysis", is_flag=True)
@click.option("--dark", is_flag=True)
@click.option("--locus", is_flag=True)
def main(
    target_path: str,
    save_image: str,
    location: bool,
    analysis: bool,
    dark: bool,
    locus: bool,
):
    if target_path:
        click.echo(f"搜索路径={target_path}")
        config.target_path = target_path
    if save_image:
        click.echo(f"保存路径={save_image}")
        config.save_image = save_image
    if location:
        click.echo(f"是否定位地址={location}")
        config.location = location
    if analysis:
        click.echo(f"是否分析结果={analysis}")
        config.analysis = analysis
        config.save_image = True
    if dark:
        config.dark_mode = dark
    if locus:
        config.locus = locus
    Finder().run()


if __name__ == "__main__":
    main()
