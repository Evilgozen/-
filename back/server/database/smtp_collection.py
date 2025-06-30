from bson.objectid import ObjectId
from typing import List, Optional
from datetime import datetime
from .connection import db_manager

class SMTPConfigCollection:
    """SMTP配置数据库操作类"""
    def __init__(self):
        self.collection = db_manager.database.get_collection("smtp_config")
    
    def smtp_config_helper(self, config) -> dict:
        """将MongoDB文档转换为字典格式"""
        return {
            "id": str(config["_id"]),
            "smtp_server": config["smtp_server"],
            "smtp_port": config["smtp_port"],
            "username": config["username"],
            "password": config["password"],
            "use_tls": config["use_tls"],
            "sender_name": config["sender_name"],
            "sender_email": config["sender_email"],
            "created_at": config.get("created_at"),
            "updated_at": config.get("updated_at")
        }
    
    async def add_config(self, config_data: dict) -> dict:
        """添加SMTP配置"""
        config_data["created_at"] = datetime.utcnow()
        config_data["updated_at"] = datetime.utcnow()
        config = await self.collection.insert_one(config_data)
        new_config = await self.collection.find_one({"_id": config.inserted_id})
        return self.smtp_config_helper(new_config)
    
    async def get_config(self) -> Optional[dict]:
        """获取当前SMTP配置（假设只有一个配置）"""
        config = await self.collection.find_one()
        if config:
            return self.smtp_config_helper(config)
        return None
    
    async def update_config(self, config_id: str, data: dict) -> bool:
        """更新SMTP配置"""
        if len(data) < 1:
            return False
        
        config = await self.collection.find_one({"_id": ObjectId(config_id)})
        if config:
            update_data = {k: v for k, v in data.items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            if update_data:
                result = await self.collection.update_one(
                    {"_id": ObjectId(config_id)}, 
                    {"$set": update_data}
                )
                return result.modified_count > 0
        return False
    
    async def delete_config(self, config_id: str) -> bool:
        """删除SMTP配置"""
        config = await self.collection.find_one({"_id": ObjectId(config_id)})
        if config:
            result = await self.collection.delete_one({"_id": ObjectId(config_id)})
            return result.deleted_count > 0
        return False

class EmailLogCollection:
    """邮件发送记录数据库操作类"""
    def __init__(self):
        self.collection = db_manager.database.get_collection("email_logs")
    
    def email_log_helper(self, log) -> dict:
        """将MongoDB文档转换为字典格式"""
        return {
            "id": str(log["_id"]),
            "to_emails": log["to_emails"],
            "cc_emails": log.get("cc_emails"),
            "bcc_emails": log.get("bcc_emails"),
            "subject": log["subject"],
            "body": log["body"],
            "sender_email": log["sender_email"],
            "send_time": log["send_time"],
            "status": log["status"],
            "error_message": log.get("error_message")
        }
    
    async def add_log(self, log_data: dict) -> dict:
        """添加邮件发送记录"""
        log = await self.collection.insert_one(log_data)
        new_log = await self.collection.find_one({"_id": log.inserted_id})
        return self.email_log_helper(new_log)
    
    async def get_all_logs(self, limit: int = 100) -> List[dict]:
        """获取所有邮件发送记录"""
        logs = []
        async for log in self.collection.find().sort("send_time", -1).limit(limit):
            logs.append(self.email_log_helper(log))
        return logs
    
    async def get_logs_by_status(self, status: str, limit: int = 100) -> List[dict]:
        """根据状态获取邮件发送记录"""
        logs = []
        async for log in self.collection.find({"status": status}).sort("send_time", -1).limit(limit):
            logs.append(self.email_log_helper(log))
        return logs
    
    async def get_logs_by_email(self, email: str, limit: int = 100) -> List[dict]:
        """根据收件人邮箱获取发送记录"""
        logs = []
        async for log in self.collection.find({"to_emails": {"$in": [email]}}).sort("send_time", -1).limit(limit):
            logs.append(self.email_log_helper(log))
        return logs

# 全局实例
smtp_config_collection = SMTPConfigCollection()
email_log_collection = EmailLogCollection()