# 🛡️ CyberGuard SOC Triage Simulation

## Description & Motivation
CyberGuard is a real-world OpenEnv simulation designed to test an AI agent's ability to act as a Junior Security Operations Center (SOC) Analyst. 

While many RL environments focus on games or simple web navigation, there is a massive gap in evaluating AI for cybersecurity operations. This environment simulates a network defense scenario where an agent must parse system security logs, identify malicious IP addresses, and execute the correct containment commands.

## 📊 Observation and Action Spaces

### Observation Space
The agent receives a dynamic JSON state detailing the current network environment:
* `logs` (List[str]): Real-time security alerts and system logs.
* `alert_status` (str): Tracks the progress of the investigation ("Unresolved", "Investigating", "Resolved").
* `available_tools` (List[str]): Commands the agent is authorized to use.

### Action Space
The agent must respond with a strict JSON object:
* `command` (str): The tool to execute (`analyze_log`, `block_ip`, `ignore_alert`).
* `target` (str): The specific IP address to act upon.

## 🎯 Task Difficulty Progression
The environment randomly initializes one of three tasks via the `reset()` function:
1. **Easy:** Block a known malicious IP (192.168.1.50) from a standard log alert.
2. **Medium:** Identify and block a brute-force attack originating from 10.0.0.5.
3. **Hard:** Investigate and contain an Advanced Persistent Threat (APT) from 172.16.0.22.

## 🏆 Reward Function
Rewards are strictly deterministic (0.0 to 1.0) to ensure accurate baseline grading:
* **1.0 (Success):** Agent correctly identifies the threat IP and issues the `block_ip` command.
* **0.0 (Failure):** Agent ignores the alert, blocks the wrong IP, or hallucinates an invalid command.

## ⚙️ Setup and Usage Instructions

**1. Install Dependencies**
```bash
pip install openenv-core pydantic openai

2. Set API Key

Bash
export HF_TOKEN="your_huggingface_read_token"
3. Run Inference Baseline

Bash
python inference.py
