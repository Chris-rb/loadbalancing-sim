# loadbalancing-sim

A from-scratch discrete-event simulation of load balancing in a server cluster. It compares dispatching policies — how a load balancer decides which server handles each incoming request — under random arrivals and random service times, and measures the response times that result.

The question it answers: when a web service runs across many servers, does a smart routing policy actually beat a simple one, and by how much? The simulator builds a virtual cluster, sends thousands of requests through it under each policy, and reports the difference.

## What it does

The simulator models one load balancer in front of `c` servers, each with its own finite FIFO queue. Requests arrive at random (a Poisson process), each needs a random amount of service time, and the active policy decides which server each one goes to. The engine advances through events on a virtual clock, so thousands of requests across a busy cluster simulate in a fraction of a second.

Two dispatching policies are implemented:

- Round Robin — cycles through servers in order; uses no information about their state. The simple baseline.
- Least Connections — sends each request to the server with the shortest queue right now. The full-information policy.

Output is a per-request CSV plus a printed summary (mean response time, completions, drops), so results are reproducible and can be analyzed after the fact.

> A note on units: all times are in simulation time units, where one unit is the mean service time. They are not seconds — the results are scale-free, so the comparison between policies holds regardless of how fast a real request would be.

## Requirements

- Python 3.10 or newer
- Dependencies are declared in `requirements.txt` (numpy at runtime) and install automatically in the step below.

## Clone and set up

```bash
git clone https://github.com/Chris-rb/loadbalancing-sim.git
cd loadbalancing-sim

python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate

pip install -r requirements.txt
```
Run the two halves in separate terminals.
 
**Backend** (FastAPI + WebSocket, served by uvicorn):
 
```bash
source .venv/bin/activate
uvicorn lbsim.api.lbsim_server:app --reload --port 8000
```
 
The API is now at `http://localhost:8000` and the replay WebSocket at
`ws://localhost:8000/ws/replay`. `--reload` restarts on code changes.
 
**Frontend** (Vite dev server with hot reload):
 
```bash
cd frontend
npm install                          # first time only
npm run dev
```
 
The dashboard is at `http://localhost:5173` and talks to the backend on 8000.

# Configuration & What to Expect
 
The simulator is configured through the **Simulator Configuration** panel (web
UI) or a JSON config file (CLI). Every field below maps to one setting.
 
## Configuration fields
 
| Field | Meaning | Notes |
|---|---|---|
| **Policy Type** | Dispatching algorithm | Round Robin, Least Connections, or Power of Two |
| **Number of Servers** | Servers in the cluster | e.g. 5 or 10 |
| **Max Queue Length** | Per-server queue capacity | Requests arriving at a full queue are dropped |
| **Server Load (max 1)** | Target offered load ρ | 0–1; higher = busier. Arrival rate is derived from this, not set directly |
| **Seed** | Random seed | Same seed = identical, reproducible run |
| **Number of Requests** | Requests to complete before stopping | The run ends after this many finish |
| **Warmup Requests** | Completions discarded before recording stats | Excludes the empty-system startup so numbers reflect steady state |
| **Enable Failures** | Turns the failure model on/off | Off by default |
| **MTBF** | Mean time between failures | Only shown/used when failures are enabled |
| **MTTR** | Mean time to repair | Only shown/used when failures are enabled |
 
Note on load: you set **Server Load (ρ)**, and the arrival rate follows from it
(`λ = ρ × servers × service rate`). Raising ρ toward 1 pushes the cluster toward
saturation.
 
## The three policies
 
- **Round Robin** — cycles through servers in order, ignoring how busy each is.
  The simple baseline.
- **Least Connections** — routes each request to the server with the shortest
  queue. The strongest of the three.
- **Power of Two** — samples two random servers and picks the shorter queue.
  Nearly matches Least Connections while checking far less state.
## What to expect from a run
 
**The dashboard** shows live metrics (mean/p95/p99 response time, throughput,
completed and dropped requests), a **server cluster** grid where each tile's
fill and color reflect its current queue depth (green = healthy, amber =
building, red = full or failed), and a **response-time chart** over simulated
time.
 
**Reading the results:**
 
- **Least Connections and Power of Two hold up well under load** — low mean
  response times and typically zero drops, even near ρ = 0.9.
- **Round Robin degrades at high load** — because it ignores queue state, some
  servers build long queues, inflating the p95/p99 tail and producing dropped
  requests where the other policies drop none.
- **Tail latency (p95/p99) rises sharply as ρ approaches 1.** Lowering the load
  noticeably shrinks the tail.
- **Drops appear when queues overflow** — most common under Round Robin at high
  load, or when failures remove capacity.
- **With failures enabled**, a server going down shifts its load onto the
  survivors; effective load on the remaining servers rises, and you may see a
  temporary spike in response times and additional drops until it recovers.
**Reproducibility:** a given (config, seed) pair always produces the same
result, so runs can be repeated and compared exactly.

## Output

Every run — whether launched from the web UI or the command line — generates a
**CSV report**, one file per run, saved to the `reports/` directory. Each row
corresponds to one completed request, with the summary metrics recomputed
cumulatively as the run progresses (so the final row reflects the whole run).
 
## Columns
 
| Column | Meaning |
|---|---|
| `completed_requests` | Running count of completed requests at this point |
| `dropped_requests` | Running count of dropped requests (queue full or lost to a failure) |
| `arrival_time` | Simulation clock time the request arrived |
| `completed_time` | Time spent in service for this request (its service duration) |
| `response_time` | Total time in system: waiting + service |
| `wait_time` | Time spent waiting in queue before service began |
| `throughput` | Completions per unit of simulated time, cumulative |
| `p50` | Median response time so far |
| `p95` | 95th-percentile response time so far |
| `p99` | 99th-percentile response time so far |
 
Notes:
 
- **Times are in simulation time units** (one unit ≈ one mean service time), not
  seconds. Results are scale-free.
- **Warm-up requests are excluded** — the first *N* completions (set by *Warmup
  Requests*) are discarded, so the earliest rows begin partway into the run and
  the statistics reflect steady state rather than the empty-system startup.
- `response_time = wait_time + completed_time` for each request.
- The percentile and throughput columns are **cumulative** — they update as more
  requests complete, so the last row gives the run's final p50/p95/p99 and
  throughput.
- The same `(config, seed)` always produces the same CSV, so runs are fully
  reproducible.
 