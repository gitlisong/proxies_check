import logging
import re

import aiohttp

from src.models.proxy_address import ProxyAddress
from src.models.proxy_check_target import ProxyCheckTarget
from src.models.proxy_server import ProxyServer
from src.models.proxy_source import ProxySource
from src.models.script import Script

log = logging.getLogger("app")


class ScriptError(Exception): ...


class StatusError(ScriptError): ...


class InvalidSource(ScriptError): ...


class InvalidData(ScriptError): ...


class InvalidDataLength(ScriptError): ...


async def custom_parse(
    response: aiohttp.ClientResponse, proxy_source: ProxySource
) -> list[ProxyAddress]:
    if response.ok:
        if response.content_type == "text/plain":
            text: str = await response.text()
            proxy_arr = re.findall(r"(\d{1,3}(?:\.\d{1,3}){3}):(\d+)", text)
            if len(proxy_arr) == 0:
                raise InvalidSource(f"获取到的代理池是空的\ttext:{text}")
            proxy_addresses: list[ProxyAddress] = []
            scheme: str = "http"
            if proxy_source.scheme is not None:
                scheme = proxy_source.scheme
            for host, port in proxy_arr:
                proxy_addresses.append(
                    ProxyAddress(
                        scheme=scheme,
                        host=host,
                        port=int(port),
                    )
                )
            log.info(f"成功\t{proxy_source}")
            return proxy_addresses
        else:
            raise TypeError(f"返回的类型错误\tcontent_type:{response.content_type}")
    else:
        raise StatusError(f"状态码无效\tstatus:{response.status}")


async def auto_parse(
    response: aiohttp.ClientResponse, proxy_source: ProxySource
) -> list[ProxyAddress]:
    if response.ok:
        if response.content_type == "text/plain":
            text: str = await response.text()
            proxy_arr = re.findall(
                r"(https|http):\/\/(\d{1,3}(?:\.\d{1,3}){3}):(\d+)", text
            )
            if len(proxy_arr) == 0:
                raise InvalidSource(f"获取到的代理池是空的\ttext:{text}")
            proxies: list[ProxyAddress] = []
            for scheme, host, port in proxy_arr:
                proxies.append(
                    ProxyAddress(
                        scheme=scheme,
                        host=host,
                        port=int(port),
                    )
                )
            log.info(f"成功\t{proxy_source}")
            return proxies
        else:
            raise TypeError(f"返回的类型错误\tcontent_type:{response.content_type}")
    else:
        raise StatusError(f"状态码无效\tstatus:{response.status}")


proxy_sources: list[ProxySource] = [
    ProxySource(
        parse=custom_parse,
        scheme="https",
        url="https://raw.githubusercontent.com/r00tee/Proxy-List/refs/heads/main/Https.txt",
    ),
    ProxySource(
        parse=custom_parse,
        scheme="https",
        url="https://raw.githubusercontent.com/roosterkid/openproxylist/refs/heads/main/HTTPS_RAW.txt",
    ),
    ProxySource(
        parse=custom_parse,
        scheme="https",
        url="https://raw.githubusercontent.com/databay-labs/free-proxy-list/refs/heads/master/https.txt",
    ),
    ProxySource(
        parse=auto_parse,
        url="https://raw.githubusercontent.com/trio666/proxy-checker/refs/heads/main/https.txt",
    ),
    ProxySource(
        parse=custom_parse,
        scheme="http",
        url="https://raw.githubusercontent.com/vakhov/fresh-proxy-list/refs/heads/master/http.txt",
    ),
    ProxySource(
        parse=custom_parse,
        scheme="http",
        url="https://raw.githubusercontent.com/Konorze/public-proxies/refs/heads/main/proxies_http.txt",
    ),
    ProxySource(
        parse=custom_parse,
        scheme="http",
        url="https://raw.githubusercontent.com/databay-labs/free-proxy-list/refs/heads/master/http.txt",
    ),
    ProxySource(
        parse=auto_parse,
        url="https://raw.githubusercontent.com/trio666/proxy-checker/refs/heads/main/http.txt",
    ),
    ProxySource(
        parse=custom_parse,
        scheme="https",
        url="https://raw.githubusercontent.com/MrMarble/proxy-list/refs/heads/main/all.txt",
    ),
]
github_proxy = "https://github.moeyy.xyz"
for proxy_source in proxy_sources:
    proxy_source.url = f"{github_proxy}/{proxy_source.url}"


async def ckeck(
    response: aiohttp.ClientResponse, proxy_address: ProxyAddress
) -> ProxyServer:
    if response.ok:
        if response.content_type == "text/html":
            if response.content_length == 11:
                text: str = await response.text()
                if "mb,1,安卓" in text:
                    log.info(f"成功\t{proxy_address}")
                    proxy_server: ProxyServer = ProxyServer(**proxy_address.__dict__)
                    return proxy_server
                else:
                    raise InvalidData(f"无效的数据\ttext:{text}")
            else:
                raise InvalidDataLength(
                    f"无效的数据长度\tcontent_length:{response.content_length}"
                )
        else:
            raise TypeError(f"返回的类型错误\tcontent_type:{response.content_type}")
    else:
        raise StatusError(f"状态码无效\tstatus:{response.status}")


proxy_check_target: ProxyCheckTarget = ProxyCheckTarget(
    website="sapi.egvra.cn/m/test.aspx", check=ckeck
)

script: Script = Script(
    proxy_sources=proxy_sources, proxy_check_target=proxy_check_target
)
