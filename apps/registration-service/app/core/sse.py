# app/core/sse.py
import asyncio
from typing import Dict

sse_clients: Dict[str, asyncio.Queue] = {}