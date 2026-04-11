import random
from models import Observation, Action

class SOCTriageEnv:
    def __init__(self, task_id="easy"):
        self.tasks = {
            "easy": "192.168.1.50",
            "medium": "10.0.0.5",
            "hard": "172.16.0.22"
        }
        self.target_ip = self.tasks.get(task_id, "192.168.1.50")
        self.state_data = {"step_count": 0}

    def reset(self) -> Observation:
        self.state_data = {"step_count": 0}
        return Observation(
            logs=[f"SEC-ALERT: High traffic detected from {self.target_ip}"],
            alert_status="Unresolved",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )

    def step(self, action):
        self.state_data["step_count"] += 1
        step_c = self.state_data["step_count"]
        
        reward = 0.01 
        done = False
        info = {}

        action_command = "invalid"
        action_target = "invalid"
        
        try:
            if isinstance(action, dict):
                action_command = str(action.get("command", ""))
                action_target = str(action.get("target", ""))
            else:
                action_command = str(getattr(action, "command", ""))
                action_target = str(getattr(action, "target", ""))
        except Exception:
            pass 

        if action_command == "block_ip" and action_target == self.target_ip:
            # MATH FIX: Dynamically balance so the sum of the episode is ALWAYS 0.89
            reward = round(0.89 - ((step_c - 1) * 0.01), 2)
            done = True
        elif action_command == "ignore_alert":
            reward = 0.05
            done = True
        elif step_c >= 5:
            reward = 0.05
            done = True

        if done:
            info["score"] = float(reward)

        obs = Observation(
            logs=[f"Action processed."],
            alert_status="Resolved" if done else "Investigating",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )
        
        return obs, float(reward), bool(done), info

    def state(self):
        return self.state_data
