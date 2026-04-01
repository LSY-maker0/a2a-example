"""
最简单的 A2A Agent 后端示例
"""
from a2a.server.request_handlers import DefaultRequestHandler
from a2a.server.apps import A2AStarletteApplication
from a2a.server.events import EventQueue
from a2a.server.agent_execution import AgentExecutor, RequestContext
from a2a.server.tasks import InMemoryTaskStore
from a2a.types import AgentCard, AgentSkill
from a2a.types import (
    AgentCapabilities,
    AgentCard,
    AgentInterface,
    AgentSkill,
)
import uvicorn

from src.push_a2a.weather_agent_executor import WeatherAgentExecutor

def run_push_agent():
    # 1. 声明技能
    skill = AgentSkill(
        id='check_weather', 
        name='查询天气', 
        description='根据用户提供的城市名称，查询该城市的实时天气情况', 
        tags=['天气', '查天气', '气温'], 
        # examples=['北京今天天气怎么样？', '帮我查一下上海的天气', '广州冷不冷']
    )

    # 2. 定义能力（你的硬件配置，全用默认的就行）
    capabilities = AgentCapabilities(streaming=True,pushNotifications=True)

    # 3. Agent 卡片信息
    agent_card = AgentCard(
        name='天气助手', 
        version='1.0.0',
        description='一个能够根据城市名称查询实时天气的智能代理',
        capabilities=capabilities,
        preferred_transport='JSONRPC', # default='JSONRPC', examples=['JSONRPC', 'GRPC', 'HTTP+JSON']
        url='http://localhost:8000',
        defaultInputModes=["text"],      # 必需字段
        defaultOutputModes=["text"],
        skills=[skill],
    )

    # 4. 创建执行器和事件队列
    executor = WeatherAgentExecutor()
    request_handler = DefaultRequestHandler(agent_executor=executor,task_store=InMemoryTaskStore())

    # 5. 创建应用
    app = A2AStarletteApplication(agent_card=agent_card, http_handler=request_handler)

    # 6. 启动应用
    print("🚀 A2A Agent 启动在 http://localhost:8000")
    uvicorn.run(app.build(), host="0.0.0.0", port=8000)

if __name__ == "__main__":
    run_push_agent()