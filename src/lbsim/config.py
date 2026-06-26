import json
from dataclasses import dataclass


@dataclass
class Config:
    policy: str
    c: int                      # number of servers
    k: int                      # per-server queue capacity
    rho: float                  # target offered load
    seed: int                   # RNG seed for reproducibility
    max_requests: int           # max amount of requests per run
    warmup: int = 0             # amount of requests to discard before recording stats
    service_rate: float = 1.0   # mu
    
    def arrival_rate(self) -> float:
        return self.rho * self.c * self.service_rate
    
    @staticmethod
    def from_json(path: str) -> "Config":
        try:
            with open(path, "r") as config_json:
                config_data = json.load(config_json)
                
                config = Config(
                    policy = config_data["policy"],
                    c = config_json["c"],
                    k = config_json["k"],
                    rho = config_json["rho"],
                    seed = config_json["seed"],
                    max_requests = config_json["max_requests"],
                    warmup = config_json["warmup"],
                    service_rate = config_json["service_rate"]
                )
                
                return config
                
        except Exception as e:
            print(f"Unexpected error occured: {e}")