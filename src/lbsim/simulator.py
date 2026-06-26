import heapq
from typing import Optional

from .config import Config
from .entities.Server import Server, Request, ServerState
from .policies import make_policy
from .events import Event, EventKind
from .distributions import Distributions
from .stats import StatsCollector

class Simulator:
    def __init__(self, config: Config):
        self.config = config
        self.clock: float = 0
        self._events: list[Event] = []
        self._next_request_id: int = 0
        
        self.dist = Distributions(
            seed=config.seed,
            arrival_rate=config.arrival_rate(),
            service_rate=config.service_rate
        )
        self.servers = [Server(id=i, queue_cap=config.k) for i in range(config.c)]
        self.balancer = make_policy(config.policy, self.servers)
        self.stats = StatsCollector(policy=config.policy, warmup=config.warmup)
        
    def schedule(self, event: Event) -> None:
        heapq.heappush(self._events, event)
        
    def _pop(self) -> Event:
        return heapq.heappop(self._events)
    
    def run(self) -> StatsCollector:
        arrival_event = self._make_arrival_event(at=self.dist.interarrival())
        self.schedule(arrival_event)
        
        while self._events and self.stats.finished_count < self.config.max_requests:
            event = self._pop()
            self.clock = event.time
            
            if event.kind == EventKind.ARRIVAL:
                self._handle_arrival(event)
            elif event.kind == EventKind.DEPARTURE:
                self._handle_departure(event)
                
        return self.stats
    
    def _make_arrival_event(self, at: float) -> Event:
        self._next_request_id += 1
        req_id = self._next_request_id
        demand = self.dist.service()
        t = self.clock + at
        req = Request(id=req_id, t_arrive=t, demand=demand)
        return Event(time=t, kind=EventKind.ARRIVAL, payload=req)
    
    def _handle_arrival(self, event: Event) -> None:
        arrival_event = self._make_arrival_event(at=self.dist.interarrival())
        self.schedule(arrival_event)
        chosen_server = self.balancer.choose(event.payload)
        
        server_state = chosen_server.state
        enqued_req = chosen_server.enqueue(event.payload)
        
        if enqued_req and server_state == ServerState.IDLE:
            departure_event = Event(self.clock + event.payload.demand, EventKind.DEPARTURE, chosen_server)
            self.schedule(departure_event)
        elif not enqued_req:
            self.stats.record_drop()
            
        if chosen_server is None:
            self.stats.record_drop()
            
    def _handle_departure(self, event: Event) -> None:
        finished_req = event.payload.finish_current()
        finished_req.t_done = self.clock
        self.stats.record_done(finished_req)
        
        if event.payload.state == ServerState.BUSY:
            self.schedule(Event(self.clock + event.payload.current_req.demand, EventKind.DEPARTURE, event.payload))
        