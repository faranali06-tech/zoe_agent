import json
import uuid
import datetime
from .db import SessionLocal
from .models import Task, PublishJob, PublishStatus, ApprovalRequest, ApprovalStatus, SocialConnection
from .repo_connections import get_latest_boss_youtube_connection, social_connection_to_dict
from .publishers.youtube import publish_youtube

def _parse_json(s: str | None):
    if not s: return None
    try: return json.loads(s)
    except: return None

async def run_publish_youtube_in_background(task_id: str, publish_job_id: str) -> None:
    db = SessionLocal()
    try:
        job = db.get(PublishJob, publish_job_id)
        task = db.get(Task, task_id)
        if not job or not task: return

        approval = db.query(ApprovalRequest).filter(ApprovalRequest.task_id == task_id).order_by(ApprovalRequest.requested_at.desc()).first()
        if not approval or approval.status != ApprovalStatus.approved:
            job.status = PublishStatus.failed
            job.error = "Not approved (anything other than explicit YES is treated as NO)"
            db.commit()
            return

        render = _parse_json(task.render_output) or {}
        video_url = render.get("videoUrl")
        if not video_url:
            job.status = PublishStatus.failed
            job.error = "Missing render_output.videoUrl"
            db.commit()
            return

        conn = get_latest_boss_youtube_connection(db)
        if not conn:
            job.status = PublishStatus.failed
            job.error = "No YouTube OAuth connection found for user_id='boss'"
            db.commit()
            return

        job.status = PublishStatus.posting
        db.commit()

        script_obj = _parse_json(task.script_output) or {}
        caption = script_obj.get("scriptText") or f"Task {task_id}"
        hashtags = ["shorts"]

        conn_dict = social_connection_to_dict(conn)
        result = await publish_youtube(
            connection=conn_dict,
            video_url=video_url,
            caption=caption,
            hashtags=hashtags,
            privacy_status="unlisted",
        )

        job.status = PublishStatus.posted
        job.remote_id = result.get("videoId")
        job.remote_url = result.get("remoteUrl")
        job.response_payload = json.dumps(result.get("raw"))
        db.commit()

        updated = result.get("updatedConnection") or {}
        if updated.get("access_token"):
            conn.access_token = updated["access_token"]
        if updated.get("expires_at"):
            conn.expires_at = datetime.datetime.utcfromtimestamp(int(updated["expires_at"]))
        db.commit()

    except Exception as e:
        try:
            job = db.get(PublishJob, publish_job_id)
            if job:
                job.status = PublishStatus.failed
                job.error = str(e)
                db.commit()
        except: pass
    finally:
        db.close()
