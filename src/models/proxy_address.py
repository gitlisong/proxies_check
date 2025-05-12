from dataclasses import dataclass


@dataclass
class ProxyAddress:
    scheme: str
    host: str
    port: int

    def __str__(self) -> str:
        return f"{self.scheme}://{self.host}:{self.port}"

    def __eq__(self, value: object) -> bool:
        if isinstance(value, ProxyAddress):
            return (
                self.scheme == value.scheme
                and self.host == value.host
                and self.port == value.port
            )
        return False

    def __hash__(self):
        return hash((self.scheme, self.host, self.port))
