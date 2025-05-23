from typing import Awaitable, Callable

import aiohttp
from dataclasses import dataclass

from .proxy_address import ProxyAddress

from .proxy_server import ProxyServer


@dataclass
class ProxyCheckTarget:
    website: str
    check: Callable[[aiohttp.ClientResponse, ProxyAddress], Awaitable[ProxyServer]]
    scheme: str | None = None
