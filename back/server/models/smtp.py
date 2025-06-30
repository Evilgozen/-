from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime

class SMTPConfigSchema(BaseModel):
    """SMTP服务器配置模型"""
    smtp_server: str = Field(..., description="SMTP服务器地址")
    smtp_port: int = Field(587, description="SMTP服务器端口")
    username: str = Field(..., description="发送邮箱用户名")
    password: str = Field(..., description="发送邮箱密码或授权码")
    use_tls: bool = Field(True, description="是否使用TLS加密")
    sender_name: str = Field(..., description="发送者显示名称")
    sender_email: EmailStr = Field(..., description="发送者邮箱地址")
    
    class Config:
        schema_extra = {
            "example": {
                "smtp_server": "smtp.gmail.com",
                "smtp_port": 587,
                "username": "your_email@gmail.com",
                "password": "your_app_password",
                "use_tls": True,
                "sender_name": "教师信息系统",
                "sender_email": "your_email@gmail.com"
            }
        }

class EmailSchema(BaseModel):
    """邮件发送模型"""
    to_emails: List[EmailStr] = Field(..., description="收件人邮箱列表")
    cc_emails: Optional[List[EmailStr]] = Field(None, description="抄送邮箱列表")
    bcc_emails: Optional[List[EmailStr]] = Field(None, description="密送邮箱列表")
    subject: str = Field(..., description="邮件主题")
    body: str = Field(..., description="邮件正文")
    is_html: bool = Field(False, description="是否为HTML格式")
    attachments: Optional[List[str]] = Field(None, description="附件文件路径列表")
    
    class Config:
        schema_extra = {
            "example": {
                "to_emails": ["recipient@example.com"],
                "cc_emails": ["cc@example.com"],
                "subject": "测试邮件",
                "body": "这是一封测试邮件",
                "is_html": False,
                "attachments": []
            }
        }

class EmailLogSchema(BaseModel):
    """邮件发送记录模型"""
    to_emails: List[str] = Field(..., description="收件人邮箱列表")
    cc_emails: Optional[List[str]] = Field(None, description="抄送邮箱列表")
    bcc_emails: Optional[List[str]] = Field(None, description="密送邮箱列表")
    subject: str = Field(..., description="邮件主题")
    body: str = Field(..., description="邮件正文")
    sender_email: str = Field(..., description="发送者邮箱")
    send_time: datetime = Field(..., description="发送时间")
    status: str = Field(..., description="发送状态：success/failed")
    error_message: Optional[str] = Field(None, description="错误信息")
    
class UpdateSMTPConfigModel(BaseModel):
    """更新SMTP配置模型"""
    smtp_server: Optional[str] = None
    smtp_port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: Optional[bool] = None
    sender_name: Optional[str] = None
    sender_email: Optional[EmailStr] = None

def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }

def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}