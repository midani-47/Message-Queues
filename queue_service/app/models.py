from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union
from datetime import datetime
from enum import Enum


class QueueRole(str, Enum):
    """Roles for queue access control"""
    ADMIN = "admin"
    AGENT = "agent"
    USER = "user"


class MessageBase(BaseModel):
    """Base model for queue messages
    
    This model is generic to store any kind of message content
    that follows the transaction or result format from Assignment 2
    """
    content: Dict[str, Any]  # Content can be any valid JSON object
    timestamp: datetime = Field(default_factory=datetime.utcnow)


class Message(MessageBase):
    """Message model with unique ID"""
    id: str  # Unique message ID


class QueueConfig(BaseModel):
    """Queue configuration model"""
    max_messages: int = 1000
    persist_interval_seconds: int = 60


class QueueInfo(BaseModel):
    """Queue information model"""
    name: str
    message_count: int
    created_at: datetime
    last_modified: datetime = Field(default_factory=datetime.utcnow)


class QueueCreate(BaseModel):
    """Model for queue creation"""
    name: str
    config: Optional[QueueConfig] = None


class QueueList(BaseModel):
    """Model for listing queues"""
    queues: List[QueueInfo]


class ErrorResponse(BaseModel):
    """Standard error response model"""
    detail: str


class TokenData(BaseModel):
    """Model for token data"""
    username: str
    role: QueueRole
