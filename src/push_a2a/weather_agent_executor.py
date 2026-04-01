import asyncio
import json
import time
import httpx
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils.artifact import new_text_artifact
from a2a.utils.task import new_task

class WeatherAgentExecutor(AgentExecutor):

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)

        query = ""
        if context.message and context.message.parts:
            query = context.message.parts[0].root.text

        # ========== 模拟长耗时任务 ==========
        steps = [
            "🔍 正在解析您的请求...",
            "☁️ 正在连接气象卫星数据...",
            "📊 正在分析历史天气趋势...",
            "🧮 正在生成天气预测模型...",
            "📝 正在整理最终报告...",
        ]

        for i, step in enumerate(steps):
            # 模拟每步耗时 1 秒
            await asyncio.sleep(1)

            # 每完成一步，推送一个进度更新
            await event_queue.enqueue_event(
                TaskArtifactUpdateEvent(
                    task_id=task.id,
                    context_id=task.context_id,
                    artifact=new_text_artifact(name='progress', text=f"{step}\n"),
                )
            )
            print(f"[{time.strftime('%H:%M:%S')}] 步骤 {i+1}/5 完成")

        # ========== 最终结果 ==========
        final_report = f"""
{'='*40}
📍 {query}

🌡️ 温度：26°C
💧 湿度：45%
🌬️ 风力：东南风 3级
☀️ 天气：晴转多云

任务总耗时：{len(steps) * 3} 秒
{'='*40}
"""
        await event_queue.enqueue_event(
            TaskArtifactUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                artifact=new_text_artifact(name='result', text=final_report),
            )
        )

        # ========== 推送通知（任务完成了，通知客户端） ==========
        webhook_url = context.configuration.push_notification_config.url
        async with httpx.AsyncClient() as http_client:
            await http_client.post(
                webhook_url,
                json={
                    "task_id": task.id,
                    "status": "completed",
                    "message": f"任务 {task.id} 已完成 ✅",
                },
            )
        print(f"[{time.strftime('%H:%M:%S')}] 📬 已向 {webhook_url} 发送推送通知")

        # ========== 标记任务完成 ==========
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                status=TaskStatus(state=TaskState.completed),
                final=True,
            )
        )

    async def cancel(self, context, event_queue):
        pass
