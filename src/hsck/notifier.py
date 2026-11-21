import httpx

from hsck.logger import get_logger

logger = get_logger(__name__)


class WxPusher:
    API_URL = "https://wxpusher.zjiecode.com/api/send/message"
    DEFAULT_UID = "UID_xKkkEccqH4wC2CqOY48uCMYZqVWU"

    def __init__(self, app_token: str):
        self.app_token = app_token
        self.enabled = bool(app_token)
        if not self.enabled:
            logger.warning("WXPUSHER_APPTOKEN 未设置, 消息推送功能已禁用")

    def send(
        self,
        summary: str,
        content: str,
        *,
        url: str | None = None,
        content_type: int = 2,
    ):
        """发送一条富文本消息。

        summary: 通知卡片/锁屏上的短摘要（≤100 字），即「消息主题」。
        content: 正文，HTML（content_type=2，仅 body 内部）或 Markdown（3）。
        url: 点击通知打开的链接，可选。
        content_type: 1 文本 / 2 HTML / 3 Markdown。
        """
        if not self.enabled:
            return

        body = {
            "appToken": self.app_token,
            "content": content,
            "summary": summary,
            "contentType": content_type,
            "uids": [self.DEFAULT_UID],
            "verifyPayType": 0,
        }
        if url is not None:
            body["url"] = url

        try:
            resp = httpx.post(self.API_URL, json=body, timeout=10)
            resp.raise_for_status()
            data = resp.json()
            if not data.get("success"):
                logger.warning(f"推送返回失败: code={data.get('code')} msg={data.get('msg')}")
            else:
                logger.debug(f"推送成功: {summary}")
        except httpx.HTTPError:
            logger.exception("推送请求失败")
        except ValueError:
            logger.exception("推送响应解析失败")
