import os
import asyncio
import json
import re
from openai import OpenAI
from env import SOCTriageEnv
from models import Action

# 1. Capture the Hackathon Proxy Environment Variables
api_key = os.getenv("API_KEY", "dummy-key-for-validator")
base_url = os.getenv("API_BASE_URL", "https://api.huggingface.co/models/")
model_name = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")

client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

# 2. Define the System Prompt
SYSTEM_PROMPT = """You are a Junior SOC Analyst.
You will receive a JSON state detailing the network environment.
You must respond with a strictly valid JSON object containing:
- "command": The tool to execute (analyze_log, block_ip, ignore_alert).
- "target": The specific IP address to act upon.
Example: {"command": "block_ip", "target": "192.168.1.50"}
Respond ONLY with JSON. Do not include markdown formatting or explanations."""

async def run_inference():
    # 3. Loop through exactly 3 tasks for the grader
    tasks = ["soc-triage-easy", "soc-triage-medium", "soc-triage-hard"]

    for current_task in tasks:
        env = SOCTriageEnv()
        obs = env.reset()
        
        print(f"[START] task={current_task} env=soc-triage model={model_name}")

        total_reward = 0.0
        steps = 0
        rewards_list = []

        for i in range(1, 6):
            prompt = f"Find the malicious IP in the logs and immediately use the 'block_ip' command on it.\nObs: {obs.model_dump_json()}"
            
            # 4. Send BOTH the System Prompt and User Prompt
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": prompt}
                ],
                response_format={ "type": "json_object" }
            )
            
            raw_content = response.choices[0].message.content
            
            # 5. Bulletproof JSON parsing
            match = re.search(r'\{.*\}', raw_content, re.DOTALL)
            if match:
                clean_json = match.group(0)
            else:
                clean_json = '{"command": "ignore_alert", "target": ""}'

            try:
                res_data = json.loads(clean_json)
            except json.JSONDecodeError:
                res_data = {'command': 'ignore_alert', 'target': ''}
                
            action = Action(command=res_data.get('command', 'ignore_alert'), target=res_data.get('target', ''))
            
            obs, reward, done, _ = env.step(action)
            
            # 6. Strict score clipping (Must be between 0 and 1)
            if reward >= 1.0:
                reward = 0.99
            elif reward <= 0.0:
                reward = 0.01

            steps += 1
            total_reward += reward
            rewards_list.append(f"{reward:.2f}")

            print(f"[STEP] step={steps} action={action.command} reward={reward:.2f} done={str(done).lower()} error=null")
            if done: break

        success = "true" if total_reward >= 0.99 else "false"
        print(f"[END] success={success} steps={steps} rewards={','.join(rewards_list)}")

if __name__ == "__main__":
    asyncio.run(run_inference())
