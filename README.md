<center><img src="media/eye.jpg" width=250 height=250 /></center>
<center><h1>EXIF-Finder</h1></center>

这是一个用于检索出相册中留存有GPS定位信息图像的工具，且用法很简单。只需要输入如下命令即可

```bash
python3 run.py -t [path]
```

如果您需要(-l 参数)或许定位地区的中文名称，您就需要提前到`restapi.amap.com`站点申请一个自己的`key`并填入`conf.py`中。


### 参数说明:

- `-t`: 指定相册地址【必要参数】
- `-s`: 指定图片存储文件夹名
- `-l`: 开启地理定位附近位置查询功能
- `-a`: 开启地图投影功能，默认添加图片存储地址为`image`
- `--dark`: 开启暗黑地图模式
- `--locus`: 开启标点轨迹【依据时间排布】


### 结果案例:

```json
[

    {
        "path": "images/38.jpg",
        "date": "2016-06-21 23:10:27",
        "GPSAltitude": "距海平面0.00米",
        "Make": "Xiaomi",
        "Model": "MI 5",
        "Software": "gemini-user 6.0 MRA, ... ]",
        "GPS": [
            34.787079999999996,
            113.63151497222222
        ],
        "address": "河南省郑州市金水区南阳新村街道第九人民医院家属院"
    },
    {
        "path": "images/17.jpg",
        "date": "2017-05-28 14:41:36",
        "GPSAltitude": "距海平面89.37米",
        "Make": "Apple",
        "Model": "iPhone 7",
        "Software": "10.3.1",
        "GPS": [
            40.41302777777778,
            116.67415555555556
        ],
        "address": "北京市怀柔区怀北镇中国科学院大学雁栖湖校区公寓"
    }
 
]

```

### 👯一次女装图集的分析结果

图集项目地址: [https://github.com/komeiji-satori/Dress](https://github.com/komeiji-satori/Dress)

![media/demo_map.png](media/demo_map.png)




