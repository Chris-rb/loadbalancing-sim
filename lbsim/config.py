import json
import traceback
from pydantic import BaseModel, ConfigDict, ValidationError, Field

from .policies import PolicyTypes
from .distributions import ServiceDist

class Config(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    policy: PolicyTypes
    c: int = Field(gt=0)                      # number of servers
    k: int = Field(gt=0)                      # per-server queue capacity
    rho: float = Field(gt=0, lt=1)            # target offered load
    seed: int                                 # RNG seed for reproducibility
    max_requests: int = Field(gt=0)           # max amount of requests per run
    warmup: int = 0                           # amount of requests to discard before recording stats
    service_rate: float = 1.0                 # mu
    failures_enabled: bool = False            # If failures are enabled and MTBF and MTTR can be configure
    MTBF: int = 50                            # how often a failure event occurs between requests
    MTTR: int = 2000                          # mean time to repair
    service_dist: ServiceDist = "lognormal"
    service_csv: int = 3
    
    def arrival_rate(self) -> float:
        return self.rho * self.c * self.service_rate
    
    @staticmethod
    def from_json(path: str) -> "Config":
        try:
            with open(path, "r") as config_json:
                config_data = json.load(config_json)
                
                config = Config(
                    policy = config_data["policy"],
                    c = config_data["c"],
                    k = config_data["K"],
                    rho = config_data["rho"],
                    seed = config_data["seed"],
                    max_requests = config_data["max_requests"],
                    warmup = config_data["warmup"],
                    service_rate = config_data["service_rate"],
                    failures_enabled = config_data["failures_enabled"],
                    MTBF = config_data["MTBF"],
                    MTTR = config_data["MTTR"],
                    service_dist = config_data["service_dist"],
                    service_cv = config_data["service_cv"]
                )
                
                return config
                
        except Exception as e:
            print(f"[config] Unexpected error occured: {e}")
            traceback.print_exc()