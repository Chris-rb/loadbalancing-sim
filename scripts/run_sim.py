import os
import sys
import traceback

from lbsim.config import Config
from lbsim.simulator import Simulator

root_dir = os.path.abspath(os.path.join(os.path.dirname(__file__)))
sys.path.append(root_dir)

def main(args: list[str]) -> int:
    config_path = os.path.join(os.getcwd(), "configs", args[1])
    try: 
        cfg = Config.from_json(config_path)
        sim = Simulator(cfg)
        stats = sim.run()
        stats.write_csv()
        stats.summary()
        
    except Exception as e:
        print(f"[run_sim] Unexpected error occured: {e}")
        traceback.print_exc()
    
if __name__ == "__main__":
    main(sys.argv)