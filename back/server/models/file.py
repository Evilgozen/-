from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class FileUploadSchema(BaseModel):
    """文件上传模型"""
    filename: str
    content_type: str
    size: int
    
class FileInfoSchema(BaseModel):
    """文件信息模型"""
    id: str
    filename: str
    content_type: str
    size: int
    upload_time: datetime
    file_path: str
    
class FileResponseModel(BaseModel):
    """文件响应模型"""
    error: bool = False
    code: int = 200
    message: str
    data: Optional[dict] = None