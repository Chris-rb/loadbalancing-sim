from typing import Optional
from enum import Enum
from pydantic import BaseModel, ConfigDict, ValidationError, Field

from ..entities.Server import ServerState
from ..config import Config

class ServerData(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    server_id: int
    queue_size: int = Field(ge=0)
    server_state: ServerState
    
class Metrics(BaseModel):
    completed_requests: int
    dropped_requests: int
    arrival_time: float
    completed_time: float
    response_time: float
    response_time: float
    wait_time: float
    throughput: float
    p50: float
    p95: float
    p99: float

class SimData(BaseModel):
    t: int
    servers: list[ServerData]
    metrics: Metrics
    
class MessageType(Enum):
    SIM_CONFIG = "SIM_CONFIG"
    SIM_SPEED = "SIM_SPEED"
    
class WebSocketMessage(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    message: MessageType
    sim_config: Optional[Config] = None
    sim_speed: Optional[int] = None
