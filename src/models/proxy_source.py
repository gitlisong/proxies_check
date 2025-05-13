from typing import Awaitable, Callable

import aiohttp
from dataclasses import dataclass

from .proxy_address import ProxyAddress


@dataclass
class ProxySource:
    parse: Callable[
        [aiohttp.ClientResponse, "ProxySource"], Awaitable[list[ProxyAddress]]
    ]

    url: str

    scheme: str | None = None

    def __str__(self) -> str:
        return f"scheme:{self.scheme}\turl:{self.url}"
