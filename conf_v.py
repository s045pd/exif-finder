class Config:

    name = ""
    rest_api_key = ""
    ua_list = [
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/535.1 (KHTML, like Gecko) Chrome/14.0.835.163 Safari/535.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0) Gecko/20100101 Firefox/6.0",
        "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; InfoPath.2; .NET4.0C; .NET4.0E; .NET CLR 2.0.50727; 360SE)",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Win64; x64; Trident/5.0; .NET CLR 2.0.50727; SLCC2; .NET CLR 3.5.30729; .NET CLR 3.0.30729; Media Center PC 6.0; InfoPath.3; .NET4.0C; Tablet PC 2.0; .NET4.0E)",
        "Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)",
        "Mozilla/5.0 (X11; U; Linux i686; rv:1.7.3) Gecko/20040913 Firefox/0.10",
        "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; ja) Presto/2.10.289 Version/12.00",
        "Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36",
    ]
    types_filter = ["bmp", "jpeg", "jpg", "tiff", "gif", "png"]
    location = False
    conns = 20
    target_path = ""
    save_image = False
    analysis = False

    dark_mode = False
    locus = False

    # key,nickname
    show_list = [
        ("GPS GPSDOP", "dop"),
        ("GPS GPSMeasureMode", "mode"),
        ("Image Software", "soft"),
        ("Image Model", "model"),
        ("Image Make", "make"),
        ("Text Layer Name", "text"),
    ]
    gps_tag = (
        (
            ("GPS GPSLatitude", "GPS GPSLatitudeRef"),
            ("GPS GPSLongitude", "GPS GPSLongitudeRef"),
        ),
    )
    alt_tag = ("GPS GPSAltitudeRef", "GPS GPSAltitude")
    time_list = (
        "EXIF DateTimeDigitized",
        "EXIF DateTimeOriginal",
        "Image DateTime",
        "GPS GPSDate",
    )

    status = {"success": 0, "failed": 0, "total": 0, "updated": 0}


config = Config
