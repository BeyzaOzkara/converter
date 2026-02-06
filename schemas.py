from pydantic import BaseModel
from typing import Dict, Any


class CameraSettings(BaseModel):
    settings: Dict[str, Any]


class CommandRequest(BaseModel):
    cmd: str


class CommandResponse(BaseModel):
    cmd: str


class UploadResponse(BaseModel):
    ok: bool
