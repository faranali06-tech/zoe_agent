import json
from sqlalchemy import desc
from sqlalchemy.orm import Session
from .models import SocialConnection, SocialPlatform

def get_latest_boss_youtube_connection(db: Session) -> SocialConnection | None:
    return db.query(SocialConnection).filter(SocialConnection.user_id == "boss").filter(SocialConnection.platform == SocialPlatform.youtube).order_by(desc(SocialConnection.created_at)).first()

def social_connection_to_dict(conn: SocialConnection) -> dict:
    expires_at_unix = int(conn.expires_at.timestamp()) if conn.expires_at else None
    return {
        "access_token": conn.access_token,
        "refresh_token": conn.refresh_token,
        "expires_at": expires_at_unix,
        "scopes": json.loads(conn.scopes) if conn.scopes else None,
        "meta": json.loads(conn.meta) if conn.meta else None,
    }
