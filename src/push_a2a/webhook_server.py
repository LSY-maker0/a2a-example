# webhook_server.py
from fastapi import FastAPI, Request
import uvicorn

app = FastAPI()

@app.post("/webhook")
async def receive_notification(request: Request):
    """Agent 跑完任务后，会 POST 通知到这里"""
    body = await request.json()
    print("\n📬 收到推送通知：")
    print(body)
    # 实际项目中，这里可以去调 GetTask 拉取完整结果
    return {"status": "ok"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
