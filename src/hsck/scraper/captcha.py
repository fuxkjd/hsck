import hashlib
import re

from hsck.http_client import HttpClient
from hsck.logger import get_logger

logger = get_logger(__name__)


class CaptchaSolver:
    def __init__(self, client: HttpClient):
        self.client = client

    @staticmethod
    def _string_to_hex(s: str) -> str:
        return "".join(str(ord(c) + 1) for c in s)

    def solve(self, host: str, js_url: str) -> bool:
        try:
            js_content = self.client.get_html(js_url)

            kv_match = re.search(r'key="(\w+)",value="(\w+)"', js_content)
            if not kv_match:
                logger.error("验证码 JS 中未找到 key/value")
                return False
            key, value = kv_match.groups()

            yz_pattern = r'"(/[\w_]+yanzheng_huadong.php[\w_=?]+&key=)"'
            yz_match = re.search(yz_pattern, js_content)
            if not yz_match:
                logger.error("验证码 JS 中未找到验证 URL")
                return False

            hex_value = self._string_to_hex(value)
            md5_value = hashlib.md5(hex_value.encode()).hexdigest()
            verify_url = host + yz_match.group(1) + key + "&value=" + md5_value

            logger.debug(f"请求验证 URL: {verify_url}")
            response = self.client.head(verify_url, headers={"Referer": f"{host}/"})

            if response.cookies:
                logger.info(f"获得新 Cookie: {dict(response.cookies)}")
                return True

            logger.error("验证失败, 未获得有效 Cookie")
            return False
        except Exception as e:
            logger.error(f"解决验证码出错: {e}")
            return False
