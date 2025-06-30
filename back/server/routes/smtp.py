from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.encoders import jsonable_encoder
from typing import Optional

from ..database.smtp_collection import smtp_config_collection, email_log_collection
from ..services.smtp_service import smtp_service
from ..models.smtp import (
    SMTPConfigSchema,
    UpdateSMTPConfigModel,
    EmailSchema,
    ResponseModel,
    ErrorResponseModel,
)

router = APIRouter()

# SMTP配置相关接口
@router.post("/config", response_description="SMTP配置添加成功")
async def add_smtp_config(config: SMTPConfigSchema = Body(...)):
    """添加或更新SMTP配置"""
    try:
        config_data = jsonable_encoder(config)
        
        # 测试SMTP连接
        test_result = await smtp_service.test_smtp_connection(config_data)
        if not test_result["success"]:
            return ErrorResponseModel(
                "SMTP配置测试失败", 400, test_result["message"]
            )
        
        # 检查是否已存在配置
        existing_config = await smtp_config_collection.get_config()
        if existing_config:
            # 更新现有配置
            updated = await smtp_config_collection.update_config(
                existing_config["id"], config_data
            )
            if updated:
                return ResponseModel(
                    config_data, "SMTP配置更新成功"
                )
            else:
                return ErrorResponseModel(
                    "更新失败", 500, "SMTP配置更新失败"
                )
        else:
            # 添加新配置
            new_config = await smtp_config_collection.add_config(config_data)
            return ResponseModel(new_config, "SMTP配置添加成功")
            
    except Exception as e:
        return ErrorResponseModel(
            "配置失败", 500, f"SMTP配置操作失败: {str(e)}"
        )

@router.get("/config", response_description="获取SMTP配置")
async def get_smtp_config():
    """获取当前SMTP配置"""
    config = await smtp_config_collection.get_config()
    if config:
        # 隐藏敏感信息
        config_safe = config.copy()
        config_safe["password"] = "***"
        return ResponseModel(config_safe, "SMTP配置获取成功")
    return ErrorResponseModel("未找到配置", 404, "SMTP配置不存在")

@router.put("/config/{config_id}", response_description="更新SMTP配置")
async def update_smtp_config(
    config_id: str, 
    config: UpdateSMTPConfigModel = Body(...)
):
    """更新SMTP配置"""
    try:
        config_data = {k: v for k, v in config.dict().items() if v is not None}
        
        if config_data:
            # 如果更新了关键配置，测试连接
            if any(key in config_data for key in ["smtp_server", "smtp_port", "username", "password"]):
                # 获取完整配置进行测试
                existing_config = await smtp_config_collection.get_config()
                if existing_config:
                    test_config = existing_config.copy()
                    test_config.update(config_data)
                    test_result = await smtp_service.test_smtp_connection(test_config)
                    if not test_result["success"]:
                        return ErrorResponseModel(
                            "SMTP配置测试失败", 400, test_result["message"]
                        )
            
            updated = await smtp_config_collection.update_config(config_id, config_data)
            if updated:
                return ResponseModel(
                    f"配置ID: {config_id} 更新成功",
                    "SMTP配置更新成功"
                )
        
        return ErrorResponseModel(
            "更新失败", 404, "SMTP配置更新失败或配置不存在"
        )
        
    except Exception as e:
        return ErrorResponseModel(
            "更新失败", 500, f"SMTP配置更新失败: {str(e)}"
        )

@router.delete("/config/{config_id}", response_description="删除SMTP配置")
async def delete_smtp_config(config_id: str):
    """删除SMTP配置"""
    deleted = await smtp_config_collection.delete_config(config_id)
    if deleted:
        return ResponseModel(
            f"配置ID: {config_id} 删除成功",
            "SMTP配置删除成功"
        )
    return ErrorResponseModel(
        "删除失败", 404, "SMTP配置不存在或删除失败"
    )

@router.post("/test-connection", response_description="测试SMTP连接")
async def test_smtp_connection(config: SMTPConfigSchema = Body(...)):
    """测试SMTP连接"""
    config_data = jsonable_encoder(config)
    result = await smtp_service.test_smtp_connection(config_data)
    
    if result["success"]:
        return ResponseModel(result, "SMTP连接测试成功")
    else:
        return ErrorResponseModel(
            "连接测试失败", 400, result["message"]
        )

# 邮件发送相关接口
@router.post("/send", response_description="发送邮件")
async def send_email(email: EmailSchema = Body(...)):
    """发送邮件"""
    try:
        result = await smtp_service.send_email(
            to_emails=email.to_emails,
            subject=email.subject,
            body=email.body,
            cc_emails=email.cc_emails,
            bcc_emails=email.bcc_emails,
            is_html=email.is_html,
            attachments=email.attachments
        )
        
        if result["success"]:
            return ResponseModel(result, "邮件发送成功")
        else:
            return ErrorResponseModel(
                "邮件发送失败", 500, result["message"]
            )
            
    except Exception as e:
        return ErrorResponseModel(
            "发送失败", 500, f"邮件发送失败: {str(e)}"
        )

@router.post("/send-to-teachers", response_description="批量发送邮件给教师")
async def send_email_to_teachers(
    teacher_ids: list = Body(..., description="教师ID列表"),
    subject: str = Body(..., description="邮件主题"),
    body: str = Body(..., description="邮件正文"),
    is_html: bool = Body(False, description="是否为HTML格式")
):
    """批量发送邮件给指定教师"""
    try:
        from ..database.teacher_collection import teacher_collection
        
        # 获取教师邮箱列表
        teacher_emails = []
        for teacher_id in teacher_ids:
            teacher = await teacher_collection.retrieve_by_id(teacher_id)
            if teacher and teacher.get("email"):
                teacher_emails.append(teacher["email"])
        
        if not teacher_emails:
            return ErrorResponseModel(
                "无有效邮箱", 400, "未找到有效的教师邮箱地址"
            )
        
        result = await smtp_service.send_email(
            to_emails=teacher_emails,
            subject=subject,
            body=body,
            is_html=is_html
        )
        
        if result["success"]:
            return ResponseModel(
                {"sent_to": teacher_emails, "count": len(teacher_emails)},
                f"邮件已发送给 {len(teacher_emails)} 位教师"
            )
        else:
            return ErrorResponseModel(
                "批量发送失败", 500, result["message"]
            )
            
    except Exception as e:
        return ErrorResponseModel(
            "批量发送失败", 500, f"批量邮件发送失败: {str(e)}"
        )

# 邮件日志相关接口
@router.get("/logs", response_description="获取邮件发送日志")
async def get_email_logs(
    limit: int = Query(100, description="返回记录数量限制"),
    status: Optional[str] = Query(None, description="过滤状态：success/failed")
):
    """获取邮件发送日志"""
    try:
        if status:
            logs = await email_log_collection.get_logs_by_status(status, limit)
        else:
            logs = await email_log_collection.get_all_logs(limit)
        
        return ResponseModel(logs, f"获取到 {len(logs)} 条邮件日志")
        
    except Exception as e:
        return ErrorResponseModel(
            "获取日志失败", 500, f"获取邮件日志失败: {str(e)}"
        )

@router.get("/logs/email/{email}", response_description="根据邮箱获取发送日志")
async def get_logs_by_email(
    email: str,
    limit: int = Query(100, description="返回记录数量限制")
):
    """根据收件人邮箱获取发送日志"""
    try:
        logs = await email_log_collection.get_logs_by_email(email, limit)
        return ResponseModel(logs, f"获取到 {len(logs)} 条相关邮件日志")
        
    except Exception as e:
        return ErrorResponseModel(
            "获取日志失败", 500, f"获取邮件日志失败: {str(e)}"
        )