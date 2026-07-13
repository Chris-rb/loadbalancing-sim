export type ServerState = "IDLE" | "BUSY" | "FAILED";
export type MessageType = "SIM_SPEED" | "SIM_CONFIG";
export type ResponseType = "SIM_DATA" | "REPORT_PATH";

export const PolicyTypeArray = ["Round Robin", "Least Connections", "Power of Two"] as const;

export type PolicyTypes = typeof PolicyTypeArray[number];

export interface ServerData {
    server_id: number,
    queue_size: number,
    server_state: ServerState
};

export interface Metrics {
    completed_requests: number,
    dropped_requests: number,
    arrival_time: number,
    completed_time: number,
    response_time: number,
    wait_time: number,
    throughput: number,
    p50: number,
    p95: number,
    p99: number,
}

export interface LineChartMetrics {
    t: number,
    mean: number,
    p95: number,
    p99: number,
}

export interface SimData {
    t: number,
    servers: ServerData[],
    metrics: Metrics
};

export interface Config {
    policy: PolicyTypes,
    c: number,
    k: number,
    rho: number,
    seed: number,
    max_requests: number,
    warmup: number,
    failures_enabled: boolean,
    MTBF: number,
    MTTR: number
}

export interface WebSocketMessage {
    message: MessageType
    sim_config?: Config
    sim_speed?: number
}



export interface WebSocketResponse {
    resp: ResponseType
    sim_data?: SimData
    path?: string
}

