from sqlalchemy import Column, Integer, String, DateTime, Text
from sqlalchemy.sql import func
from db.postgres import Base

class UploadedFile(Base):
    __tablename__ = "uploaded_files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    file_type = Column(String, nullable=False)
    row_count = Column(Integer, nullable=True)
    columns = Column(Text, nullable=True)
    uploaded_at = Column(DateTime(timezone=True), server_default=func.now())