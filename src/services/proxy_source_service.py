import asyncio
import logging

import aiohttp

from ..models.proxy_address import ProxyAddress
from ..models.proxy_source import ProxySource

log = logging.getLogger("app")


class ProxySourceService:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_timeout: aiohttp.ClientTimeout,
        headers: dict,
    ) -> None:
        self.session = session
        self.client_timeout = client_timeout
        self.headers = headers

    async def fetch_all_sources(self, sources: list[ProxySource]) -> list[ProxyAddress]:
        tasks: list[asyncio.Task] = []
        for source in sources:
            tasks.append(asyncio.create_task(self.fetch_source(source)))
        results: list[object] = await asyncio.gather(*tasks, return_exceptions=True)
        proxy_addresses: list[ProxyAddress] = []
        for result in results:
            if isinstance(result, list):
                proxy_addresses.extend(result)
        proxy_addresses = list(set(proxy_addresses))
        return proxy_addresses

    async def fetch_source(self, proxy_source: ProxySource) -> list[ProxyAddress]:
        try:
            async with self.session.get(
                proxy_source.url,
                headers=self.headers,
                timeout=self.client_timeout,
            ) as response:
                proxy_addresses: list[ProxyAddress] = await proxy_source.parse(
                    response, proxy_source
                )
                return proxy_addresses
        except Exception as e:
            err_msg: str = str(e)
            if isinstance(e, TimeoutError):
                err_msg = f"访问超时"
            elif len(str(e)) == 0:
                err_msg = f"未知错误"
            else:
                err_msg = f"{e}"
            try:
                error = type(e)(
                    f"{err_msg}\t{e.__class__}\tproxy_source:{proxy_source}"
                )
            except:
                error = Exception(
                    f"{err_msg}\t{e.__class__}\tproxy_source:{proxy_source}"
                )
            log.warning(error)
            raise error from e
