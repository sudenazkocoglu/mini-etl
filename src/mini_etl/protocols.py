from typing import Protocol, Iterator, Dict, Any, runtime_checkable

@runtime_checkable
class Source(Protocol):
    def read(self) -> Iterator[Dict[str, Any]]:
        ...

@runtime_checkable
class Transform(Protocol):
    def process(self, record: Dict[str, Any]) -> Dict[str, Any] | None:
        ...
    
    def __rshift__(self, other: "Transform") -> "Transform":
        ...

@runtime_checkable
class Sink(Protocol):
    def write(self, record: Dict[str, Any]) -> None:
        ...
    
    def close(self) -> None:
        ...