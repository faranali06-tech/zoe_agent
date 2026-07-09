import os
import json
import urllib.parse
import time
import uuid
import datetime
import httpx
from fastapi import APIRouter, HTTPException
from sqlalchemy.orm import Session
from .db import SessionLocal
from .models import SocialConnection, SocialPlatform

router = APIRouter()
AUTH_URL = "https://google.com"
TOKEN_URL = "https://googleapis.com"
YOUTUBE_SCOPES = ["https://googleapis.com"]

@router.get("/oauth/youtube/start")
def youtube_oauth_start():
    client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
    public_base = os.getenv("PUBLIC_BASE_URL", "")
    if not client_id or not public_base:
        raise HTTPException(status_code=500, detail="Missing configuration keys")
    redirect_uri = f"{public_base}/oauth/youtube/callback"
    params = {
        "client_id": client_id,
        "redirect_uri": redirect_uri,
        "response_type": "code",
        "scope": " ".join(YOUTUBE_SCOPES),
        "access_type": "offline",
        "prompt": "consent",
        "include_granted_scopes": "true",
    }
    return {"authUrl": f"{AUTH_URL}?{urllib.parse.urlencode(params)}"}

@router.get("/oauth/youtube/callback")
async def youtube_oauth_callback(code: str):
    client_id = os.getenv("YOUTUBE_CLIENT_ID", "")
    client_secret = os.getenv("YOUTUBE_CLIENT_SECRET", "")
    public_base = os.getenv("PUBLIC_BASE_URL", "")
    if not client_id or not client_secret or not public_base:
        raise HTTPException(status_code=500, detail="Missing OAuth credentials")
    redirect_uri = f"{public_base}/oauth/youtube/callback"
    data = {
        "client_id": client_id,
        "client_secret": client_secret,
        "code": code,
        "grant_type": "authorization_code",
        "redirect_uri": redirect_uri,
    }
    async with httpx.AsyncClient(timeout=30) as client:
        r = await client.post(TOKEN_URL, data=data)
        r.raise_for_status()
        token = r.json()

    db: Session = SessionLocal()
    try:
        conn_id = f"conn_{uuid.uuid4().hex[:10]}"
        expires_in = int(token.get("expires_in", 3600))
        expires_at_unix = int(time.time()) + expires_in
        expires_at_dt = datetime.datetime.utcfromtimestamp(expires_at_unix)

        conn = SocialConnection(
            id=conn_id,
            user_id="boss",
            platform=SocialPlatform.youtube,
            access_token=token.get("access_token"),
            refresh_token=token.get("refresh_token"),
            expires_at=expires_at_dt,
            scopes=json.dumps(YOUTUBE_SCOPES),
            meta=json.dumps({"token_type": token.get("token_type")}),
        )
        db.add(conn)
        db.commit()
    finally:
        db.close()
    return {"ok": True, "connectionId": conn_id, "note": "OAuth complete."}
