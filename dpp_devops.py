# Save this file exactly as: dpp_devops.py
import re
import sys
import os
import subprocess
from typing import Dict, Any

class DPlusPlusGitHubActionsEngine:
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.registry: Dict[str, Dict[str, str]] = {}
        self.rule: Dict[str, Any] = {}

    def compile(self) -> bool:
        try:
            with open(self.filepath, "r") as f:
                dpp_code = f.read()
        except FileNotFoundError:
            print(f"❌ Error: D++ file '{self.filepath}' could not be found.")
            return False

        print(f"🧬 [D++ CLOUD ENGINE] Parsing repository policy: '{self.filepath}'...")

        # Parse resource allocations
        for line in dpp_code.splitlines():
            line = line.strip()
            if not line or line.startswith("//") or line.startswith("#"): continue
            res_match = re.match(r"RESOURCE\s+(\w+)\s+([a-zA-Z0-9_]+)\s+(IDENTIFIED\s+BY|LOCATED\s+AT)\s+[\"\']?(.+?)[\"\']?$", line)
            if res_match:
                res_type, res_name, _, res_addr = res_match.groups()
                self.registry[res_name] = {"type": res_type, "address": res_addr.strip('"\'')}

        # Parse grammar logic rules
        rule_pattern = (
            r"WHEN\s+([a-zA-Z0-9_\.]+)\s+(IS GREATER THAN|IS LESS THAN|IS EQUAL TO)\s+(\d+)\s+FOR\s+(\d+)\s+seconds\s+"
            r"TRIGGER\s+([a-zA-Z0-9_]+)\s+([a-zA-Z0-9_\s]+)"
        )
        match = re.search(rule_pattern, dpp_code)
        if not match:
            print("❌ D++ Compilation Error: Invalid structural grammar logic.")
            return False

        self.rule = {
            "metric": match.group(1), "op": match.group(2), "thresh": int(match.group(3)),
            "device": match.group(5), "action": match.group(6).strip(),
            "val_min": None, "val_max": None
        }

        val_match = re.search(r"VALIDATE\s+([a-zA-Z0-9_\.]+)\s+BETWEEN\s+(\d+)\s+AND\s+(\d+)", dpp_code)
        if val_match:
            self.rule["val_min"] = int(val_match.group(2))
            self.rule["val_max"] = int(val_match.group(3))

        print(f"   ✔ Cloud policy compiled for target resource gate: '{self.rule['device']}'\n")
        return True

    def run_real_pipeline(self, current_pass_rate: float):
        """Processes real build telemetry inside the live GitHub Actions virtual server"""
        print(f"--- D++ PRODUCTION POLICY MONITOR ACTIVE ---")
        print(f"Analyzing incoming pipeline metric '{self.rule['metric']}': {current_pass_rate}%")

        # Evaluate validation parameters
        if self.rule["val_min"] is not None and self.rule["val_max"] is not None:
            if not (self.rule["val_min"] <= current_pass_rate <= self.rule["val_max"]):
                print(f"   🚨 [POLICY BREACH] Telemetry report is invalid or out-of-bounds ({current_pass_rate}%).")
                print("   📊 CI/CD Gateway Decision: [HALT] Aborting workflow to protect infrastructure integrity.")
                sys.exit(1) # Terminates GitHub Action runner with a failure code!

        # Evaluate trigger constraints
        breached = False
        if self.rule["op"] == "IS LESS THAN" and current_pass_rate < self.rule["thresh"]:
            breached = True

        if breached:
            print(f"   🚨 Critical threshold violation detected against security rules!")
            target_res = self.registry.get(self.rule["device"], {"address": "echo 'Halt'"})
            print(f"   🚀 [D++ AUTOMATED POLICY ENFORCED] -> Executing: '{target_res['address']}'")
            
            # Fire real pipeline system-level command
            subprocess.run(target_res["address"], shell=True)
            
            print("   📊 CI/CD Gateway Decision: [FAILED] Deployment blocked.")
            sys.exit(1) # Tell GitHub Actions the run failed
        else:
            print("   ✅ [PIPELINE VERIFIED] All clear. Code validation checks passed successfully.")
            print("   📊 CI/CD Gateway Decision: [SUCCESS] Proceeding to production deployment.")
            sys.exit(0) # Tell GitHub Actions the run passed cleanly

if __name__ == "__main__":
    # Expects parameters: python dpp_devops.py [filename.dpp] [actual_metric_value]
    script_file = sys.argv[1] if len(sys.argv) > 1 else "cicd_pipeline.dpp"
    live_metric = float(sys.argv[2]) if len(sys.argv) > 2 else 100.0

    engine = DPlusPlusGitHubActionsEngine(script_file)
    if engine.compile():
        engine.run_real_pipeline(live_metric)
