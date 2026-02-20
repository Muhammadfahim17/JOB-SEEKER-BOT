from sqlalchemy import Column, Integer, String, BigInteger, DateTime, Boolean, Text, JSON
from database import Base
from datetime import datetime

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    tg_id = Column(BigInteger, unique=True, nullable=False)
    username = Column(String(100))
    
    # Анкета
    first_name = Column(String(100))
    last_name = Column(String(100))
    age = Column(Integer)
    desired_job = Column(String(200))
    skills = Column(Text)  # Навыки через запятую
    photo_file_id = Column(String(255))
    phone = Column(String(20))
    salary_expectation = Column(String(100))  # "договорная" или сумма
    resume = Column(JSON)  # {"type": "text/document/photo/video", "content": "..."}
    
    # Статус
    is_completed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class SupportMessage(Base):
    __tablename__ = "support_messages"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(BigInteger, nullable=False)  # Telegram ID
    user_tg_id = Column(BigInteger, nullable=False)  # Telegram ID
    user_name = Column(String(200))
    message = Column(Text)
    reply_to_admin = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)