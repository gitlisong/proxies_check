import asyncio
import logging
from ssl import SSLError

import aiohttp

from ..models.proxy_address import ProxyAddress
from ..models.proxy_check_target import ProxyCheckTarget
from ..models.proxy_server import ProxyServer

log = logging.getLogger("app")


class ProxyGetCheckService:
    def __init__(
        self,
        session: aiohttp.ClientSession,
        client_timeout: aiohttp.ClientTimeout,
        headers: dict,
        proxy_check_target: ProxyCheckTarget,
    ) -> None:
        self.session = session
        self.client_timeout = client_timeout
        self.headers = headers
        self.proxy_check_target = proxy_check_target
        self.semaphore = asyncio.Semaphore(
            self.session.connector.limit if self.session.connector else 1
        )

    async def check_all_proxies(
        self, proxy_addresses: list[ProxyAddress]
    ) -> list[ProxyServer]:
        tasks: list[asyncio.Task] = []
        for proxy_address in proxy_addresses:
            tasks.append(asyncio.create_task(self.check_proxy(proxy_address)))
        results: list[object] = await asyncio.gather(*tasks, return_exceptions=True)
        proxy_servers: list[ProxyServer] = []
        for result in results:
            if isinstance(result, ProxyServer):
                proxy_servers.append(result)
        return proxy_servers

    async def check_proxy(self, proxy_address: ProxyAddress) -> ProxyServer:
        async with self.semaphore:
            while True:
                url: str = ""
                if self.proxy_check_target.scheme == None:
                    url = f"{proxy_address.scheme}://{self.proxy_check_target.website}"
                else:
                    url = f"{self.proxy_check_target.scheme}://{self.proxy_check_target.website}"
                try:
                    try:
                        async with self.session.get(
                            url,
                            headers=self.headers,
                            timeout=self.client_timeout,
                            proxy=str(proxy_address),
                        ) as response:
                            proxy_server: ProxyServer = (
                                await self.proxy_check_target.check(
                                    response, proxy_address
                                )
                            )
                            return proxy_server
                    except SSLError as e:
                        if proxy_address.scheme == "https":
                            log.warning(f"使用http重试\tproxy_address:{proxy_address}")
                            proxy_address.scheme = "http"
                            continue
                        else:
                            raise
                except Exception as e:
                    err_msg: str = str(e)
                    if isinstance(e, TimeoutError):
                        err_msg = f"访问超时"
                    elif isinstance(e, aiohttp.ClientOSError):
                        err_msg = f"连接失败"
                    elif len(str(e)) == 0:
                        err_msg = f"未知错误"
                    elif isinstance(e, aiohttp.ClientError):
                        err_msg = f"无效的代理"
                    else:
                        err_msg = f"{e}"
                    try:
                        error = type(e)(
                            f"{err_msg}\t{e.__class__}\tproxy_address:{proxy_address}"
                        )
                    except:
                        error = Exception(
                            f"{err_msg}\t{e.__class__}\tproxy_address:{proxy_address}"
                        )
                    log.warning(error)
                    raise error from e
