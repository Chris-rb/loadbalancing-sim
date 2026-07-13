import { useState, useEffect } from "react";
import { useWebSocket } from "./api/useWebSocket";
import { Box, Button, Typography, Slider, Stack } from "@mui/material";
import type { Config, WebSocketMessage } from "./api/types";
import ConfigModal from "./components/ConfigModal";
import LatencyChart from "./components/LatencyChart";
import './SimDashboard.css';


const SimDashboard = () => {
    const [runConfig, setRunConfig] = useState<Config | null>(null);
    const [speed, setSpeed] = useState<number>(10);
    const [openConfigModal, setOpenConfigModal] = useState<boolean>(false);
    

    const { simData, isConnected, metricsFrames, sendRunConfig } = useWebSocket({ url: "ws://localhost:8000/ws/sim_stream" });

    const handleStartSim = () => {
        const webSocketMessage: WebSocketMessage = {
            message: "SIM_CONFIG",
            sim_config: runConfig
        }
        sendRunConfig(webSocketMessage)
    }

    const handleSetSpeed = async (newValue: number) => {
        setSpeed(newValue);
    }

    const setSimSpeed= async (_, newValue: number)  => {
        await handleSetSpeed(newValue);
        const webSocketMessage: WebSocketMessage = {
            message: "SIM_SPEED",
            sim_speed: speed
        }
        sendRunConfig(webSocketMessage)
    } 

    const toggleConfigModal = () => {
        setOpenConfigModal(!openConfigModal);
    }

    const ServerTile = ({ id, state, qlen, K = 15 }) => {
        const failed = state === "FAILED";
        const ratio = failed ? 1 : qlen / K;
        const color = failed ? "#E24B4A"       
                    : ratio > 0.66 ? "#E24B4A"    
                    : ratio > 0.25 ? "#EF9F27"   
                    : "#1D9E75";                

        return (
            <div style={{
                position: "relative", overflow: "hidden", borderBlockColor: "rgba(128, 128, 128, 0.159)",
                border: "0.5px solid var(--border)", borderRadius: 8,
                padding: 10, textAlign: "center", minHeight: 90, minWidth: 175
            }}>
                <div style={{
                    position: "absolute", left: 0, bottom: 0, width: "100%",
                    height: `${Math.max(6, ratio * 100)}%`,
                    background: color, opacity: 0.18,
                    transition: "height 0.2s ease",
                }} />
                <div style={{ position: "relative" }}>
                    <Typography style={{ fontSize: 16}}>
                        Server {id}
                    </Typography>
                    <div style={{ 
                        fontSize: 20, fontWeight: 500, fontFamily: "var(--font-mono)",
                        color: failed ? "#A32D2D" : "#ffffff" 
                    }}>
                        {failed ? "FAILED" : `q=${qlen}`}
                    </div>
                </div>
            </div>
        );
        }

    const serverClusters = () => {
        if (simData == null) {
            return <Typography style={{ display: "flex", justifySelf: "center" }}>No server cluster data to display</Typography>
        }

        const serverClusters = simData.servers.map((server, idx) => {
            return (
                <ServerTile 
                    key={idx} 
                    id={server.server_id + 1} 
                    state={server.server_state} 
                    qlen={server.queue_size}
                    K={runConfig.k}
                />
            )
        });

        return serverClusters;
    }

    const metricsDisplays = () => {

        return (
            <div className="metrics-container">
                <Box className="metrics-box-col">
                    <Typography className="inner-box-title">mean completion t</Typography>
                    <Typography 
                        className="metrics" 
                        variant="h4"
                        sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}
                    >
                        {simData ? simData.metrics.completed_time.toFixed(3) : 0.0}
                    </Typography>
                </Box>
                <Box className="metrics-box-col">
                    <Typography className="inner-box-title">mean wait t</Typography>
                    <Typography 
                        className="metrics" 
                        variant="h4"
                        sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}
                    >
                        {simData ? simData.metrics.wait_time.toFixed(3) : 0}
                    </Typography>
                </Box>
                <Box className="metrics-box-col">
                    <Typography className="inner-box-title">completed requests</Typography>
                    <Typography 
                        className="metrics" 
                        variant="h4"
                        sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}
                    >
                        {simData ? simData.metrics.completed_requests : 0}
                    </Typography>
                </Box>
                <Box className="metrics-box-col">
                    <Typography className="inner-box-title">dropped requests</Typography>
                    <Typography 
                        className="metrics" 
                        variant="h4"
                        sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}
                    >
                        {simData ? simData.metrics.dropped_requests : 0}
                    </Typography>
                </Box>
                <Box className="metrics-box-col">
                    <Typography className="inner-box-title">throughput</Typography>
                    <Typography 
                        className="metrics" 
                        variant="h4"
                        sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}
                    >
                        {simData ? simData.metrics.throughput.toFixed(3) : 0.}
                    </Typography>
                </Box>
                <Box className="metrics-box-col">
                    <Typography className="inner-box-title">mean response t</Typography>
                    <Typography 
                        className="metrics" 
                        variant="h4"
                        sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}
                    >
                        {simData ? simData.metrics.p50.toFixed(3) : 0.0}
                    </Typography>
                </Box>
                <Box className="metrics-box-col">
                    <Typography className="inner-box-title">p95th response t</Typography>
                    <Typography 
                        className="metrics" 
                        variant="h4"
                        sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}
                    >
                        {simData ? simData.metrics.p95.toFixed(3) : 0.0}
                    </Typography>
                </Box>
                <Box className="metrics-box-col">
                    <Typography className="inner-box-title">p99th response t</Typography>
                    <Typography 
                        className="metrics" 
                        variant="h4"
                        sx={{ fontVariantNumeric: 'tabular-nums', fontWeight: 600 }}
                    >
                        {simData ? simData.metrics.p99.toFixed(3) : 0.0}
                    </Typography>
                </Box>
            </div>
        )
    }

    useEffect(() => {
        console.log(isConnected ? "Websocket connected" : "Websocket not connected")
    }, [isConnected]);

    return (
        <div>
            <div className="sim-config-container">
                <Typography className="sim-title" variant="h4">Load Balancer Simulator</Typography>
                <div className="sim-details-labels">
                    <Typography className="policy-title">{runConfig != null ? runConfig.policy : "No Policy Selected"}</Typography>
                    <Typography style={{ display: "flex"}}>
                        Server time: 
                            <span style={{ color: "white", whiteSpace: "pre-wrap"}}>
                                {simData ? ` ${simData.t}` : " n/a"}
                            </span>
                    </Typography>
                </div>
                <div className="sim-control-panel">
                    <div className="speed-slider">
                        <Stack spacing={2} direction={"row"} sx={{ alignItems: "center"}}>
                            <Typography id="slider">
                            Speed
                            </Typography>
                            <Slider 
                                id="speed-slider"
                                size="small"
                                min={1}
                                max={20}
                                step={1}
                                value={speed}
                                onChange={setSimSpeed}
                                valueLabelDisplay="auto"
                            />
                            <Typography>
                            {speed}x
                            </Typography>
                        </Stack>
                    </div>
                    <div className="sim-config-controls">
                        <Button
                            onClick={() => handleStartSim()}
                            disabled={runConfig == null}
                        >
                            Play
                        </Button>
                        <Button
                            onClick={toggleConfigModal}
                        >
                            Config
                        </Button>
                        <ConfigModal
                            open={openConfigModal} 
                            handleClose={toggleConfigModal}
                            setRunConfig={setRunConfig}
                        />
                    </div>
                </div>
            </div>
            <div className="metrics-label">
                <Typography variant="h6">Metrics</Typography>
            </div>
            <div className="metrics-container-outer">
                {metricsDisplays()}
            </div>
            <div className="server-cluster-label">
                <Typography variant="h6">Server Cluster</Typography>
            </div>
            <div className="server-cluster-container">
                {serverClusters()}
            </div>
            <div className="response-times-charts">
                <div className="line-chart-label">
                    <Typography variant="h6">Response time over simulated time</Typography>
                </div>
                <LatencyChart metricsFrames={metricsFrames} />
            </div>
        </div>        
    )
}

export default SimDashboard;