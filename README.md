---
title: SOC Triage Environment
emoji: 🛡️
colorFrom: blue
colorTo: red
sdk: docker
app_port: 7860
---

# CyberGuard: OpenEnv SOC Triage Simulation

CyberGuard is a high-fidelity Reinforcement Learning environment built for the Meta PyTorch OpenEnv Hackathon. It evaluates an AI agent's ability to act as a Tier-2 Security Operations Center (SOC) Analyst by parsing noisy network logs, identifying malicious behavior, and executing targeted defensive commands.

## Observation Space (The "Cyber Range")
Unlike standard environments that spoon-feed alerts to the agent, CyberGuard forces the LLM to reason through realistic network noise. The observation state is returned as a JSON object containing `logs`, `alert_status`, and `available_tools`.

The environment features three distinct threat scenarios:
* **Easy (SQLi Alert):** The agent must identify a clear IDS alert buried in standard network traffic and extract the attacking IP.
* **Medium (Distributed Brute Force):** The agent must identify a coordinated SSH brute-force attack hidden amongst a sea of benign, accidental failed logins from normal users.
* **Hard (Advanced Persistent Threat):** There are no IDS alerts. The agent must analyze standard web traffic logs and identify an APT executing anomalous bash commands (e.g., `cat /etc/shadow`, `reverse_shell.php`) and block the actor.

## Action Space
The agent interacts with the environment by outputting a strictly formatted JSON object dictating its tool use.
* `command`: The specific tool to execute (`analyze_log`, `block_ip`, or `ignore_alert`).
* `target`: The specific IPv4 address to act upon.
* *Example Action:* `{"command": "block_ip", "target": "192.168.1.50"}`

## Meaningful Grader Logic
CyberGuard implements dynamic, class-based evaluation logic (`server/grader.py`). 
The agent is not graded on a simple Pass/Fail binary. The environment penalizes hesitation (Reward Degradation).
* Agents that swiftly identify the threat and issue the `block_ip` command receive a high reward.
* For every unnecessary step the agent takes (or if it issues the `ignore_alert` command), the final episode score is dynamically mathematically penalized.
* **Validation Safe:** The scoring architecture is aggressively clamped and heavily typed to survive strict parameterless reflection tests and ensure scores remain strictly bounded `(0, 1)`.

## Architecture
* `env.py`: Generates the dynamic state observations and noisy logs based on the current `task_id`. Handles step-based score degradation.
* `server/grader.py`: Class-based, framework-compliant graders (`EasyGrader`, `MediumGrader`, `HardGrader`) that safely evaluate the agent's trajectory.
* `inference.py`: Houses the system prompt directing the Qwen 72B model to act as a Tier 2 SOC Analyst, parsing the noisy JSON state and outputting strict tool-calling JSON.

## Setup and Execution Instructions
To run this environment locally and test the inference agent:

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/AraKrizz/openenv-soc-triage.git](https://github.com/AraKrizz/openenv-soc-triage.git)
   cd openenv-soc-triage
2. **Set your Hugging Face Token:**
   export HF_TOKEN="your_huggingface_token_here"
3. **Run the AI Agent Inference:**
   python inference.py
4. **(Optional) Run OpenEnv Cloud Validation Locally::**
   openenv validate
