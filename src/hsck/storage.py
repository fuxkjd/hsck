import dataclasses
import json
from pathlib import Path

from hsck.logger import get_logger
from hsck.models import VideoItem
from hsck.utils import get_page_dir

logger = get_logger(__name__)


class DataStorage:
    def __init__(self, media_dir: Path):
        self.media_dir = media_dir
        media_dir.mkdir(parents=True, exist_ok=True)

    def save_video(self, item: VideoItem):
        page_dir = self.media_dir / get_page_dir(item.vod_id)
        page_dir.mkdir(exist_ok=True)
        cache_file = page_dir / f"{item.vod_id}.json"

        data = dataclasses.asdict(item)
        cache_file.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
        logger.info(f"保存: {item.vod_id} {item.title}")
