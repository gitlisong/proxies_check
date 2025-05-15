import asyncio
import logging
import socket

import aiohttp

from src.models.proxy_address import ProxyAddress
from src.models.proxy_server import ProxyServer
from src.services.proxy_get_check_service import ProxyGetCheckService
from src.services.proxy_source_service import ProxySourceService
from src.models.script import Script
from src.services.config import Config


async def main():
    log: logging.Logger = Config.init_log(logging.getLogger("app"))
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
        proxy_get_check_service: ProxyGetCheckService = ProxyGetCheckService(
            session=session,
            headers=headers,
            client_timeout=client_timeout,
            proxy_check_target=script.proxy_check_target,
        )

        proxy_servers: list[ProxyServer] = (
            await proxy_get_check_service.check_all_proxies(
                proxy_addresses=proxy_addresses,
            )
        )
        log.info(f"成功数量:{len(proxy_servers)}")


if __name__ == "__main__":
    asyncio.run(main())
