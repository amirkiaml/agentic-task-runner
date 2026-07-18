from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from datetime import datetime, timezone
from agents import Runner
from agent import agent
from utils import build_trace, extract_tools_used
from storage import save_task, list_tasks
from storage import save_task, list_tasks, clear_all_tasks


app = FastAPI()


class AgentRequest(BaseModel):
    user_input: str


@app.get("/")
async def home():
    return FileResponse("static/index.html")

@app.post("/run")
async def run_agent(request: AgentRequest):
    try:
        result = await Runner.run(agent, request.user_input)
    except Exception as e:
        return {"error": f"Agent run failed: {e}"}

    trace = build_trace(request.user_input, result)
    tools_used = extract_tools_used(result)
    timestamp = datetime.now(timezone.utc).isoformat()

    task_id = save_task(request.user_input, result.final_output, tools_used, trace)

    return {"id": task_id, "response": result.final_output, "tools_used": tools_used, "trace": trace, "timestamp": timestamp}

@app.get("/history")
async def get_history():
    return list_tasks()


app.mount("/static", StaticFiles(directory="static"), name="static")

@app.delete("/history")
async def delete_history():
    clear_all_tasks()
    return {"status": "cleared"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)