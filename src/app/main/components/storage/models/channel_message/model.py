from datetime import datetime

from sqlalchemy import Column, Integer, String, DateTime, JSON, ForeignKey

from src.app.bases.db import BaseModel
from src.app.main.components.auth.models.user import UserModel


class StorageChannelMessageModel(BaseModel):
    __tablename__ = 'storage_channel_messages'
    __pk_field__ = "id"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey(UserModel.id), nullable=False)
    intent = Column(String(50), nullable=False)
    sender_name = Column(String(50), index=True, nullable=False)
    target_name = Column(String(50), index=True, nullable=False)
    channel_name = Column(String(50), index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now, nullable=False)
    data = Column(JSON, nullable=False)
