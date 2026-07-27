import argparse
import json
from .core import SolutionInput, build_output

def main() -> None:
    p = argparse.ArgumentParser(description='ruvnet / ruflo Implementation')
    p.add_argument('--workflow-steps', type=float, required=True)
    p.add_argument('--integration-points', type=float, required=True)
    p.add_argument('--automation-window-hours', type=float, required=True)
    args = p.parse_args()
    inp = SolutionInput(args.workflow_steps, args.integration_points, args.automation_window_hours)
    print(json.dumps(build_output(inp), indent=2))

if __name__ == '__main__':
    main()
