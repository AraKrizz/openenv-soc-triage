from models import Observation, Action

class SOCTriageEnv:
    def __init__(self, task_id="soc-triage-easy"):
        # Explicitly map the IDs to their respective target IPs
        self.tasks = {
            "soc-triage-easy": "192.168.1.50",
            "soc-triage-medium": "10.0.0.5",
            "soc-triage-hard": "172.16.0.22"
        }
        # Safely get the target IP based on the requested task_id
        self.target_ip = self.tasks.get(task_id, "192.168.1.50")
        self.state_data = {"step_count": 0}

    def reset(self) -> Observation:
        self.state_data = {"step_count": 0}
        
        return Observation(
            logs=[f"SEC-ALERT: High traffic detected from {self.target_ip}"],
            alert_status="Unresolved",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )

    def step(self, action: Action):
        self.state_data["step_count"] += 1
        step_c = self.state_data["step_count"]
        
        reward = 0.01 
        done = False
        info = {}

        if action.command == "block_ip" and action.target == self.target_ip:
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

        
