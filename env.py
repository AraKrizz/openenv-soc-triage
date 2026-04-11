import random
from models import Observation, Action

class SOCTriageEnv:
    def __init__(self, task_id="easy"):
        self.task_id = task_id
        self.tasks = {
            "easy": "192.168.1.50",
            "medium": "10.0.0.5",
            "hard": "172.16.0.22"
        }
        self.target_ip = self.tasks.get(task_id, "192.168.1.50")
        self.state_data = {"step_count": 0}

    def _generate_realistic_logs(self):
        """Generates realistic SOC noise based on difficulty to test the AI's reasoning."""
        # EASY TASK: Clear alert, minimal noise
        if self.task_id == "easy":
            return [
                "[INFO] 08:00:01 - 192.168.1.10: Successful login for user 'admin'",
                "[INFO] 08:00:05 - 10.0.0.2: ICMP Echo Request received",
                f"[CRITICAL] 08:01:12 - IDS ALERT: SQL Injection payload detected from {self.target_ip}",
                "[INFO] 08:01:15 - 192.168.1.10: Session terminated"
            ]
        # MEDIUM TASK: Brute force hidden among normal failed logins
        elif self.task_id == "medium":
            logs = ["[INFO] Normal network baseline established."]
            for i in range(1, 4):
                logs.append(f"[WARN] 10.0.0.{i+10}: Failed login attempt (Invalid Password)")
            for _ in range(5):
                logs.append(f"[ERROR] {self.target_ip}: Failed SSH login attempt user 'root'")
            logs.append("[WARN] 10.0.0.15: Failed login attempt (Invalid Password)")
            return logs
        # HARD TASK: Advanced Persistent Threat. No explicit alerts.
        else: 
            return [
                "[INFO] 192.168.1.100 - GET /index.html 200 OK",
                f"[INFO] {self.target_ip} - GET /api/v1/health 200 OK",
                "[INFO] 192.168.1.101 - POST /login 401 Unauthorized",
                f"[INFO] {self.target_ip} - POST /upload?file=reverse_shell.php 201 Created",
                f"[WARN] {self.target_ip} - Executing bash command: 'cat /etc/shadow'",
                "[INFO] 192.168.1.100 - GET /dashboard 200 OK"
            ]

    def reset(self) -> Observation:
        self.state_data = {"step_count": 0}
        noisy_logs = self._generate_realistic_logs()
        
        return Observation(
            logs=noisy_logs,
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
        
        # Crash Armor: Prevents Phase 2 validator failures
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
            # Safe dynamic math to avoid 1.0 total sum
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
            logs=[f"Action '{action_command}' processed."],
            alert_status="Resolved" if done else "Investigating",
            available_tools=["analyze_log", "block_ip", "ignore_alert"]
        )
        
        return obs, float(reward), bool(done), info

    def state(self):
        return self.state_data
