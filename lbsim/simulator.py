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
        self._next_req_id: int = 0
        
        self.dist = Distributions(
            seed=config.seed,
            arrival_rate=config.arrival_rate(),
            MTBF=config.MTBF,
            MTTR=config.MTTR,
            service_rate=config.service_rate
        )
        self.servers = [Server(id=i, queue_cap=config.k) for i in range(config.c)]
        self.balancer = make_policy(config.policy, self.servers)
        self.stats = StatsCollector(policy=config.policy, warmup=config.warmup)
        
    def schedule(self, event: Event) -> None:
        heapq.heappush(self._events, event)
        
    def _pop(self) -> Event:
        return heapq.heappop(self._events)
    
    def run_static(self) -> StatsCollector:
        # initialize first arrivals
        arrival_event = self._make_arrival_event(at=self.dist.interarrival())
        self.schedule(arrival_event)
        
        if self.config.failures_enabled:
            # initialize failure events for each server
            for server in self.servers:
                self.schedule(
                    self._make_failure_event(at=self.dist.failure_time(), server=server)
                )
        
        while self._events and self.stats.finished_count < self.config.max_requests:
            event = self._pop()
            self.clock = event.time
            
            if event.kind == EventKind.ARRIVAL:
                self._handle_arrival(event.req_payload)
            elif event.kind == EventKind.DEPARTURE:
                self._handle_departure(event.server_payload)
            elif event.kind == EventKind.FAILURE:
                self._handle_failure(event.server_payload)
            elif event.kind == EventKind.REPAIR:
                self._handle_repair(event.server_payload)
                
        return self.stats
    
    async def run_steam(self):
        # initialize first arrivals
        arrival_event = self._make_arrival_event(at=self.dist.interarrival())
        self.schedule(arrival_event)
        
        if self.config.failures_enabled:
            # initialize failure events for each server
            for server in self.servers:
                self.schedule(
                    self._make_failure_event(at=self.dist.failure_time(), server=server)
                )
        
        while self._events and self.stats.finished_count < self.config.max_requests:
            event = self._pop()
            self.clock = event.time
            
            if event.kind == EventKind.ARRIVAL:
                self._handle_arrival(event.req_payload)
            elif event.kind == EventKind.DEPARTURE:
                self._handle_departure(event.server_payload)
            elif event.kind == EventKind.FAILURE:
                self._handle_failure(event.server_payload)
            elif event.kind == EventKind.REPAIR:
                self._handle_repair(event.server_payload)
                
            yield {
                "t": round((self.clock - self.stats._t_warmup_complete), 4),
                "servers": [
                    {"server_id": server.id, "queue_size": server.queue_len(), "server_state": server.state.value}
                    for server in self.servers
                ],
                "metrics": { **self.stats.current_snapshot() }
            }
    
    def _make_arrival_event(self, at: float) -> Event:
        self._next_req_id += 1
        req_id = self._next_req_id
        demand = self.dist.service()
        t = self.clock + at
        req = Request(id=req_id, t_arrive=t, demand=demand)
        return Event(time=t, kind=EventKind.ARRIVAL, req_payload=req)
    
    def _make_failure_event(self, at: float, server: Server) -> Event:
        t = self.clock + at
        return Event(
            time=t,
            kind=EventKind.FAILURE,
            server_payload=server
        )
        
    def _handle_arrival(self, request: Request) -> None:
        arrival_event = self._make_arrival_event(at=self.dist.interarrival())
        self.schedule(arrival_event)
        chosen_server = self.balancer.choose(request)
        
        if chosen_server is None:
            self.stats.record_drop(request)
            return
        
        server_state = chosen_server.state
        
        # Request ARRIVES at chosen server queue if possible
        enqued = chosen_server.enqueue(request)
        
        if enqued:
            departure_event = Event(
                time=self.clock + request.demand, 
                kind=EventKind.DEPARTURE,
                server_payload=chosen_server
            )
        else:
            self.stats.record_drop(request)
            return
        
        if server_state == ServerState.IDLE:
            request.t_start = self.clock
            self.schedule(departure_event)
        
            
    def _handle_departure(self, server: Server) -> None:
        # ignore deperture events for requests that were dropped during failure events
        if server.state != ServerState.BUSY or server.current_req is None:
            return
        
        finished_req = server.finish_current()
        finished_req.t_done = self.clock
        self.stats.record_done(finished_req)
        
        if server.state == ServerState.BUSY:
            server.current_req.t_start = self.clock
            self.schedule(
                Event(
                    time=self.clock + server.current_req.demand, 
                    kind=EventKind.DEPARTURE,
                    server_payload=server
                    )
                )
            
    def _handle_failure(self, failed_server: Server) -> None:
        failed_server.state = ServerState.FAILED
        
        if failed_server.current_req:
            self.stats.record_drop(failed_server.current_req)
            failed_server.current_req = None
            
        while failed_server.queue:
            self.stats.record_drop(failed_server.queue.popleft())
            
        self.schedule(
            Event(
                time=self.clock + self.dist.repair_time(),
                kind=EventKind.REPAIR,
                server_payload=failed_server
            )
        )
            
    def _handle_repair(self, repaired_server: Server) -> None:
        repaired_server.state = ServerState.IDLE
        
        self.schedule(
            Event(
                time=self.clock + self.dist.failure_time(),
                kind=EventKind.FAILURE,
                server_payload=repaired_server
            )
        )
        