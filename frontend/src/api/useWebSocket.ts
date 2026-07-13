import { useEffect, useRef, useState, useCallback } from "react";
import type { SimData, WebSocketMessage, LineChartMetrics, WebSocketResponse } from "./types";

interface Props {
    url: string
}

export const useWebSocket = ( { url }: Props ) => {
    const [simData, setSimData] = useState<SimData | null>(null);
    const [isConnected, setIsConnected] = useState<boolean>(false);
    const [metricsFrames, setMetricsFrames] = useState<LineChartMetrics[]>([]);
    const ws = useRef<WebSocket | null>(null);

    useEffect(() => {
        const socket = new WebSocket(url);
        ws.current = socket;

        socket.onopen = () => {
            setIsConnected(true);
            console.log("WebSocket connection opened");
        }

        socket.onmessage = (msg: MessageEvent) => {
            try {
                const data: WebSocketResponse = JSON.parse(msg.data);

                switch (data.resp) {
                    case "SIM_DATA":
                            if (data && data.sim_data){
                                setSimData(data.sim_data);

                                const newMetricFrames: LineChartMetrics = {
                                    t: data.sim_data.t,
                                    mean: data.sim_data.metrics.p50,
                                    p95: data.sim_data.metrics.p95,
                                    p99: data.sim_data.metrics.p99
                                }
                                setMetricsFrames((prevFrames) => [...prevFrames, newMetricFrames]);
                            }
                        break;

                    case "REPORT_PATH":
                        console.log(`Report generated to ${data.path}`);
                        break;
                            
                    default:
                        throw Error("Unexpected response received");
                }
            }
            catch (error) {
                console.error("An error occured attemping to parse WebSocket message: ", error)
            }
        }

        socket.onclose = () => {
            setIsConnected(false);
            console.log("WebSocket connection closed");
        }

        return () => {
            socket.close();
        };
    }, [url]);

    const sendRunConfig = useCallback((webSocketMessage: WebSocketMessage) => {
        console.log(`Meesage sent: ${JSON.stringify(webSocketMessage)}`)
        if (ws.current && ws.current.readyState == WebSocket.OPEN) {
            ws.current.send(JSON.stringify(webSocketMessage));
            console.log(`Meesage sent: ${webSocketMessage}`)
        }
        console.log(`${ws.current}`)
        console.log(`${ws.current.readyState}`)
    }, []);

    return { simData, isConnected, metricsFrames, sendRunConfig }
}