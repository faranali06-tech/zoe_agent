import json
import uuid
import datetime
from typing import Any, Dict
from sqlalchemy.orm import Session
from sqlalchemy.sql import func

from .db import SessionLocal
from .models import Task, TaskStatus, ApprovalRequest, ApprovalStatus
from .pipeline.research import run_research
from .pipeline.script_gen import generate_script
from .pipeline.render import mock_render
from .vapi_outbound import create_approval_call

def create_task_row(db: Session, args: dict) -> str:
    task_id = f"task_{uuid.uuid4().hex[:10]}"
    task_type = args.get("taskType", "trend_research")
    topic = args.get("topic", "")
    platforms = args.get("platforms", []) or []
    language = args.get("language", "en") or "en"
    timezone = args.get("timezone", "UTC") or "UTC"
    schedule_at = args.get("scheduleAt")

    task = Task(
        id=task_id,
        task_type=task_type,
        topic=topic,
        platforms=json.dumps(platforms),
        language=language,
        timezone=timezone,
        schedule_at=schedule_at,
        status=TaskStatus.queued,
    )
    db.add(task)
    db.commit()
    return task_id

async def handle_create_scheduled_task_queued(db: Session, args: dict) -> Dict[str, Any]:
    task_id = create_task_row(db, args)
    return {
        "taskId": task_id,
        "status": "queued",
        "topic": args.get("topic", ""),
        "taskType": args.get("taskType", "trend_research"),
    }

async def run_pipeline_in_background(task_id: str, args: dict) -> None:
    db = SessionLocal()
    try:
        task = db.get(Task, task_id)
        if not task:
            return

        try:
            task.status = TaskStatus.running
            db.commit()

            topic = task.topic
            platforms = json.loads(task.platforms or "[]")

            # Stage 1: Research
            research = await run_research(topic, platforms)
            task.research_output = json.dumps(research)

            # Stage 2: Script gen
            max_words = 45
            constraints = args.get("constraints") or {}
            if isinstance(constraints, dict) and isinstance(constraints.get("maxWords"), int):
                max_words = constraints["maxWords"]

            script = await generate_script(topic, research, max_words=max_words)
            task.script_output = json.dumps(script)

            # Stage 3: Render (mock for MVP)
            render = await mock_render(script["scriptText"])
            task.render_output = json.dumps(render)

            task.status = TaskStatus.done
            db.commit()

            # --- Sprint 4: Create approval request + trigger outbound call ---
            render_obj = json.loads(task.render_output or "{}")
            video_url = render_obj.get("videoUrl")

            approval_id = f"apr_{uuid.uuid4().hex[:10]}"
            approval = ApprovalRequest(
                id=approval_id,
                task_id=task.id,
                status=ApprovalStatus.pending,
                video_url=video_url,
            )
            db.add(approval)
            db.commit()

            try:
                call_id = await create_approval_call(task_id=task.id, video_url=video_url or "")
                approval.call_id = call_id
                db.commit()
            except Exception as ce:
                approval.status = ApprovalStatus.failed
                approval.decision = f"Call trigger failed: {str(ce)}"
                db.commit()

        except Exception as e:
            task.status = TaskStatus.failed
            task.error = str(e)
            db.commit()

    finally:
        db.close()
