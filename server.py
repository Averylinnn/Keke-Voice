from mcp.server.fastmcp import FastMCP
import os, requests, base64

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

app = mcp.sse_app()
