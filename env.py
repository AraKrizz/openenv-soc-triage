import random
from models import Observation, Action, Reward

class SOCTriageEnv:
    def __init__(self):
        self.tasks = [
            {"id": "soc-triage-easy", "target_ip": "192.168.1.50", "desc": "Block a known malicious IP"},
            {"id": "soc-triage-medium", "target_ip": "10.0.0.5", "desc": "Identify and block a brute-force attack"},
            {"id": "soc-triage-hard", "target_ip": "172.16.0.22", "desc": "Advanced Persistent Threat investigation"}
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
        step_c = self.state_data["step_count"]
        
        reward = 0.0 
        done = False
        info = {}

        # MEANINGFUL GRADER LOGIC: Faster resolution = higher score
        if action.command == "block_ip" and action.target == self.current_task['target_ip']:
            final_score = round(0.99 - (step_c * 0.02), 2)
            reward = final_score
            done = True
        elif action.command == "ignore_alert":
            final_score = 0.05
            reward = final_score
            done = True
        elif step_c >= 5:
            final_score = 0.10
            reward = final_score
            done = True

        # CRITICAL FIX: Pass the explicit score to the OpenEnv Grader
        if done:
            info["score"] = reward

        obs = Observation(
            logs=[f"Action '{action.command}' performed on '{action.target}'."],
            alert_status="Resolved" if done else "Investigating",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )
        
        return obs, reward, done, info

    def state(self):
        return self.state_data
