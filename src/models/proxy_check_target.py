from typing import Awaitable, Callable

import aiohttp
from attr import dataclass

from ..models.proxy_address import ProxyAddress

from ..models.proxy_server import ProxyServer


@dataclass
class ProxyCheckTarget:
    website: str
    check: Callable[[aiohttp.ClientResponse, ProxyAddress], Awaitable[ProxyServer]]
    scheme: str | None = None
