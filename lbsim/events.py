from dataclasses import dataclass
from typing import Optional
from enum import Enum

from .entities.Request import Request
from .entities.Server import Server

class EventKind(Enum):
    ARRIVAL = 0
    DEPARTURE = 1
    FAILURE = 2
    REPAIR = 3

@dataclass(order=True)
class Event:
    time: float
    kind: EventKind
    server_payload: Optional[Server] = None
    req_payload: Optional[Request] = None