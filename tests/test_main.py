import asyncio
import logging
import socket
import time
import unittest

import aiohttp

from src.models.proxy_address import ProxyAddress
from src.models.script import Script
from src.services.config import Config
from src.services.proxy_source_service import ProxySourceService

log: logging.Logger = Config.init_log(logging.getLogger("app"))


class TestMain(unittest.IsolatedAsyncioTestCase):
    a = asyncio.Semaphore(1000)

    async def socket_test(self, proxy_address: ProxyAddress):
        s = socket.socket()
        s.setblocking(False)
        loop = asyncio.get_event_loop()
        async with self.a:
            try:
                t = time.time() * 1000
                await asyncio.wait_for(
                    loop.sock_connect(s, (proxy_address.host, proxy_address.port)),
                    10,
                )
                log.info(f"成功{proxy_address}\t耗时:{(time.time()*1000)-t}")
                return proxy_address
            except Exception as e:
                log.info(f"失败{proxy_address}\t耗时:{(time.time()*1000)-t}")
                raise
            finally:
                s.close()

    async def test_main(self):

        script: Script = Config.load_script("script.py", "script")

        tcp_connector = aiohttp.TCPConnector(limit=1000, verify_ssl=False)
        client_timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=5)
        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL Build/QD1A.190505.018) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36"
        }

        async with aiohttp.ClientSession(connector=tcp_connector) as session:
            proxy_source_service: ProxySourceService = ProxySourceService(
                session=session, headers=headers, client_timeout=client_timeout
            )
            proxy_addresses: list[ProxyAddress] = (
                await proxy_source_service.fetch_all_sources(script.proxy_sources)
            )
            log.info(f"数量:{len(proxy_addresses)}")
        tasks: list[asyncio.Task] = []
        for proxy_address in proxy_addresses:
            tasks.append(asyncio.create_task(self.socket_test(proxy_address)))
        t = time.time() * 1000
        results: list[object] = await asyncio.gather(*tasks, return_exceptions=True)
        print(f"耗时:{(time.time() * 1000)-t}")
        proxy_addresses_ok: list[ProxyAddress] = []
        for result in results:
            if isinstance(result, ProxyAddress):
                proxy_addresses_ok.append(result)
        log.info(f"成功:{len(proxy_addresses_ok)}")
