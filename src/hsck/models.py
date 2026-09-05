from dataclasses import dataclass


@dataclass
class VideoItem:
    """视频数据模型(与 PHP 原代码字段一致)"""

    vod_type_id: int
    vod_type_name: str
    vod_id: int
    title: str
    thumd: str
    media: str
    time: str = ""
    heart: int = 0
    eye: int = 0
    uptime: str = ""
