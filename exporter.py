import json
import pathlib
import webbrowser

import folium
import pandas
from folium import plugins

from common import checkPath, checkTimes, make_popup
from conf import config
from log import success


def create_xlsx(datas, columns, filename="res.xlsx"):
    with checkTimes(f"created {filename}"):
        xlsx = pandas.DataFrame(datas)
        xlsx.rename(columns={_: __ for _, __ in enumerate(columns)}, inplace=True)
        writer = pandas.ExcelWriter(filename, options={"strings_to_urls": False})
        xlsx.to_excel(writer, "data")
        writer.save()


def create_json(datas, filename="res.json"):
    with checkTimes(f"saved {filename}"):
        with open(filename, "w") as f:
            f.write(json.dumps(datas, ensure_ascii=False, indent=4))


def analysis(data, filename="map.html"):
    map = folium.Map(
        [30, 120], world_copy_jump=False, detect_retina=True, no_wrap=True, zoom_start=5
    )
    locations = []
    popups = []
    for item in data:
        locations.append(item["gps"])
        popups.append(
            folium.Popup(make_popup(item), parse_html=False, max_width="100%")
        )
    if config.locus:
        folium.plugins.AntPath(locations, reverse="True", dash_array=[20, 30]).add_to(
            map
        )
    map.add_child(folium.LatLngPopup())
    plugins.MarkerCluster(locations, popups=popups).add_to(map)
    if config.dark_mode:
        folium.TileLayer("cartodbdark_matter").add_to(map)
    map.fit_bounds(map.get_bounds())
    map.save(filename)
    webbrowser.open(pathlib.Path(filename).absolute().as_uri())
