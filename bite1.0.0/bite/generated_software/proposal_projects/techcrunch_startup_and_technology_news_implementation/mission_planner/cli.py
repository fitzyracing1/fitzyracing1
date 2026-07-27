import argparse
import json
from .core import MissionInput, build_plan

def main() -> None:
    p = argparse.ArgumentParser(description='Aerospace Mission Planner')
    p.add_argument('--payload-mass-kg', type=float, required=True)
    p.add_argument('--orbit-altitude-km', type=float, required=True)
    p.add_argument('--launch-window-hours', type=float, required=True)
    args = p.parse_args()
    inp = MissionInput(args.payload_mass_kg, args.orbit_altitude_km, args.launch_window_hours)
    print(json.dumps(build_plan(inp), indent=2))

if __name__ == '__main__':
    main()
