import os
import sys
import traceback

from src.lbsim.config import Config
from src.lbsim.simulator import Simulator

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(root_dir)

def main(args: list[str]) -> int:
    config_path = os.path.join(os.getcwd(), "configs", args[1])
    try: 
        cfg = Config.from_json(config_path)
        sim = Simulator(cfg)
        stats = sim.run()
        stats.write_csv()
        return 0
    except Exception as e:
        print(f"[run_sim] Unexpected error occured: {e}")
        traceback.print_exc()
    
if __name__ == "__main__":
    raise SystemExit(main(sys.argv))