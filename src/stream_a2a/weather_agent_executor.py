import os
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.events import EventQueue
from a2a.types import (
    TaskArtifactUpdateEvent,
    TaskState,
    TaskStatus,
    TaskStatusUpdateEvent,
)
from a2a.utils.artifact import new_text_artifact
from a2a.utils.message import new_agent_text_message
from a2a.utils.task import new_task

from openai import OpenAI,AsyncOpenAI

client = AsyncOpenAI(
    base_url='http://183.147.142.111:30000/v1',
    api_key= os.getenv('ANTHROPIC_API_KEY', 'sk-xxx')
)

class WeatherAgentExecutor(AgentExecutor):
    """你的专属 Agent 执行器"""

    async def execute(
        self,
        context: RequestContext,
        event_queue: EventQueue,
    ) -> None:
        """执行代理过程并将最终响应加入队列"""
        # 初始化 -> 干活 -> 发Artifact(结果) -> 发Status(完结)
        
        # 1. 初始化任务（如果是新任务的话）
        task = context.current_task or new_task(context.message)
        await event_queue.enqueue_event(task)

        # 2. 获取用户发来的文本
        query = ''
        if context.message and context.message.parts:
            query = context.message.parts[0].root.text

        # 3. 这里写你的业务逻辑（比如调用大模型、查数据库等）
        messages = [{"role": "user", "content": query}]
        resp = await client.chat.completions.create(
            messages=messages,
            model='qwen3.5-plus',
            stream=True,
            extra_body={"enable_thinking": False}
        )
        collected = ""
        async for chunk in resp:
            if not chunk.choices:
                continue
            delta = chunk.choices[0].delta.content
            if delta:
                collected += delta
                # 4. 将处理结果作为文本 artifact 推送出去
                await event_queue.enqueue_event(
                    TaskArtifactUpdateEvent(
                        task_id=task.id,
                        context_id=task.context_id,
                        artifact=new_text_artifact(name='chunk', text=delta),
                    )
                )

        # 5. 告诉框架，这个任务我已经干完了
        await event_queue.enqueue_event(
            TaskStatusUpdateEvent(
                task_id=task.id,
                context_id=task.context_id,
                status=TaskStatus(state=TaskState.completed),
                final=True
            )
        )

    async def cancel(
        self, context: RequestContext, event_queue: EventQueue
    ) -> None:
        """取消任务"""
        pass
