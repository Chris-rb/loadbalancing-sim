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


## Run a simulation

Point the runner at a config file:

```bash
python -m scripts.run_experiment configs/lc_config.json
```

This runs the simulation, prints a one-line summary, and writes a per-request CSV to `results/`. Two configs are provided — identical except for the policy — so you can compare them at the same load:

```bash
python -m scripts.run_experiment configs/rr_config.json
python -m scripts.run_experiment configs/lc_config.json
```

At the same load, Least Connections should report a lower mean response time than Round Robin. That is the system working as intended: routing to the shortest queue beats routing blindly.

## Configuration

Each experiment is one JSON file in `configs/`. The arrival rate is not set directly — you set the target load `rho` and the arrival rate is derived from it.

| key            | meaning                                        |
|----------------|------------------------------------------------|
| `policy`       | `Round Robin` or `Least Connections`           |
| `c`            | number of servers                              |
| `K`            | per-server queue capacity                      |
| `rho`          | target offered load, between 0 and 1           |
| `seed`         | random seed (makes a run reproducible)         |
| `max_requests` | stop after this many requests complete         |
| `warmup`       | completions discarded before recording stats   |
| `service_rate` | mean service rate; leave at 1.0                |

To run your own scenario, copy a config, change the values, and point the runner at it. A higher `rho` (closer to 1) makes the cluster busier and the differences between policies sharper.

## Output

The per-request CSV in `results/` has one row per completed request:

| column          | meaning                                        |
|-----------------|------------------------------------------------|
| `t_arrive`      | clock time the request entered the system      |
| `t_done`        | clock time its service completed               |
| `response_time` | `t_done − t_arrive`; total time in the system  |

`response_time` is the headline metric; `t_arrive` and `t_done` are timestamps on the virtual clock (they start partway into the run because the warm-up period is discarded). All values are in simulation time units.
