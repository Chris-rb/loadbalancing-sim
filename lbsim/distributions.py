from enum import Enum
import numpy as np
import math

class ServiceDist(Enum):
    exponential = "exponential"
    lognormal = "lognormal"

class Distributions:
    
    def __init__(
        self, 
        seed: int, 
        arrival_rate: float,
        MTBF: int,
        MTTR: int,
        service_rate: float = 1.0,
        service_dist: ServiceDist = ServiceDist.lognormal.value,
        service_cv: int = 3
    ):
        self.rng = np.random.default_rng(seed)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        self.MTTR = MTTR 
        self.MTBF = MTBF
        self.service_dist = service_dist
        self.service_cv = service_cv
        
        mean = 1 / service_rate
        
        self._sigma_log = math.sqrt(math.log(1 + service_cv**2))
        self._mu_log = math.log(mean) - self._sigma_log**2 / 2
        
    def interarrival(self) -> float:
        return self.rng.exponential(scale=(1/self.arrival_rate))
    
    def failure_time(self) -> float:
        return self.rng.exponential(scale=self.MTBF)
    
    def repair_time(self) -> float:
        return self.rng.exponential(scale=self.MTTR)
    
    def service(self) -> float:
        if self.service_dist == "lognormal":
            return self.rng.lognormal(mean=self._mu_log, sigma=self._sigma_log)
        return self.rng.exponential(scale=(1/self.service_rate))