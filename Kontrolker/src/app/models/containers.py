# src/app/models/container.py
from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.session import Base

class Container(Base):
    __tablename__ = "containers"

    id = Column(Integer, primary_key=True, index=True)       # id lógico de tu API
    docker_id = Column(String(128), unique=True, index=True) # id real de Docker
    name = Column(String(255), index=True)
    image = Column(String(255), nullable=False)

    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True, index=True)
    service_id = Column(Integer, ForeignKey("services.id"), nullable=True, index=True)

    status = Column(String(64), nullable=False, default="created")

    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    deleted_at = Column(DateTime, nullable=True)

    project = relationship("Project", backref="containers")
    service = relationship("Service", backref="containers")
