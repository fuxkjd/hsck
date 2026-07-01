import json
from collections import defaultdict
from pathlib import Path

from hsck.logger import get_logger

logger = get_logger(__name__)


class DistGenerator:
    def __init__(self, media_dir: Path, dist_dir: Path):
        self.media_dir = media_dir
        self.dist_dir = dist_dir
        dist_dir.mkdir(parents=True, exist_ok=True)

    def generate(self, image_host: str):
        logger.info("正在生成发布文件...")

        all_data = []
        categorized_data = defaultdict(list)

        dirs = [d for d in self.media_dir.iterdir() if d.is_dir()]
        dirs.sort(key=lambda x: int(x.name) if x.name.isdigit() else 0, reverse=True)

        data_count = 0

        for page_dir in dirs:
            if data_count > 3000:
                logger.info(f"删除目录 {page_dir}")
                for f in page_dir.glob("*.json"):
                    f.unlink()
                page_dir.rmdir()
                continue

            json_files = sorted(
                page_dir.glob("*.json"),
                key=lambda f: int(f.stem) if f.stem.isdigit() else 0,
                reverse=True,
            )

            for json_file in json_files:
                try:
                    data = json.loads(json_file.read_text(encoding="utf-8"))
                except Exception:
                    logger.warning(f"跳过无效文件 {json_file}")
                    continue

                if not all(k in data for k in ["title", "thumd", "media"]):
                    logger.warning(f"文件缺少必要字段: {json_file}")
                    continue

                data["thumd"] = image_host + data["thumd"]
                data_count += 1
                all_data.append(data)
                type_name = data.get("vod_type_name", "未分类")
                categorized_data[type_name].append(data)

        txt_content = ""
        m3u_content = "#EXTM3U\n"

        for type_name, items in sorted(categorized_data.items()):
            for i, item in enumerate(items):
                group_idx = i // 50 + 1
                group_name = f"{type_name}{group_idx}"

                if i % 50 == 0:
                    txt_content += f"{group_name},#genre#\n"

                txt_content += f"{item['title']},{item['media']}\n"
                m3u_content += (
                    f'#EXTINF:-1 tvg-logo="{item["thumd"]}" '
                    f'group-title="{group_name}", {item["title"]}\n'
                    f"{item['media']}\n"
                )

        (self.dist_dir / "all.json").write_text(
            json.dumps(all_data, ensure_ascii=False), encoding="utf-8"
        )
        (self.dist_dir / "all.txt").write_text(txt_content, encoding="utf-8")
        (self.dist_dir / "all.m3u").write_text(m3u_content, encoding="utf-8")

        logger.info(f"生成完成, 共 {len(all_data)} 条记录")
