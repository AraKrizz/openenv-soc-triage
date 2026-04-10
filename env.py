import random
from models import Observation, Action, Reward

class SOCTriageEnv:
    def __init__(self):
        self.tasks = [
            {"id": "easy", "target_ip": "192.168.1.50", "desc": "Block a known malicious IP"},
            {"id": "medium", "target_ip": "10.0.0.5", "desc": "Identify and block a brute-force attack"},
            {"id": "hard", "target_ip": "172.16.0.22", "desc": "Advanced Persistent Threat investigation"}
        ]
        self.current_task = self.tasks[0]
        self.state_data = {"step_count": 0, "threat_blocked": False}

    def reset(self) -> Observation:
        self.state_data = {"step_count": 0, "threat_blocked": False}
        self.current_task = random.choice(self.tasks)
        
        return Observation(
            logs=[f"SEC-ALERT: High traffic detected from {self.current_task['target_ip']}"],
            alert_status="Unresolved",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )

    def step(self, action: Action):
        self.state_data["step_count"] += 1
        
        # Default reward is now strictly within the 0 to 1 boundary
        reward = 0.01 
        done = False

        if action.command == "block_ip" and action.target == self.current_task['target_ip']:
            reward = 0.99
            done = True
        elif action.command == "ignore_alert":
            reward = 0.01
            done = True
        elif self.state_data["step_count"] >= 5:
            # Force stop after 5 steps so it doesn't run forever
            reward = 0.01
            done = True

        obs = Observation(
            logs=[f"Action {action.command} performed."],
            alert_status="Resolved" if done else "Investigating",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )
        return obs, reward, done, {}

    def state(self):
        return self.state_data
