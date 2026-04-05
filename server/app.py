from fastapi import FastAPI
import uvicorn
from env import SOCTriageEnv
from models import Action

app = FastAPI()
my_env = SOCTriageEnv()

@app.get("/")
def ping():
    return {"status": "OK", "message": "CyberGuard SOC Triage is running"}

@app.post("/reset")
def reset_env():
    return my_env.reset()

@app.post("/step")
def step_env(action: Action):
    obs, reward, done, info = my_env.step(action)
    return {"observation": obs, "reward": reward, "done": done, "info": info}

@app.get("/state")
def state_env():
    return my_env.state()

def main():
    # Use "server.app:app" because the file is inside the 'server' folder
    uvicorn.run("server.app:app", host="0.0.0.0", port=7860)

if __name__ == "__main__":
    main()
