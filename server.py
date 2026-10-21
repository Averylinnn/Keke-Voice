import os
import requests
import base64
from starlette.applications import Starlette
from starlette.routing import Route, Mount
from starlette.responses import JSONResponse

os.environ["MCP_ALLOWED_HOSTS"] = "*"

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("keke-voice")
API_KEY = os.environ.get("ELEVENLABS_API_KEY", "")
VOICE_ID = os.environ.get("ELEVENLABS_VOICE_ID", "RzwbtmqtU97ulT8Pclua")

@mcp.tool()
def speak(text: str) -> str:
    resp = requests.post(
        f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}",
        json={
            "text": text,
            "model_id": "eleven_multilingual_v2",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.75,
                "style": 0.3,
                "use_speaker_boost": True
            }
        },
        headers={
            "xi-api-key": API_KEY,
            "Content-Type": "application/json",
            "Accept": "audio/mpeg"
        },
        timeout=30
    )
    if resp.status_code != 200:
        return f"Error {resp.status_code}"
    audio_b64 = base64.b64encode(resp.content).decode()
    return f"data:audio/mpeg;base64,{audio_b64}"

_sse_app = mcp.sse_app()

from starlette.types import ASGIApp, Receive, Scope, Send

class HostFixMiddleware:
    def __init__(self, app: ASGIApp):
        self.app = app
    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] == "http":
            headers = list(scope.get("headers", []))
            scope["headers"] = [
                (b"host", b"localhost") if k == b"host" else (k, v)
                for k, v in headers
            ]
        await self.app(scope, receive, send)

app = HostFixMiddleware(_sse_app)
