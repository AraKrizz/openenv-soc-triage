import random
from models import Observation, Action

class SOCTriageEnv:
    def __init__(self):
        self.tasks = [
            {"id": "soc-triage-easy", "target_ip": "192.168.1.50", "desc": "Block IP"},
            {"id": "soc-triage-medium", "target_ip": "10.0.0.5", "desc": "Block IP"},
            {"id": "soc-triage-hard", "target_ip": "172.16.0.22", "desc": "Block IP"}
        ]
        self.current_task = self.tasks[0]
        self.state_data = {"step_count": 0}

    def reset(self) -> Observation:
        self.state_data = {"step_count": 0}
        self.current_task = random.choice(self.tasks)
        
        return Observation(
            logs=[f"SEC-ALERT: High traffic detected from {self.current_task['target_ip']}"],
            alert_status="Unresolved",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )

    def step(self, action: Action):
        self.state_data["step_count"] += 1
        step_c = self.state_data["step_count"]
        
        reward = 0.01 
        done = False
        info = {}

        if action.command == "block_ip" and action.target == self.current_task['target_ip']:
            reward = 0.90 
            done = True
        elif action.command == "ignore_alert":
            reward = 0.10
            done = True
        elif step_c >= 5:
            reward = 0.10
            done = True

        if done:
            info["score"] = reward

        obs = Observation(
            logs=[f"Action '{action.command}' performed."],
            alert_status="Resolved" if done else "Investigating",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )
        
        return obs, reward, done, info

    def state(self):
        return self.state_data
