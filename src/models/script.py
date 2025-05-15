from dataclasses import dataclass

from .proxy_check_target import ProxyCheckTarget
from .proxy_source import ProxySource


@dataclass
class Script:
    proxy_sources: list[ProxySource]
    proxy_check_target: ProxyCheckTarget
