from attr import dataclass


@dataclass
class ProxySourceInfo:
    scheme: str
    url: str

    def __str__(self) -> str:
        return f"scheme:{self.scheme}\turl:{self.url}"
