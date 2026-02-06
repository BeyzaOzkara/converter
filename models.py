from sqlalchemy import (
    Column,
    String,
    JSON,
    LargeBinary,
    Integer,
    TIMESTAMP,
    ForeignKey,
    func,
)
from .database import Base


class Device(Base):
    __tablename__ = "devices"

    device_id = Column(String, primary_key=True, index=True)
    camera_settings = Column(JSON, nullable=False, default=dict)
    command = Column(String, nullable=False, default="none")
    last_seen = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )


class Capture(Base):
    __tablename__ = "captures"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String, ForeignKey("devices.device_id"), index=True)
    timestamp = Column(
        TIMESTAMP(timezone=True),
        server_default=func.now(),
    )
    image = Column(LargeBinary, nullable=False)
    size = Column(Integer)
