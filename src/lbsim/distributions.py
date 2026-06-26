import numpy as np


class Distributions:
    
    def __init__(self, seed: int, arrival_rate: float, service_rate: float = 1.0):
        self.rng = np.random.default_rng(seed)
        self.arrival_rate = arrival_rate
        self.service_rate = service_rate
        
    def interarrival(self) -> float:
        return self.rng.exponential(scale=(1/self.arrival_rate))
    
    def service(self) -> float:
        return self.rng.exponential(scale=(1/self.service_rate))