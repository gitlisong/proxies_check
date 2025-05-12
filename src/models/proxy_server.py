from attr import dataclass

from .proxy_address import ProxyAddress


@dataclass
class ProxyServer(ProxyAddress):
    response_time: int | None = None
    retry_count: int | None = None
    
    def __str__(self) -> str:
        s: str = super().__str__()
        if self.response_time is not None:
            s += str(f"\ttime:{self.response_time}")
        if self.retry_count is not None:
            s += str(f"\tretry:{self.retry_count}")
        return s