import os
import asyncio
import json
import re
from openai import OpenAI
from env import SOCTriageEnv
from models import Action

# 1. Grab the environment variables injected by the Hackathon Judges
api_key = os.getenv("API_KEY", "dummy-key-for-validator")
base_url = os.getenv("API_BASE_URL", "https://api.huggingface.co/models/")
model_name = os.getenv("MODEL_NAME", "Qwen/Qwen2.5-72B-Instruct")

# 2. Initialize the client using those variables
client = OpenAI(
    base_url=base_url,
    api_key=api_key,
)

SYSTEM_PROMPT = """You are a Junior SOC Analyst.
You will receive a JSON state detailing the network environment.
You must respond with a strictly valid JSON object containing:
- "command": The tool to execute (analyze_log, block_ip, ignore_alert).
- "target": The specific IP address to act upon.
Example: {"command": "block_ip", "target": "192.168.1.50"}
Respond ONLY with JSON. Do not include markdown formatting or explanations."""

async def run_inference():
    env = SOCTriageEnv()
    obs = env.reset()
    
    # Notice we are using the lowercase model_name here
    print(f"[START] task=soc-threat-block env=soc-triage model={model_name}")

    total_reward = 0.0
    steps = 0
    rewards_list = []

    for i in range(1, 6):
        prompt = f"You are a SOC Agent. Find the malicious IP in the logs and immediately use the 'block_ip' command on it.\nObs: {obs.model_dump_json()}\nRespond ONLY with a JSON object: {{'command': '...', 'target': '...'}}"
        
        # Notice we are using the lowercase model_name here too
        response = client.chat.completions.create(
            model=model_name,
            messages=[{"role": "user", "content": prompt}],
            response_format={ "type": "json_object" }
        )
        
        raw_content = response.choices[0].message.content
        
        # BULLETPROOF FILTER: Find anything between { and }
        match = re.search(r'\{.*\}', raw_content, re.DOTALL)
        if match:
            clean_json = match.group(0)
        else:
            # Fallback if the AI completely breaks
            clean_json = '{"command": "ignore_alert", "target": ""}'

        try:
            res_data = json.loads(clean_json)
        except json.JSONDecodeError:
            res_data = {'command': 'ignore_alert', 'target': ''}
            
        action = Action(command=res_data.get('command', 'ignore_alert'), target=res_data.get('target', ''))
        
        obs, reward, done, _ = env.step(action)
        steps += 1
        total_reward += reward
        rewards_list.append(f"{reward:.2f}")

        print(f"[STEP] step={steps} action={action.command} reward={reward:.2f} done={str(done).lower()} error=null")
        if done: break

    success = "true" if total_reward >= 1.0 else "false"
    print(f"[END] success={success} steps={steps} rewards={','.join(rewards_list)}")

if __name__ == "__main__":
    asyncio.run(run_inference())
