import os
from pathlib import Path
from typing import ClassVar

from dotenv import load_dotenv

from hsck.config import ConfigManager
from hsck.generator import DistGenerator
from hsck.http_client import HttpClient
from hsck.logger import get_logger
from hsck.notifier import WxPusher
from hsck.scraper.host_checker import HostChecker
from hsck.scraper.video_scraper import VideoScraper
from hsck.storage import DataStorage

logger = get_logger(__name__)


class App:
    VOD_TYPES: ClassVar[dict[int, str]] = {
        7: "日本有码",
        8: "无码中文字幕",
        9: "有码中文字幕",
        10: "日本无码",
        15: "国产视频",
        21: "欧美高清",
        22: "动漫剧情",
        26: "骑兵破解",
    }

    def __init__(self, base_dir: Path):
        load_dotenv()
        self.base_dir = base_dir
        self.config = ConfigManager(base_dir / "config.json")
        self.storage = DataStorage(base_dir / "media")
        self.generator = DistGenerator(base_dir / "media", base_dir / "dist")
        self.pusher = WxPusher(os.getenv("WXPUSHER_APPTOKEN", ""))

    def run(self):
        logger.info("=" * 40)
        logger.info("Hsck 数据采集工具")
        logger.info("=" * 40)

        client = HttpClient()

        host_checker = HostChecker(client, self.config)
        if not host_checker.check_host():
            logger.error("Host 检查失败")
            self.pusher.send("hsckCheckHostError")
            return

        host = host_checker.current_host
        image_host = host_checker.image_host
        assert host is not None
        assert image_host is not None

        saved_counts = self.config.get_saved_vod_counts()
        current_counts = host_checker.vod_type_counts
        self.config.save_vod_counts(current_counts)

        total_delta = 0
        update_pages: dict[int, int] = {}

        for type_id, type_name in self.VOD_TYPES.items():
            type_id_str = str(type_id)
            if type_id_str not in current_counts:
                continue

            current = current_counts[type_id_str]
            saved = saved_counts.get(type_id_str, {"num": 0})

            if current["num"] > saved["num"]:
                delta = current["num"] - saved["num"]
                if delta > 200:
                    delta = 200
                pages = (delta + 39) // 40
                update_pages[type_id] = pages
                total_delta += delta
                logger.info(f"{type_id}-{type_name}: 总{current['num']}条, 新+{delta}条 {pages}页")
            else:
                logger.debug(f"{type_id}-{type_name}: 无更新")

        needs_regenerate = False
        if total_delta > 0:
            scraper = VideoScraper(client, host, self.storage.media_dir)
            for type_id, pages in update_pages.items():
                type_name = self.VOD_TYPES[type_id]
                for page in range(1, pages + 1):
                    for video in scraper.scrape_videos(type_id, type_name, page):
                        self.storage.save_video(video)
                        needs_regenerate = True

        old_image_host = self.config.get_saved_image_host()
        if old_image_host != image_host:
            logger.info(f"图片主机更新: {old_image_host} -> {image_host}")
            self.config.save_image_host(image_host)
            needs_regenerate = True

        if needs_regenerate:
            self.generator.generate(image_host)
            if total_delta > 0:
                self.pusher.send(f"hsckUpdate +{total_delta}")
            else:
                self.pusher.send("hsckImageUrlUpdate")
        else:
            logger.info("无更新内容")
            self.pusher.send("hsckNoUpdate")

        logger.info("运行结束")


def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    app = App(base_dir)
    app.run()
