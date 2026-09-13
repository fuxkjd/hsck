import re
from urllib.parse import urljoin, urlparse

from bs4 import BeautifulSoup

from hsck.config import ConfigManager
from hsck.http_client import HttpClient
from hsck.logger import get_logger
from hsck.scraper.captcha import CaptchaSolver

logger = get_logger(__name__)


class HostChecker:
    def __init__(self, client: HttpClient, config: ConfigManager):
        self.client = client
        self.config = config
        self.captcha_solver = CaptchaSolver(client)

        self.current_host: str | None = None
        self.image_host: str | None = None
        self.vod_type_counts: dict[str, dict[str, int]] = {}

    def _extract_host_info(self, html: str, host: str) -> bool | str:
        soup = BeautifulSoup(html, "lxml")

        if len(html) > 20000 and soup.find(class_="stui-warp-content") and "最近更新" in html:
            self.vod_type_counts = {}
            menu_ul = soup.find("ul", class_="stui-pannel__menu")
            if menu_ul:
                for li in menu_ul.find_all("li"):
                    a = li.find("a", href=True)
                    if a:
                        href = str(a["href"])
                        match = re.match(r"/vodtype/(\d+)\.html", href)
                        if match:
                            vod_type_id = match.group(1)
                            count_span = a.find("span", class_="count pull-right")
                            if count_span:
                                count = int(count_span.text.strip())
                                self.vod_type_counts[vod_type_id] = {
                                    "num": count,
                                    "page": (count + 39) // 40,
                                }

            thumb = soup.find(
                "a",
                class_="stui-vodlist__thumb lazyload",
                href=re.compile(r"^/[^/]+/\d+-1-1\.html$"),
                attrs={"data-original": re.compile(r"^https?://[^/]+/(images|video)/")},
            )
            if not thumb:
                logger.error("无法找到符合条件的缩略图标签")
                return False

            parsed_url = urlparse(str(thumb["data-original"]))
            self.image_host = f"{parsed_url.scheme}://{parsed_url.netloc}"
            logger.debug(f"检测到图片主机: {self.image_host}")

            self.current_host = host
            return True

        if "strU=" in html and soup.find(id="hao123"):
            match = re.search(r'strU="(https?://[^"]+)"', html)
            if match and match.end() < len(html) and html[match.end()] == "+":
                redirect_url = f"{match.group(1)}{host}/&p=/"
                logger.debug(f"检测到跳转: {redirect_url}")
                response = self.client.head(redirect_url)
                location = response.headers.get("Location")
                if location:
                    loc_match = re.match(r"(https?://[a-zA-Z0-9]+\.[a-zA-Z0-9]+(:\d+)?)", location)
                    if loc_match:
                        return loc_match.group(1)
                    else:
                        logger.debug(f"Location 格式不匹配: {location}")
                else:
                    logger.debug(f"响应头中无 Location: status={response.status_code}")
            else:
                logger.debug("strU 格式不匹配或非 JS 拼接跳转")

        if "滑动验证" in html:
            script_tag = soup.find("script", src=re.compile(r"/huadong.*js\?id="))
            if script_tag and script_tag.get("src"):
                js_url = urljoin(host, str(script_tag["src"]))
                logger.debug(f"检测到验证码 JS: {js_url}")
                if self.captcha_solver.solve(host, js_url):
                    return host

        return False

    def _check_single_host(self, host: str) -> bool:
        logger.info(f"正在检查主机: {host}")
        html = self.client.get_html(host)
        result = self._extract_host_info(html, host)

        if result is True:
            self.config.save_host(host)
            logger.info(f"找到有效主机: {host}")
            return True
        elif isinstance(result, str):
            return self._check_single_host(result)
        else:
            logger.debug(f"主机 {host} 响应内容:\n{html}")
            logger.error(f"主机 {host} 不可用")
            return False

    def check_host(self) -> bool:
        saved_host = self.config.get_saved_host()
        if saved_host and self._check_single_host(saved_host):
            return True

        fallback_host = "http://hsck.us"
        if saved_host == fallback_host:
            return False

        return self._check_single_host(fallback_host)
