import json
import re
import time
from collections.abc import Iterator
from pathlib import Path
from typing import TypedDict
from urllib.parse import urlparse

from bs4 import BeautifulSoup

from hsck.http_client import HttpClient
from hsck.logger import get_logger
from hsck.models import VideoItem
from hsck.utils import get_page_dir

logger = get_logger(__name__)


class VideoInfo(TypedDict):
    vod_id: int
    title: str
    thumd: str
    time: str
    heart: int
    eye: int
    uptime: str


class VideoScraper:
    def __init__(self, client: HttpClient, host: str, media_dir: Path):
        self.client = client
        self.host = host
        self.media_dir = media_dir

    def _parse_list_page(self, html: str) -> list[VideoInfo]:
        soup = BeautifulSoup(html, "lxml")
        videos: list[VideoInfo] = []

        vodlist = soup.find("ul", class_="stui-vodlist")
        if not vodlist:
            return videos

        for li in vodlist.find_all("li"):
            thumb = li.find(
                "a",
                class_="stui-vodlist__thumb lazyload",
                href=re.compile(r"^/[^/]+/\d+-1-1\.html$"),
            )

            if not thumb or not thumb.get("href") or not thumb.get("title"):
                continue

            vod_id_match = re.search(r"/[^/]+/(\d+)-1-1\.html", str(thumb["href"]))
            if not vod_id_match:
                continue
            vod_id = int(vod_id_match.group(1))

            time_span = thumb.find("span", class_="pic-text text-right")
            video_time = time_span.text.strip() if time_span else ""

            heart = 0
            eye = 0
            uptime = ""

            sub_p = li.find("p", class_="sub")
            if sub_p:
                heart_span = sub_p.find("span", class_="number pull-right")
                if heart_span:
                    heart_match = re.search(r"(\d+)", heart_span.text)
                    if heart_match:
                        heart = int(heart_match.group(1))

                eye_span = None
                eye_spans = sub_p.find_all("span", class_="pull-right")
                for span in eye_spans:
                    if span.find("i", class_="fa-eye"):
                        eye_span = span
                        break

                if eye_span:
                    eye_match = re.search(r"(\d+)", eye_span.text)
                    if eye_match:
                        eye = int(eye_match.group(1))

                uptime_text = ""
                for content in sub_p.contents:
                    if isinstance(content, str):
                        uptime_text += content.strip()
                uptime = uptime_text.strip()

            title_str = str(thumb.get("title", "") or "")
            clean_title = title_str.strip()
            thumd_url = str(thumb.get("data-original", "") or "")
            parsed_url = urlparse(thumd_url)
            thumd_url = (
                f"{parsed_url.path}?{parsed_url.query}" if parsed_url.query else parsed_url.path
            )
            videos.append(
                {
                    "vod_id": vod_id,
                    "title": clean_title,
                    "thumd": thumd_url,
                    "time": video_time,
                    "heart": heart,
                    "eye": eye,
                    "uptime": uptime,
                }
            )

        return videos

    def _fetch_media_url(self, vod_id: int) -> str | None:
        timestamp = int(time.time() * 1000)
        api_url = f"{self.host}/playdata.php?id={vod_id}&sid=1&nid=1&_={timestamp}&r=0"

        html = self.client.get_html(api_url)
        try:
            data = json.loads(html)
            if data.get("ok") and "p" in data:
                url = data["p"].get("url")
                if url:
                    return url.replace("\\/", "/")
        except json.JSONDecodeError:
            pass
        return None

    def scrape_videos(self, vod_type_id: int, vod_type_name: str, page: int) -> Iterator[VideoItem]:
        url = f"{self.host}/vodtype/{vod_type_id}-{page}.html"
        logger.debug(f"正在采集: {vod_type_id} {vod_type_name} 第 {page} 页")

        html = self.client.get_html(url)
        video_infos = self._parse_list_page(html)

        for info in video_infos:
            page_dir = self.media_dir / get_page_dir(info["vod_id"])
            cache_file = page_dir / f"{info['vod_id']}.json"

            if cache_file.exists():
                try:
                    cached = json.loads(cache_file.read_text(encoding="utf-8"))
                    if cached.get("heart") != info["heart"] or cached.get("eye") != info["eye"]:
                        cached["heart"] = info["heart"]
                        cached["eye"] = info["eye"]
                        cache_file.write_text(
                            json.dumps(cached, ensure_ascii=False, indent=2),
                            encoding="utf-8",
                        )
                        logger.debug(f"更新统计: {info['vod_id']} {info['title']}")
                    else:
                        logger.debug(f"跳过已存在: {info['vod_id']} {info['title']}")
                except Exception:
                    pass
                continue

            media_url = self._fetch_media_url(info["vod_id"])
            if not media_url:
                logger.warning(f"无法获取媒体地址: {info['vod_id']} {info['title']}")
                continue

            yield VideoItem(
                vod_id=info["vod_id"],
                vod_type_id=vod_type_id,
                vod_type_name=vod_type_name,
                title=info["title"],
                thumd=info["thumd"],
                media=media_url,
                time=info["time"],
                heart=info["heart"],
                eye=info["eye"],
                uptime=info["uptime"],
            )
