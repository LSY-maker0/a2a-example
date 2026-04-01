import asyncio
from src.sync_a2a.client import run_sync_client
from src.stream_a2a.client import run_stream_client
from src.push_a2a.client import run_push_client

if __name__ == "__main__":
    # asyncio.run(run_sync_client())
    # asyncio.run(run_stream_client())
    asyncio.run(run_push_client())
