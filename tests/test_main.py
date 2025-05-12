from email import header
import logging
import re
import unittest

import aiohttp

from src.services.proxy_check_service import ProxyCheckService
from src.errors.error import EmptyData, InvalidData, InvalidSource, StatusError
from src.models.proxy_address import ProxyAddress
from src.models.proxy_check_target import ProxyCheckTarget
from src.models.proxy_server import ProxyServer
from src.models.proxy_source import ProxySource
from src.models.proxy_source_info import ProxySourceInfo
from src.services.proxy_source_service import ProxySourceService

log = logging.getLogger("app")
log.setLevel(logging.DEBUG)

file_handler = logging.FileHandler(filename="app.log", mode="w")
file_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)

log.addHandler(file_handler)
stream_handler = logging.StreamHandler()
stream_handler.setFormatter(
    logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
)
log.addHandler(stream_handler)


class TestMain(unittest.IsolatedAsyncioTestCase):
    @staticmethod
    async def my_parse(
        response: aiohttp.ClientResponse, proxy_source: ProxySource
    ) -> list[ProxyAddress]:
        if response.ok:
            if response.content_type == "text/plain":
                text: str = await response.text()
                proxy_arr = re.findall(r"(\d{1,3}(?:\.\d{1,3}){3}):(\d+)", text)
                if len(proxy_arr) == 0:
                    raise InvalidSource(f"获取到的代理池是空的\ttext:{text}")
                proxies: list[ProxyAddress] = []
                for host, port in proxy_arr:
                    proxies.append(
                        ProxyAddress(
                            scheme=proxy_source.proxy_source_info.scheme,
                            host=host,
                            port=int(port),
                        )
                    )
                log.info(f"成功{proxy_source}")
                return proxies
            else:
                raise TypeError(f"返回的类型错误\tcontent_type:{response.content_type}")
        else:
            raise StatusError(f"状态码无效\tstatus:{response.status}")

    github_proxy = "https://github.moeyy.xyz"
    proxy_source_infos: list[ProxySourceInfo] = [
        ProxySourceInfo(
            scheme="https",
            url="https://raw.githubusercontent.com/r00tee/Proxy-List/refs/heads/main/Https.txt",
        ),
        ProxySourceInfo(
            scheme="https",
            url="https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/HTTPS_RAW.txt",
        ),
        ProxySourceInfo(
            scheme="https",
            url="https://raw.githubusercontent.com/databay-labs/free-proxy-list/refs/heads/master/https.txt",
        ),
        ProxySourceInfo(
            scheme="https",
            url="https://raw.githubusercontent.com/trio666/proxy-checker/refs/heads/main/https.txt",
        ),
        ProxySourceInfo(
            scheme="http",
            url="https://raw.githubusercontent.com/vakhov/fresh-proxy-list/refs/heads/master/http.txt",
        ),
        ProxySourceInfo(
            scheme="http",
            url="https://raw.githubusercontent.com/Konorze/public-proxies/refs/heads/main/proxies_http.txt",
        ),
        ProxySourceInfo(
            scheme="http",
            url="https://raw.githubusercontent.com/databay-labs/free-proxy-list/refs/heads/master/http.txt",
        ),
        ProxySourceInfo(
            scheme="http",
            url="https://raw.githubusercontent.com/trio666/proxy-checker/refs/heads/main/http.txt",
        ),
        ProxySourceInfo(
            scheme="https",
            url="https://raw.githubusercontent.com/MrMarble/proxy-list/refs/heads/main/all.txt",
        ),
    ]

    @staticmethod
    async def ckeck(response: aiohttp.ClientResponse, proxy_address: ProxyAddress):
        if response.ok:
            if response.content_type == "text/plain":
                text: str = await response.text()
                if "mb,1,安卓" in text:
                    log.info(f"成功\t{proxy_address}")
                    return ProxyServer(**proxy_address.__dict__)
                else:
                    raise InvalidData(f"无效的数据\ttext:{text}")
            else:
                raise TypeError(f"返回的类型错误\tcontent_type:{response.content_type}")
        else:
            raise StatusError(f"状态码无效\tstatus:{response.status}")

    proxy_check_target: ProxyCheckTarget = ProxyCheckTarget(
        website="ipv4.icanhazip.com", check=ckeck
    )

    proxy_sources: list[ProxySource] = []
    for proxy_source in proxy_source_infos:
        proxy_source.url = f"{github_proxy}/{proxy_source.url}"
        proxy_sources.append(
            ProxySource(proxy_source_info=proxy_source, parse=my_parse)
        )
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; Pixel 4 XL Build/QD1A.190505.018) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.149 Mobile Safari/537.36"
    }

    async def test_a(self):
        tcp_connector = aiohttp.TCPConnector(limit=1000, verify_ssl=False)
        client_timeout: aiohttp.ClientTimeout = aiohttp.ClientTimeout(total=5)
        async with aiohttp.ClientSession(connector=tcp_connector) as session:
            proxy_pool_service: ProxySourceService = ProxySourceService(
                session=session, headers=self.headers, client_timeout=client_timeout
            )
            proxy_addresses: list[ProxyAddress] = (
                await proxy_pool_service.fetch_all_sources(self.proxy_sources)
            )

            proxy_check_service: ProxyCheckService = ProxyCheckService(
                session=session,
                headers=self.headers,
                client_timeout=client_timeout,
                proxy_check_target=self.proxy_check_target,
            )

            await proxy_check_service.check_all_proxies(
                proxy_addresses=proxy_addresses,
            )
