import os
import httpx

VAPI_BASE_URL = "https://vapi.ai"

async def create_approval_call(*, task_id: str, video_url: str) -> str:
    token = os.getenv("VAPI_PRIVATE_API_KEY", "")
    phone_number_id = os.getenv("VAPI_PHONE_NUMBER_ID_TWILIO", "")
    assistant_id = os.getenv("VAPI_ASSISTANT_ID_ZOE", "")
    boss_number = os.getenv("BOSS_PHONE_NUMBER_E164", "+966551846135")

    if not token or not phone_number_id or not assistant_id or not boss_number:
        raise RuntimeError("Missing Vapi environment configuration keys")

    payload = {
        "assistantId": assistant_id,
        "phoneNumberId": phone_number_id,
        "customer": {"number": boss_number},
        "assistantOverrides": {
            "variableValues": {"taskId": task_id, "videoUrl": video_url},
            "firstMessage": "Yes Boss, your video is ready. Should I upload it?"
        }
    }
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(f"{VAPI_BASE_URL}/call", json=payload, headers=headers)
        r.raise_for_status()
        data = r.json()
    return data["id"]
