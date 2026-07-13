from dataclasses import dataclass
from typing import Optional

@dataclass
class Request:
    id: int
    demand: float
    t_arrive: float
    t_start: Optional[float] = None
    t_done: Optional[float] = None
    dropped: Optional[bool] = False
    
    def wait_time(self) -> float:
        if self.t_start is None:
            raise Exception
        return self.t_start - self.t_arrive
    
    def response_time(self) -> float:
        if self.t_done is None:
            raise Exception
        return self.t_done - self.t_arrive
    
    def complete_time(self) -> float:
        if self.t_done is None:
            raise Exception
        return self.t_done - self.t_start