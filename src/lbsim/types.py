from enum import Enum

class PolicyTypes(Enum):
    RR = "Round Robin"
    LC = "Least Connections"