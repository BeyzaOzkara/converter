from sqlalchemy.orm import Session
from sqlalchemy import func
from .models import Device, Capture


def get_device(db: Session, device_id: str) -> Device | None:
    return db.query(Device).filter(Device.device_id == device_id).first()


def create_or_get_device(db: Session, device_id: str) -> Device:
    dev = get_device(db, device_id)
    if dev is None:
        dev = Device(device_id=device_id, camera_settings={}, command="none")
        db.add(dev)
        db.commit()
        db.refresh(dev)
    return dev


def update_settings(db: Session, device_id: str, settings: dict) -> Device:
    dev = create_or_get_device(db, device_id)
    dev.camera_settings = settings
    dev.last_seen = func.now()
    db.commit()
    db.refresh(dev)
    return dev


def set_command(db: Session, device_id: str, command: str) -> Device:
    dev = create_or_get_device(db, device_id)
    dev.command = command
    dev.last_seen = func.now()
    db.commit()
    db.refresh(dev)
    return dev


def pop_command(db: Session, device_id: str) -> str:
    dev = create_or_get_device(db, device_id)
    cmd = dev.command or "none"
    dev.command = "none"
    dev.last_seen = func.now()
    db.commit()
    return cmd


def save_capture(db: Session, device_id: str, data: bytes) -> Capture:
    dev = create_or_get_device(db, device_id)  # cihaz kaydı yoksa bile oluştur
    cap = Capture(device_id=dev.device_id, image=data, size=len(data))
    db.add(cap)
    db.commit()
    db.refresh(cap)
    return cap


def get_latest_capture(db: Session, device_id: str) -> Capture | None:
    return (
        db.query(Capture)
        .filter(Capture.device_id == device_id)
        .order_by(Capture.timestamp.desc())
        .first()
    )
