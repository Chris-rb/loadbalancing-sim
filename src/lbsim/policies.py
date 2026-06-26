from enum import Enum
from typing import Optional, Sequence
from abc import ABC, abstractmethod

from .entities.Request import Request
from .entities.Server import Server, ServerState

class PolicyTypes(Enum):
    RR = "Round Robin"
    LC = "Least Connections"


class LoadBalancer(ABC):
    
    def __init__(self, servers: Sequence[Server]):
        self.servers = servers
    
    @abstractmethod
    def choose(self, request: Request) -> Optional[Server]:
        pass
    
    def _available(self) -> list[Server]:
        return [server for server in self.servers if server.state is not ServerState.FAILED]
    
    
class RoundRobin(LoadBalancer):
    
    def __init__(self, servers):
        super().__init__(servers)
        self._cursor = 0
    
    def choose(self, request) -> Optional[Server]:
        if (avail_servers := self._available()) == None:
            return None
        
        self._cursor += 1
        return avail_servers[self._cursor % len(avail_servers)]
    
class LeastConnections(LoadBalancer):
    
    def choose(self, request) -> Optional[Server]:
        if (avail_servers := self._available()) == None:
            return None
        
        return min(avail_servers, key=lambda s: s.queue_len())
    
def make_policy(name: str, servers: Sequence[Server]) -> LoadBalancer:
    if name == PolicyTypes.RR.value:
        return RoundRobin(servers)
    
    elif name == PolicyTypes.LC.value:
        return LeastConnections(servers)
    
    raise ValueError