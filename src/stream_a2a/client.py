"""
测试 A2A Agent
"""
import httpx
import asyncio
import json
from uuid import uuid4

from a2a.client import A2ACardResolver
from a2a.client.client import ClientConfig
from a2a.client.client_factory import ClientFactory
from a2a.types import (
    TaskArtifactUpdateEvent,
    Message,
    Part,
    Role,
)
from a2a.utils.constants import AGENT_CARD_WELL_KNOWN_PATH

async def run_stream_client():
    base_url = "http://localhost:8000"
    # 打通一个电话线路，不用的时候自动断开，httpx相当于requests的升级版，支持异步
    async with httpx.AsyncClient() as httpx_client:
        # 初始化 A2ACardResolver，用来接收和解析 Agent Card（名片）
        resolver = A2ACardResolver(
            httpx_client=httpx_client,
            base_url=base_url,
        )

        _public_card = (await resolver.get_agent_card()) 
        # print(f'_public_card: {json.dumps(_public_card.dict(), indent=2, ensure_ascii=False)}') # 名片信息
        
        # 封装好的客户端，用于发请求
        client_factory = ClientFactory(config=ClientConfig(streaming=True))
        client = client_factory.create(_public_card)

        # 组建消息
        parts = [Part(text='我要查看北京的天气')]
        message = Message(
            role=Role.user,
            parts=parts,
            message_id=uuid4().hex,
        )
        # request = SendMessageRequest(id=uuid4().hex, params=MessageSendParams(message=message))

        # 发送消息，接收响应
        response = client.send_message(message)
        full_text = ""

        async for task, update in response:
            if isinstance(update, TaskArtifactUpdateEvent) and update.artifact:
                for part in update.artifact.parts:
                    full_text += part.root.text
                    print(part.root.text, end="", flush=True)

if __name__ == "__main__":
    asyncio.run(run_stream_client())