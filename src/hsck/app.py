import html as _html
import os
import sys
import traceback
from datetime import datetime
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

# GitHub 仓库地址（远程中带 token，此处仅用公开地址），点击通知时打开仓库
REPO_URL = "https://github.com/fuxkjd/hsck"

# 边框/分隔线统一用中性灰（带透明度），在 WxPusher 明/暗两套主题下都可见。
# 文本颜色一律不写，交给 WxPusher 模板按系统主题自动适配，避免深浅主题下看不清。
_BORDER = "1px solid rgba(128,128,128,.3)"
_BORDER_ACCENT = "1px solid rgba(128,128,128,.3);border-left:3px solid rgba(128,128,128,.6)"


def _esc(value) -> str:
    return _html.escape(str(value), quote=True)


def _wrap(title: str, body: str) -> str:
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return (
        "<div style=\"font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,"
        'sans-serif;line-height:1.5;">'
        f'<h2 style="margin:0 0 8px;font-size:18px;">{_esc(title)}</h2>'
        f"{body}"
        '<hr style="border:none;border-top:1px solid rgba(128,128,128,.3);margin:12px 0;" />'
        f'<p style="margin:0;opacity:.65;font-size:12px;">Hsck 数据采集 · {_esc(now)}</p>'
        "</div>"
    )


def _build_update(
    per_type_delta: dict[int, int],
    current_counts: dict[str, dict[str, int]],
    vod_types: dict[int, str],
    total_delta: int,
    local_total: int,
    host: str,
    image_host: str,
) -> str:
    # 展示所有类别：有更新的显示 +N，未更新的显示 +0
    rows = ""
    shown = 0
    for type_id, name in vod_types.items():
        type_id_str = str(type_id)
        if type_id_str not in current_counts:
            continue
        shown += 1
        delta = per_type_delta.get(type_id, 0)
        current_num = current_counts[type_id_str].get("num", 0)
        rows += (
            "<tr>"
            f'<td style="padding:4px 8px;border:{_BORDER};">{_esc(name)}</td>'
            '<td style="padding:4px 8px;border:'
            f'{_BORDER};text-align:right;font-weight:bold;">+{delta}</td>'
            f'<td style="padding:4px 8px;border:{_BORDER};text-align:right;">{current_num}</td>'
            "</tr>"
        )
    table = (
        '<table style="border-collapse:collapse;width:100%;font-size:14px;margin:6px 0;">'
        "<thead><tr>"
        f'<th style="padding:4px 8px;border:{_BORDER};text-align:left;">分类</th>'
        f'<th style="padding:4px 8px;border:{_BORDER};text-align:right;">本次新增</th>'
        f'<th style="padding:4px 8px;border:{_BORDER};text-align:right;">远程总条目</th>'
        "</tr></thead>"
        f"<tbody>{rows}</tbody>"
        "</table>"
    )
    body = (
        f'<p style="margin:6px 0;">本次运行共新增 <b>{total_delta}</b> 条，'
        f"共展示 {shown} 个分类（未新增的显示 +0）。</p>"
        f"{table}"
        f'<p style="margin:6px 0;">本地已缓存合计：<b>{local_total}</b> 条</p>'
        f'<p style="margin:6px 0;opacity:.65;font-size:13px;">'
        f"当前主机：{_esc(host)}<br/>图片主机：{_esc(image_host)}</p>"
    )
    return _wrap("Hsck 采集成功", body)


def _build_image_update(old_host: str | None, new_host: str, local_total: int) -> str:
    old_text = _esc(old_host) if old_host is not None else "（首次设置，无旧值）"
    body = (
        '<p style="margin:6px 0;">远程条目无变化，<b>图片主机已变更</b>，已重新生成发布文件。</p>'
        f'<p style="margin:6px 0;">旧图床：{old_text}<br/>新图床：{_esc(new_host)}</p>'
        f'<p style="margin:6px 0;">本地已缓存合计：<b>{local_total}</b> 条</p>'
    )
    return _wrap("Hsck 图床更新", body)


def _build_no_update(local_total: int, host: str) -> str:
    body = (
        '<p style="margin:6px 0;">本次运行远程条目与上次一致，<b>未采集新内容</b>（CI 正常执行）。</p>'
        f'<p style="margin:6px 0;">本地已缓存合计：<b>{local_total}</b> 条</p>'
        f'<p style="margin:6px 0;opacity:.65;font-size:13px;">当前主机：{_esc(host)}</p>'
    )
    return _wrap("Hsck 无更新", body)


def _build_host_error(details: list[str]) -> str:
    detail_text = "\n".join(details) if details else "未知原因（无明细）"
    body = (
        '<p style="margin:6px 0;">主机检查失败，未采集任何内容。</p>'
        '<p style="margin:6px 0;font-weight:bold;">失败详情：</p>'
        '<pre style="margin:6px 0;padding:8px;border:'
        f'{_BORDER_ACCENT};border-radius:4px;white-space:pre-wrap;font-size:12px;">'
        f"{_esc(detail_text)}</pre>"
    )
    return _wrap("Hsck 采集失败", body)


def _build_exception(stage: str, exc_type: str, exc_msg: str, tb_text: str) -> str:
    body = (
        f'<p style="margin:6px 0;">运行中断于 <b>{_esc(stage)}</b> 阶段。</p>'
        '<p style="margin:6px 0;">'
        f"异常：<b>{_esc(exc_type)}: {_esc(exc_msg)}</b></p>"
        '<pre style="margin:6px 0;padding:8px;border:'
        f'{_BORDER_ACCENT};border-radius:4px;white-space:pre-wrap;font-size:12px;">'
        f"{_esc(tb_text)}</pre>"
    )
    return _wrap("Hsck 采集异常", body)


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
        self._stage = "初始化"

    def run(self):
        logger.info("=" * 40)
        logger.info("Hsck 数据采集工具")
        logger.info("=" * 40)
        self._stage = "初始化"
        try:
            self._execute()
        except Exception:  # noqa: BLE001 顶层兜底：任何异常都要推送告警
            self._send_exception(traceback.format_exc())
        logger.info("运行结束")

    def _send_exception(self, tb_text: str):
        tb_lines = tb_text.strip().splitlines()
        tb_text = "\n".join(tb_lines[-25:])
        exc = sys.exc_info()
        exc_type = exc[0].__name__ if exc[0] else "Exception"
        exc_msg = str(exc[1]) if exc[1] else ""
        summary = f"🔴 采集异常 · {exc_type}"
        content = _build_exception(self._stage, exc_type, exc_msg, tb_text)
        self.pusher.send(summary, content, url=REPO_URL)

    def _execute(self):
        client = HttpClient()

        self._stage = "主机检查"
        host_checker = HostChecker(client, self.config)
        if not host_checker.check_host():
            logger.error("Host 检查失败")
            self.pusher.send(
                "🔴 采集失败 · 主机不可用",
                _build_host_error(host_checker.check_details),
                url=REPO_URL,
            )
            return

        host = host_checker.current_host
        image_host = host_checker.image_host
        assert host is not None
        assert image_host is not None

        self._stage = "比对条目数量"
        saved_counts = self.config.get_saved_vod_counts()
        current_counts = host_checker.vod_type_counts
        self.config.save_vod_counts(current_counts)

        total_delta = 0
        update_pages: dict[int, int] = {}
        per_type_delta: dict[int, int] = {}

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
                per_type_delta[type_id] = delta
                total_delta += delta
                logger.info(f"{type_id}-{type_name}: 总{current['num']}条, 新+{delta}条 {pages}页")
            else:
                logger.debug(f"{type_id}-{type_name}: 无更新")

        needs_regenerate = False
        if total_delta > 0:
            self._stage = "采集新条目"
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
            self._stage = "生成发布文件"
            self.generator.generate(image_host)
            local_total = self.storage.count_videos()
            if total_delta > 0:
                content = _build_update(
                    per_type_delta,
                    current_counts,
                    self.VOD_TYPES,
                    total_delta,
                    local_total,
                    host,
                    image_host,
                )
                self.pusher.send(
                    f"🟢 采集成功 · 新增 {total_delta} 条",
                    content,
                    url=REPO_URL,
                )
            else:
                content = _build_image_update(old_image_host, image_host, local_total)
                self.pusher.send(
                    "🟡 图床更新 · 已重新生成",
                    content,
                    url=REPO_URL,
                )
        else:
            logger.info("无更新内容")
            local_total = self.storage.count_videos()
            content = _build_no_update(local_total, host)
            self.pusher.send(
                "⚪ 无更新 · CI 已执行",
                content,
                url=REPO_URL,
            )


def main():
    base_dir = Path(__file__).resolve().parent.parent.parent
    app = App(base_dir)
    app.run()
