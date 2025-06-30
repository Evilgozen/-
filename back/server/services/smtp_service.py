import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from email.header import Header
from email.utils import formataddr
from typing import List, Optional, Dict
from datetime import datetime
import os
import logging
import base64
import mimetypes
import urllib.parse

from ..database.smtp_collection import smtp_config_collection, email_log_collection

class SMTPService:
    """SMTP邮件发送服务类"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    async def get_smtp_config(self) -> Optional[dict]:
        """获取SMTP配置"""
        return await smtp_config_collection.get_config()
    
    async def send_email(
        self,
        to_emails: List[str],
        subject: str,
        body: str,
        cc_emails: Optional[List[str]] = None,
        bcc_emails: Optional[List[str]] = None,
        is_html: bool = False,
        attachment_ids: Optional[List[str]] = None
    ) -> Dict[str, any]:
        """发送邮件"""
        
        # 获取SMTP配置
        config = await self.get_smtp_config()
        if not config:
            error_msg = "SMTP配置不存在，请先配置SMTP服务器"
            await self._log_email_attempt(
                to_emails, cc_emails, bcc_emails, subject, body, 
                "", "failed", error_msg
            )
            return {"success": False, "message": error_msg}
        
        try:
            # 创建邮件消息
            message = MIMEMultipart()
            
            # 正确构造From头部，支持非ASCII字符
            sender_name = config['sender_name']
            sender_email = config['sender_email']
            
            # 检查发送者名称是否包含非ASCII字符
            try:
                sender_name.encode('ascii')
                # 如果是纯ASCII字符，直接使用
                from_header = f"{sender_name} <{sender_email}>"
            except UnicodeEncodeError:
                # 如果包含非ASCII字符，使用RFC2047编码
                encoded_name = Header(sender_name, 'utf-8').encode()
                from_header = f"{encoded_name} <{sender_email}>"
            
            message["From"] = from_header
            message["To"] = ", ".join(to_emails)
            
            # 对主题也进行编码处理
            try:
                subject.encode('ascii')
                message["Subject"] = subject
            except UnicodeEncodeError:
                message["Subject"] = Header(subject, 'utf-8').encode()
            
            if cc_emails:
                message["Cc"] = ", ".join(cc_emails)
            
            # 添加邮件正文
            if is_html:
                message.attach(MIMEText(body, "html", "utf-8"))
            else:
                message.attach(MIMEText(body, "plain", "utf-8"))
            
            # 添加附件
            if attachment_ids:
                from ..services.file_service import file_service
                
                for file_id in attachment_ids:
                    try:
                        # 获取文件信息
                        file_info = await file_service.get_file_info(file_id)
                        if not file_info:
                            continue
                        
                        # 读取文件内容
                        file_data = await file_service.read_file_content(file_info['file_path'])
                        original_size = len(file_data)
                        
                        # 确定MIME类型，优先使用数据库中的content_type，如果为空则根据文件扩展名推断
                        mime_type = file_info['content_type']
                        if not mime_type or mime_type == 'application/octet-stream':
                            # 使用mimetypes模块根据文件扩展名推断MIME类型
                            guessed_type, _ = mimetypes.guess_type(file_info['filename'])
                            mime_type = guessed_type or 'application/octet-stream'
                        
                        main_type, sub_type = mime_type.split('/', 1) if '/' in mime_type else ('application', 'octet-stream')
                        
                        self.logger.info(f"附件 {file_info['filename']} 原始大小: {original_size} bytes, MIME类型: {mime_type}")
                        
                        # 创建附件部分 - 使用更标准的方式
                        if main_type == 'text':
                            # 对于文本文件，使用MIMEText
                            if isinstance(file_data, bytes):
                                file_data = file_data.decode('utf-8', errors='replace')
                            part = MIMEText(file_data, sub_type, 'utf-8')
                        else:
                            # 对于二进制文件，使用MIMEBase
                            part = MIMEBase(main_type, sub_type)
                            
                            # 确保文件数据是bytes类型
                            if isinstance(file_data, str):
                                file_data = file_data.encode('utf-8')
                            
                            part.set_payload(file_data)
                            
                            # 编码附件
                            encoders.encode_base64(part)
                        
                        # 记录处理后的大小
                        if main_type == 'text':
                            processed_size = len(part.get_payload().encode('utf-8'))
                            self.logger.info(f"附件 {file_info['filename']} 文本处理后大小: {processed_size} bytes")
                        else:
                            encoded_size = len(part.get_payload())
                            self.logger.info(f"附件 {file_info['filename']} base64编码后大小: {encoded_size} bytes")
                        
                        # 添加附件头部
                        filename = file_info['filename']
                        
                        # 使用正确的方式设置Content-Disposition，避免邮件客户端显示为.bin文件
                        try:
                            # 尝试ASCII编码
                            filename.encode('ascii')
                            # 如果是ASCII字符，直接使用
                            disposition = f'attachment; filename="{filename}"'
                        except UnicodeEncodeError:
                            # 如果包含非ASCII字符，使用RFC2231标准
                            encoded_filename = urllib.parse.quote(filename, safe='')
                            disposition = f'attachment; filename*=utf-8\'\'{encoded_filename}'
                        
                        # 设置附件头部信息
                        part.add_header("Content-Disposition", disposition)
                        
                        # 对于文本文件，确保正确的Content-Type设置
                        if main_type == 'text':
                            # MIMEText会自动设置Content-Type，但我们需要确保它作为附件处理
                            part.replace_header('Content-Type', f'{mime_type}; name="{filename}"')
                        
                        # Content-Transfer-Encoding会由相应的MIME类和编码器自动设置
                        message.attach(part)
                        
                    except Exception as e:
                        self.logger.warning(f"附件处理失败: {str(e)}")
                        continue
            
            # 准备收件人列表
            all_recipients = to_emails.copy()
            if cc_emails:
                all_recipients.extend(cc_emails)
            if bcc_emails:
                all_recipients.extend(bcc_emails)
            
            # 发送邮件
            context = ssl.create_default_context()
            
            # 针对163邮箱的特殊处理
            if "163.com" in config["smtp_server"]:
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            # 根据端口选择连接方式
            if config["smtp_port"] == 465:
                # 465端口使用SSL
                with smtplib.SMTP_SSL(config["smtp_server"], config["smtp_port"], context=context) as server:
                    server.login(config["username"], config["password"])
                    text = message.as_string()
                    server.sendmail(config["sender_email"], all_recipients, text)
            else:
                # 587端口使用TLS
                with smtplib.SMTP(config["smtp_server"], config["smtp_port"], timeout=30) as server:
                    server.ehlo()
                    if config["use_tls"]:
                        server.starttls(context=context)
                        server.ehlo()
                    server.login(config["username"], config["password"])
                    text = message.as_string()
                    server.sendmail(config["sender_email"], all_recipients, text)
            
            # 记录成功日志
            await self._log_email_attempt(
                to_emails, cc_emails, bcc_emails, subject, body,
                config["sender_email"], "success", None
            )
            
            self.logger.info(f"邮件发送成功: {subject} -> {', '.join(to_emails)}")
            return {"success": True, "message": "邮件发送成功"}
            
        except smtplib.SMTPAuthenticationError as e:
            error_msg = f"SMTP认证失败: {str(e)}"
            self.logger.error(error_msg)
            await self._log_email_attempt(
                to_emails, cc_emails, bcc_emails, subject, body,
                config.get("sender_email", ""), "failed", error_msg
            )
            return {"success": False, "message": error_msg}
            
        except smtplib.SMTPConnectError as e:
            error_msg = f"SMTP连接失败: {str(e)}"
            self.logger.error(error_msg)
            await self._log_email_attempt(
                to_emails, cc_emails, bcc_emails, subject, body,
                config.get("sender_email", ""), "failed", error_msg
            )
            return {"success": False, "message": error_msg}
            
        except Exception as e:
            error_msg = f"邮件发送失败: {str(e)}"
            self.logger.error(error_msg)
            await self._log_email_attempt(
                to_emails, cc_emails, bcc_emails, subject, body,
                config.get("sender_email", ""), "failed", error_msg
            )
            return {"success": False, "message": error_msg}
    
    async def _log_email_attempt(
        self,
        to_emails: List[str],
        cc_emails: Optional[List[str]],
        bcc_emails: Optional[List[str]],
        subject: str,
        body: str,
        sender_email: str,
        status: str,
        error_message: Optional[str]
    ):
        """记录邮件发送尝试"""
        log_data = {
            "to_emails": to_emails,
            "cc_emails": cc_emails or [],
            "bcc_emails": bcc_emails or [],
            "subject": subject,
            "body": body,
            "sender_email": sender_email,
            "send_time": datetime.utcnow(),
            "status": status,
            "error_message": error_message
        }
        await email_log_collection.add_log(log_data)
    
    async def test_smtp_connection(self, config_data: dict) -> dict:
        """测试SMTP连接"""
        try:
            context = ssl.create_default_context()
            
            # 针对163邮箱的特殊处理
            if "163.com" in config_data["smtp_server"]:
                # 163邮箱建议使用更宽松的SSL设置
                context.check_hostname = False
                context.verify_mode = ssl.CERT_NONE
            
            # 根据端口选择连接方式
            if config_data["smtp_port"] == 465:
                # 465端口使用SSL
                with smtplib.SMTP_SSL(config_data["smtp_server"], config_data["smtp_port"], context=context) as server:
                    server.set_debuglevel(1)  # 启用调试模式
                    server.login(config_data["username"], config_data["password"])
            else:
                # 587端口使用TLS
                with smtplib.SMTP(config_data["smtp_server"], config_data["smtp_port"], timeout=30) as server:
                    server.set_debuglevel(1)  # 启用调试模式
                    server.ehlo()  # 发送EHLO命令
                    if config_data["use_tls"]:
                        server.starttls(context=context)
                        server.ehlo()  # TLS后再次发送EHLO
                    server.login(config_data["username"], config_data["password"])
            
            return {"success": True, "message": "SMTP连接测试成功"}
            
        except smtplib.SMTPAuthenticationError as e:
            return {"success": False, "message": f"SMTP认证失败，请检查用户名和密码（授权码）: {str(e)}"}
        except smtplib.SMTPConnectError as e:
            return {"success": False, "message": f"SMTP连接失败，请检查服务器地址和端口: {str(e)}"}
        except smtplib.SMTPServerDisconnected as e:
            return {"success": False, "message": f"服务器连接意外断开，可能是网络问题或服务器限制: {str(e)}"}
        except Exception as e:
            return {"success": False, "message": f"连接测试失败: {str(e)}"}

# 全局SMTP服务实例
smtp_service = SMTPService()