import asyncio
import json
from pydantic import BaseModel, ConfigDict, ValidationError
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from enum import Enum

from .schema import WebSocketMessage, MessageType
from lbsim.config import Config
from  lbsim.simulator import Simulator


class ResponseType(Enum):
    SIM_DATA = "SIM_DATA"
    REPORT_PATH = "REPORT_PATH"

class WebsockectResp(BaseModel):
    model_config = ConfigDict(use_enum_values=True)
    
    resp: ResponseType
    sim_data: object = None
    path: str = None


app = FastAPI()

@app.websocket("/ws/sim_stream")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    state = {
        "sim_config": None,
        "delay": 1,
        "base_step": 0.5,
        "speed_scale": 1
    }
    
    start_sim = asyncio.Event()

    async def sim_speed_listener():
        while True:
            try:
                raw_data = await websocket.receive_json()
                json_data = WebSocketMessage(**raw_data).model_dump(exclude_unset=True)

                if json_data.get("message") == MessageType.SIM_SPEED.value:
                    state["speed_scale"] = json_data.get("sim_speed", state["speed_scale"] )
                    current_speed = max(1, min(20, state["speed_scale"]))
                    state["delay"] = state["base_step"] / current_speed
    
                
                elif json_data.get("message") == MessageType.SIM_CONFIG.value:
                    state["sim_config"] = Config(**json_data.get("sim_config"))
                    start_sim.set()
                    
                
            except ValidationError as e:
                print(f"Validation error: {e}")
            except WebSocketDisconnect:
                print("Read task caught client disconnect.")
                raise
                
                
    async def run_lb_sim():
        while True:
            await start_sim.wait()
            start_sim.clear()
                
            sim_config = state["sim_config"]
            if sim_config is None:
                print("Skipping execution: SIM_CONFIG has not been sent yet.")
                continue
                
            lb_sim = Simulator(config=sim_config)
            
            try:
                async for sim_data in lb_sim.run_steam():
                    if sim_data.get("metrics", {}).get("completed_requests") <= 0:
                        continue
                    
                    sim_data_resp = WebsockectResp(
                        resp = ResponseType.SIM_DATA.value,
                        sim_data = sim_data,
                    )
                    await asyncio.sleep(state["delay"])
                    await websocket.send_json(sim_data_resp.model_dump())
                    print(f"message sent: {sim_data}")
                    
                print("generating sim report")
                report_path = lb_sim.stats.write_csv()
                
                report_resp = WebsockectResp(
                    resp = ResponseType.REPORT_PATH.value,
                    path = report_path
                )
                await websocket.send_json(report_resp.model_dump())

            except ValidationError as e:
                print(f"Validation error: {e}")
        
    try:
        await asyncio.gather(
            sim_speed_listener(),
            run_lb_sim()
        )   
        
    except WebSocketDisconnect:
        print("Client disconnected normally")
    except Exception as e:
        print(f"Unexpected connection error: {e.with_traceback()}")