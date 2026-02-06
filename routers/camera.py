from fastapi import APIRouter, UploadFile, File, Depends, HTTPException
from fastapi.responses import Response
from sqlalchemy.orm import Session

from ..database import SessionLocal
from .. import crud
from ..schemas import CameraSettings, CommandRequest, CommandResponse, UploadResponse

router = APIRouter(prefix="/camera", tags=["camera"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# ------------------------------
# GET SETTINGS (ESP + UI)
# ------------------------------
@router.get("/settings/{device_id}")
def get_settings(device_id: str, db: Session = Depends(get_db)):
    dev = crud.create_or_get_device(db, device_id)
    return {
        "device_id": dev.device_id,
        "settings": dev.camera_settings,
        "command": dev.command,
    }


# ------------------------------
# UPDATE SETTINGS (UI → server)
# ------------------------------
@router.post("/settings/{device_id}")
def update_settings(
    device_id: str, payload: CameraSettings, db: Session = Depends(get_db)
):
    crud.update_settings(db, device_id, payload.settings)
    return {"ok": True}


# ------------------------------
# UI → trigger command
# ------------------------------
@router.post("/command/{device_id}")
def set_command(
    device_id: str, payload: CommandRequest, db: Session = Depends(get_db)
):
    # Şimdilik sadece basit doğrulama
    if payload.cmd not in ["none", "capture"]:
        raise HTTPException(status_code=400, detail="Unsupported command")

    crud.set_command(db, device_id, payload.cmd)
    return {"ok": True}


# ------------------------------
# ESP32 → poll command
# ------------------------------
@router.get("/command/{device_id}", response_model=CommandResponse)
def get_command(device_id: str, db: Session = Depends(get_db)):
    cmd = crud.pop_command(db, device_id)
    return CommandResponse(cmd=cmd)


# ------------------------------
# ESP32 upload image
# ------------------------------
@router.post("/upload/{device_id}", response_model=UploadResponse)
async def upload(
    device_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    if file.content_type not in ("image/jpeg", "image/jpg"):
        raise HTTPException(status_code=400, detail="Only JPEG supported")

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Empty file")

    crud.save_capture(db, device_id, data)
    return UploadResponse(ok=True)


# ------------------------------
# UI → show latest jpg
# ------------------------------
@router.get("/latest/{device_id}")
def latest(device_id: str, db: Session = Depends(get_db)):
    cap = crud.get_latest_capture(db, device_id)
    if not cap:
        raise HTTPException(status_code=404, detail="No capture yet")

    return Response(cap.image, media_type="image/jpeg")
