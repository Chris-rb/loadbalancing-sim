from dataclasses import dataclass
from enum import Enum
from collections import deque
from typing import Optional

from .Request import Request


class ServerState(Enum):
    IDLE = "IDLE"
    BUSY = "BUSY"
    FAILED = "FAILED"

@dataclass
class Server:
    id: int
    queue: deque[Request]
    queue_cap: int
    state: ServerState = ServerState.IDLE
    current_req: Optional[Request] = None
    
    def __init__(self, id, queue_cap):
        self.id = id
        self.queue_cap = queue_cap
        self.queue = deque(maxlen=self.queue_cap)
    
    def queue_len(self) -> int:
        return len(self.queue)
    
    def is_full(self) -> bool:
        return self.queue_len() == self.queue_cap
    
    def enqueue(self, request: Request) -> bool:
        if self.is_full():
            return False
        
        if self.state == ServerState.IDLE:
            self.current_req = request
            self.state = ServerState.BUSY
            return True
        
        self.queue.append(request)
        return True
        
    def finish_current(self) -> Request:
        if self.current_req is None:
            raise Exception("No request currently active")
        
        finished_req = self.current_req
        if self.queue_len() > 0:
            self.current_req = self.queue.pop()
        
        elif self.queue_len() == 0:
            self.state = ServerState.IDLE
            self.current_req = None
            
        return finished_req
                
            