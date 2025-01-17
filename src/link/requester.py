from re import compile
from typing import TYPE_CHECKING

# from src.custom import PHONE_HEADERS
from src.custom import wait
from src.tools import PrivateRetry
from src.tools import TikTokDownloaderError
from src.tools import capture_error_request

if TYPE_CHECKING:
    from src.config import Parameter
    from httpx import AsyncClient

__all__ = ["Requester"]


class Requester:
    URL = compile(r"(https?://\S+)")

    def __init__(self, params: "Parameter", client: "AsyncClient", ):
        self.client = client
        self.log = params.logger
        self.max_retry = params.max_retry

    async def run(self, text: str, ) -> str:
        urls = self.URL.finditer(text)
        if not urls:
            return ""
        result = []
        for i in urls:
            result.append(await self.request_url(u := i.group(), ) or u)
            await wait()
        return " ".join(i for i in result if i)

    @PrivateRetry.retry
    @capture_error_request
    async def request_url(self, url: str, content="url", ):
        response = await self.client.get(url, )
        match content:
            case "text":
                return response.text
            case "content":
                return response.content
            case "json":
                return response.json()
            case "headers":
                return response.headers
            case "url":
                return str(response.url)
            case _:
                raise TikTokDownloaderError
