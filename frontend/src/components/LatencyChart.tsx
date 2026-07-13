import { 
    LineChart, 
    Line,
    XAxis,
    YAxis,
    CartesianGrid, 
    Tooltip,
    Legend, 
    ResponsiveContainer
} from "recharts";
import type { LineChartMetrics } from "../api/types";

interface Props {
    metricsFrames: LineChartMetrics[]
}

const LatencyChart = ({ metricsFrames }: Props) => {

    return (
        <ResponsiveContainer width="100%" height={255}>
            <LineChart data={metricsFrames ? metricsFrames : []} margin={{top: 8, right: 26, bottom: 8, left: 0}}>
                <CartesianGrid stroke="rgba(136,135,128,0.15)" vertical={false} />
                <XAxis 
                    dataKey="t"
                    tick={{ fontSize: 13, fill: "#888781"}}
                    label={{ value: "Simulated time", position: "insideBottom", offset:-4, fontSize: 16}}
                />
                <YAxis tick={{ fontSize: 12, fill: "#888781" }} label={{ value: "Response time", angle: -90 }}/>
                <Tooltip
                    contentStyle={{ fontSize: 13, borderRadius: 8}} 
                    labelFormatter={(t) => `t = ${t}`}
                />
                <Legend wrapperStyle={{ fontSize: 13}}/>
                <Line type="monotone" dataKey="mean" stroke="#1D9E75" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="p95"  stroke="#378ADD" strokeWidth={2} dot={false} isAnimationActive={false} />
                <Line type="monotone" dataKey="p99" stroke="#BA7517" strokeWidth={2} dot={false} isAnimationActive={false}/>
            </LineChart>
        </ResponsiveContainer>
    )
}

export default LatencyChart;