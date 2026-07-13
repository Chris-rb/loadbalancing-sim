import numpy as np
from enum import Enum
from typing import Optional, Sequence
from abc import ABC, abstractmethod

from .entities.Request import Request
from .entities.Server import Server, ServerState

class PolicyTypes(Enum):
    RR = "Round Robin"
    LC = "Least Connections"
    PC = "Power of Two"


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
        if (avail_servers := self._available()) == []:
            return None
        
        
        server = avail_servers[self._cursor % len(avail_servers)]
        self._cursor += 1
        return server
    
class LeastConnections(LoadBalancer):
    
    def choose(self, request) -> Optional[Server]:
        if (avail_servers := self._available()) == []:
            return None
        
        return min(avail_servers, key=lambda s: s.queue_len())
    
    
class PowerOfTwo(LoadBalancer):
    
    def choose(self, request) -> Optional[Server]:
        rng = np.random.default_rng()
        server_options = np.array(self._available(), dtype=object)
        
        random_servers = rng.choice(server_options, size=2, replace=False)
        
        return min(random_servers, key=lambda s: s.queue_len())
        
def make_policy(name: str, servers: Sequence[Server]) -> LoadBalancer:
    if name == PolicyTypes.RR.value:
        return RoundRobin(servers)
    
    elif name == PolicyTypes.LC.value:
        return LeastConnections(servers)
    
    elif name == PolicyTypes.PC.value:
        return PowerOfTwo(servers)
    
    raise ValueError