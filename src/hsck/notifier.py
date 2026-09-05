import httpx

from hsck.logger import get_logger

logger = get_logger(__name__)


class WxPusher:
    API_URL = "https://wxpusher.zjiecode.com/api/send/message/"
    DEFAULT_UID = "UID_xKkkEccqH4wC2CqOY48uCMYZqVWU"

    def __init__(self, app_token: str):
        self.app_token = app_token
        self.enabled = bool(app_token)
        if not self.enabled:
            logger.warning("WXPUSHER_APPTOKEN 未设置, 消息推送功能已禁用")

    def send(self, content: str):
        if not self.enabled:
            return

        params = {
            "appToken": self.app_token,
            "content": content,
            "uid": self.DEFAULT_UID,
        }

        try:
            httpx.get(self.API_URL, params=params, timeout=10)
            logger.debug(f"推送消息: {content}")
        except Exception as e:
            logger.error(f"推送失败: {e}")
