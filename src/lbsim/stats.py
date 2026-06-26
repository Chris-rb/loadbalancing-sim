import os
import sys
import csv
from datetime import datetime

from .entities.Request import Request
from .policies import PolicyTypes

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(root_dir)

class StatsCollector:
    
    def __init__(self, policy: str, warmup: int = 0):
        self.policy = policy
        self.warmup = warmup
        self.finished_count: int = 0
        self.drop_count: int = 0
        self._records: list[dict] = []
        self._response_times: list[float] = []
    
    def record_done(self, request: Request) -> None:
        self.finished_count += 1
        if self.finished_count <= self.warmup:
            return

        rt = request.reponse_time()
        self._response_times.append(rt)
        self._records.append({
            "id": request.id,
            "arrival_time": request.t_arrive,
            "completed_time": request.t_done,
            "response_time": request.reponse_time()
        })
        
    def record_drop(self, request: Request) -> None:
        self.drop_count += 1
        
    def mean_response_time(self) -> float:
        if len(self._response_times) == 0:
            return 0
        
        return sum(self._response_times[self.warmup:]) / (len(self._response_times) - self.warmup)
    
    def summary(self) -> None:
        print(f"Policy: \t\t{self.policy}")
        print(f"Completed requests: \t{self.finished_count}")
        print(f"Droped requests: \t{self.drop_count}")
        print(f"Average service time: \t{self.mean_response_time()}")
    
    def write_csv(self) -> None:
        now = datetime.now()
        cwd = os.getcwd()
        report_csv = f"load_balancing_sim_report_{now.strftime("%Y%m%dT%H%M%S")}.csv"
        if self.policy == PolicyTypes.RR.value:
            report_csv = "RR_" + report_csv
        else:
            report_csv = "LC_" + report_csv
        report_path = os.path.join(cwd, "reports", report_csv)
        
        headers = [
            "id",
            "arrival_time",
            "completed_time",
            "response_time"
        ]
        self._records.sort(key=lambda s: s["id"])
        
        try:
            with open(report_path, "w") as report_file:
                writer = csv.DictWriter(report_file, fieldnames=headers)
                writer.writeheader()
                writer.writerows(self._records)
        except Exception as e:
            print(f"Unexpected error occured: {e}")
                