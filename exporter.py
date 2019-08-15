import json

import pandas

from common import checkPath
from log import success
from common import checkTimes


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
