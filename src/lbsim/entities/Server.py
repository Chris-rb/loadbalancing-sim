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
        
        if self.queue_len() > 0:
            finished_req = self.current_req
            self.current_req = self.queue.pop()
            
            if self.queue_len() == 0:
                self.state = ServerState.IDLE
                self.current_req = None
                
            return finished_req
                
            