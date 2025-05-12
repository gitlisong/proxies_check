from typing import Awaitable, Callable

import aiohttp
from attr import dataclass

from .proxy_source_info import ProxySourceInfo

from .proxy_address import ProxyAddress


@dataclass
class ProxySource:
    proxy_source_info: ProxySourceInfo

    parse: Callable[
        [aiohttp.ClientResponse, "ProxySource"], Awaitable[list[ProxyAddress]]
    ]

    def __str__(self) -> str:
        return str(self.proxy_source_info)
