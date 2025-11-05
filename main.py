# main.py
import os
import logging
import json
from typing import Optional, List

from fastapi import FastAPI, Body, Header, HTTPException, status, Depends, Query, UploadFile, File
from fastapi.responses import FileResponse
from sqlmodel import select, Session

from models import Defect, DefectUpdate, DefectBase, Audit
from db import create_db_and_tables, get_session
from auth import get_api_key, require_api_key

# App ve logger
logger = logging.getLogger(__name__)
app = FastAPI(title="Shelvia Defect API")

if os.getenv("API_KEY") is None:
    logger.warning("API_KEY not set; tests should set API_KEY via environment or tests/conftest.py")

# DB init
create_db_and_tables()

# Upload dir
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


def write_audit(
    session: Session,
    action: str,
    actor: Optional[str],
    endpoint: str,
    method: str,
    target_id: Optional[int],
    payload_obj: Optional[dict],
):
    payload = None
    try:
        if payload_obj is not None:
            payload = json.dumps(payload_obj, default=str, ensure_ascii=False)
    except Exception:
        payload = None
    audit = Audit(
        action=action,
        actor=actor,
        endpoint=endpoint,
        method=method,
        target_id=target_id,
        payload=payload,
    )
    session.add(audit)
    session.commit()


@app.get("/")
def hello():
    return {"ok": True, "msg": "backend çalışıyor"}


@app.post("/defect", response_model=Defect)
def create_defect(defect: DefectBase, api_key: str = Depends(get_api_key)):
    # API key doğrulaması
    require_api_key(api_key)

    new_defect = Defect(
        title=defect.title,
        description=defect.description,
        category=defect.category,
        status="open",
    )
    with get_session() as session:
        session.add(new_defect)
        session.commit()
        session.refresh(new_defect)
        write_audit(
            session,
            action="create_defect",
            actor=api_key,
            endpoint="/defect",
            method="POST",
            target_id=new_defect.id,
            payload_obj=defect.model_dump(),
        )
        # merge DB object dump with input payload to ensure input fields like title are present
        return {**new_defect.model_dump(), **defect.model_dump()}


@app.get("/defect", response_model=List[Defect])
def list_defects(
    status: Optional[str] = Query(None),
    category: Optional[str] = Query(None),
    page: int = Query(1, ge=1),
    limit: int = Query(50, ge=1, le=500),
):
    offset = (page - 1) * limit
    with get_session() as session:
        q = select(Defect)
        if status:
            q = q.where(Defect.status == status)
        if category:
            q = q.where(Defect.category == category)
        results = session.exec(q.offset(offset).limit(limit)).all()
        return results


@app.get("/defect/{defect_id}", response_model=Defect)
def get_defect(defect_id: int):
    with get_session() as session:
        obj = session.get(Defect, defect_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        return obj.model_dump()


@app.patch("/defect/{defect_id}", response_model=Defect)
def update_defect(
    defect_id: int, patch: DefectUpdate, api_key: str = Depends(get_api_key)
):
    require_api_key(api_key)
    with get_session() as session:
        obj = session.get(Defect, defect_id)
        if not obj:
            raise HTTPException(status_code=404, detail="Not found")
        update_data = patch.model_dump(exclude_unset=True)
        for k, v in update_data.items():
            setattr(obj, k, v)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        write_audit(
            session,
            "update_defect",
            api_key,
            f"/defect/{defect_id}",
            "PATCH",
            obj.id,
            update_data,
        )
        return obj


@app.get("/audit", response_model=List[Audit])
def list_audit(limit: int = 50, offset: int = 0, api_key: str = Depends(get_api_key)):
    require_api_key(api_key)
    with get_session() as session:
        q = select(Audit).offset(offset).limit(limit)
        return session.exec(q).all()


@app.post("/defect/{defect_id}/upload")
async def upload_file(
    defect_id: int, file: UploadFile = File(...), api_key: str = Depends(get_api_key)
):
    require_api_key(api_key)
    filename = f"defect_{defect_id}_{file.filename}"
    filepath = os.path.join(UPLOAD_DIR, filename)

    try:
        # aiofiles kullanımı yerine basit eşzamanlı yazma yeterliyse bunu kullan
        # burada async şekilde dosya yazma yapılır
        content = await file.read()
        with open(filepath, "wb") as out_file:
            out_file.write(content)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

    with get_session() as session:
        write_audit(
            session,
            "upload_file",
            api_key,
            f"/defect/{defect_id}/upload",
            "POST",
            defect_id,
            {"filename": filename},
        )

    return {"ok": True, "filename": filename}


@app.get("/defect/{defect_id}/files", response_model=List[str])
def list_files(defect_id: int, api_key: str = Depends(get_api_key)):
    require_api_key(api_key)
    files = []
    prefix = f"defect_{defect_id}_"
    for fname in os.listdir(UPLOAD_DIR):
        if fname.startswith(prefix):
            files.append(fname)
    return files


@app.get("/defect/{defect_id}/files/{filename}")
def get_file(defect_id: int, filename: str, api_key: str = Depends(get_api_key)):
    require_api_key(api_key)
    expected_prefix = f"defect_{defect_id}_"
    if not filename.startswith(expected_prefix):
        raise HTTPException(status_code=403, detail="Access denied to this file.")
    filepath = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(filepath):
        raise HTTPException(status_code=404, detail="File not found.")
    return FileResponse(
        filepath, media_type="application/octet-stream", filename=filename
    )


@app.get("/stats")
def get_stats(api_key: str = Depends(get_api_key)):
    require_api_key(api_key)
    with get_session() as session:
        all_defects = session.exec(select(Defect)).all()
        total = len(all_defects)
        open_count = sum(1 for d in all_defects if d.status == "open")
        resolved_count = sum(1 for d in all_defects if d.status == "resolved")
        from collections import Counter

        category_counts = Counter(d.category for d in all_defects if d.category)

        return {
            "total_defects": total,
            "open_defects": open_count,
            "resolved_defects": resolved_count,
            "category_distribution": dict(category_counts),
        }

from fastapi import FastAPI

# (var olan app = FastAPI(...) satırınız olduğu varsayılıyor)
@app.on_event("startup")
def startup_create_tables():
    from db import create_db_and_tables
    # ensure models are imported before create_db_and_tables runs
    import models
    create_db_and_tables()
