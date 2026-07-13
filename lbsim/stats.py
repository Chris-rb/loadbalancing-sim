import os
import sys
import csv
import numpy as np
from datetime import datetime

from .entities.Request import Request
from .policies import PolicyTypes

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(root_dir)

class StatsCollector:
    
    def __init__(self, policy: str, warmup: int = 0):
        self.policy = policy
        self.warmup = warmup
        self.id: int = 0
        self.pre_warmup_count: int = 0
        self.finished_count: int = 0
        self._t_warmup_complete: int = 0
        self._measured_time: int = 0
        self.drop_count: int = 0
        self._records: list[dict] = []
        self._response_times: list[float] = []
        self._completed_times: list[float] = []
        self._wait_times: list[float] = []
    
    
    def record_done(self, request: Request) -> None:
        self.pre_warmup_count += 1
        if self.pre_warmup_count < self.warmup:
            return
        elif self.pre_warmup_count == self.warmup:
            self._t_warmup_complete = request.t_done
            return
        self.id += 1
        self.finished_count += 1
        self._measured_time = request.t_done - self._t_warmup_complete
        rt = request.response_time()
        ct = request.complete_time()
        wt = request.wait_time()
        
        self._response_times.append(rt)
        self._completed_times.append(ct)
        self._wait_times.append(wt)
        
        print(F"\n\n{self._measured_time}\n\n")
        
        resp_times = np.array(self._response_times)
        self._records.append({
            "id": self.id,
            "completed_requests": self.finished_count,
            "dropped_requests": self.drop_count,
            "arrival_time": request.t_arrive,
            "completed_time": self.mean_completed_time(),
            "response_time": self.mean_response_time(),
            "wait_time": self.mean_wait_time(),
            "throughput": self.throughput(),
            "p50": np.percentile(resp_times, 50),
            "p95": np.percentile(resp_times, 95),
            "p99": np.percentile(resp_times, 99),
        })
        
    def current_snapshot(self):
        if not self._records:
            return {
                "completed_requests": 0,
                "dropped_requests": 0,
                "arrival_time": 0,
                "completed_time": 0,
                "response_time": 0,
                "wait_time": 0,
                "throughput": 0,
                "p50": 0,
                "p95": 0,
                "p99": 0,
            }
        
        return self._records[-1]
    
    def record_drop(self, request: Request = None) -> None:
        self.pre_warmup_count += 1
        request.dropped = True
        if (self.pre_warmup_count <= self.warmup):
            return
        self.drop_count += 1
        
    def mean_response_time(self) -> float:
        if len(self._response_times) == 0:
            return 0
        return (sum(self._response_times) / len(self._response_times))
    
    def mean_completed_time(self) -> int:
        if len(self._completed_times) == 0:
            return 0
        return sum(self._completed_times) / len(self._completed_times)
    
    def mean_wait_time(self) -> int:
        if len(self._wait_times) == 0:
            return 0
        return sum(self._wait_times) / len(self._wait_times)
        
    def throughput(self):
        if self._measured_time == 0:
            return 0
        return self.finished_count / self._measured_time
    
    def summary(self) -> None:
        print(f"Policy: \t\t{self.policy}")
        print(f"Completed requests: \t{self.finished_count}")
        print(f"Droped requests: \t{self.drop_count}")
        print(f"Average service time: \t{self.mean_response_time()}")
    
    def write_csv(self) -> str:
        now = datetime.now()
        cwd = os.getcwd()
        report_csv = f"lb_sim_report_{now.strftime("%Y%m%dT%H%M%S")}.csv"
        if self.policy == PolicyTypes.RR.value:
            report_csv = "RR_" + report_csv
        elif self.policy == PolicyTypes.LC.value:
            report_csv = "LC_" + report_csv
        else:
            report_csv = "PC_" + report_csv
        
        report_dir = os.path.join(cwd, "reports")
        os.makedirs(report_dir, exist_ok=True)
        report_path = os.path.join(report_dir, report_csv)
        
        headers = [
            "completed_requests",
            "dropped_requests",
            "arrival_time",
            "completed_time",
            "response_time",
            "wait_time",
            "throughput",
            "p50",
            "p95",
            "p99"
        ]

        self._records.sort(key=lambda s: s["id"])
        
        try:
            with open(report_path, "w") as report_file:
                writer = csv.DictWriter(report_file, fieldnames=headers, extrasaction='ignore')
                writer.writeheader()
                writer.writerows(self._records)
        except Exception as e:
            print(f"Unexpected error occured: {e}")
            
        return report_path
    