import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch, MagicMock
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from server.models.smtp import SMTPConfigSchema, EmailSchema

client = TestClient(app)

class TestSMTPAPI:
    """SMTP API单元测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.base_url = "/api/v1/smtp"
        self.sample_smtp_config = {
            "smtp_server": "smtp.163.com",
            "smtp_port": 465,
            "username": "gmapop163@163.com",  # 修正：使用完整邮箱地址
            "password": "FRYiZ4iP2Gp2Y8pZ",
            "use_tls": False,  # 修正：465端口使用SSL而不是TLS
            "use_ssl": True,   # 添加：启用SSL
            "sender_name": "杨鸿博",
            "sender_email": "gmapop163@163.com"
        }
    
    @patch('server.services.smtp_service.smtp_service.test_smtp_connection')
    @patch('server.database.smtp_collection.smtp_config_collection.get_config')
    @patch('server.database.smtp_collection.smtp_config_collection.add_config')
    def test_add_smtp_config_success(self, mock_add_config, mock_get_config, mock_test_connection):
        """测试成功添加SMTP配置"""
        # 模拟测试连接成功
        mock_test_connection.return_value = asyncio.Future()
        mock_test_connection.return_value.set_result({
            "success": True,
            "message": "连接测试成功"
        })
        
        # 模拟没有现有配置
        mock_get_config.return_value = asyncio.Future()
        mock_get_config.return_value.set_result(None)
        
        # 模拟添加配置成功
        mock_add_config.return_value = asyncio.Future()
        mock_add_config.return_value.set_result({
            "id": "507f1f77bcf86cd799439011",
            **self.sample_smtp_config
        })
        
        response = client.post(f"{self.base_url}/config", json=self.sample_smtp_config)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "SMTP配置添加成功"
    
    @patch('server.services.smtp_service.smtp_service.test_smtp_connection')
    def test_test_smtp_connection_success(self, mock_test_connection):
        """测试SMTP连接测试成功"""
        mock_test_connection.return_value = asyncio.Future()
        mock_test_connection.return_value.set_result({
            "success": True,
            "message": "SMTP连接测试成功",
            "details": "连接到smtp.163.com:465成功"
        })
        
        response = client.post(f"{self.base_url}/test-connection", json=self.sample_smtp_config)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "SMTP连接测试成功"
        assert data["data"]["success"] is True
    
    @patch('server.services.smtp_service.smtp_service.test_smtp_connection')
    def test_test_smtp_connection_failure(self, mock_test_connection):
        """测试SMTP连接测试失败"""
        mock_test_connection.return_value = asyncio.Future()
        mock_test_connection.return_value.set_result({
            "success": False,
            "message": "认证失败：用户名或密码错误"
        })
        
        response = client.post(f"{self.base_url}/test-connection", json=self.sample_smtp_config)
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["code"] == 400
    
    def test_smtp_config_validation(self):
        """测试SMTP配置数据验证"""
        invalid_configs = [
            # 缺少必填字段
            {
                "smtp_server": "smtp.163.com",
                # 缺少其他必填字段
            },
            # 无效的端口号
            {
                **self.sample_smtp_config,
                "smtp_port": "invalid_port"
            },
            # 无效的邮箱格式
            {
                **self.sample_smtp_config,
                "sender_email": "invalid_email"
            }
        ]
        
        for invalid_config in invalid_configs:
            response = client.post(f"{self.base_url}/config", json=invalid_config)
            assert response.status_code == 422  # Pydantic验证错误
    
    @patch('server.database.smtp_collection.smtp_config_collection.get_config')
    def test_get_smtp_config_success(self, mock_get_config):
        """测试成功获取SMTP配置"""
        mock_config = {
            "id": "507f1f77bcf86cd799439011",
            **self.sample_smtp_config
        }
        mock_get_config.return_value = asyncio.Future()
        mock_get_config.return_value.set_result(mock_config)
        
        response = client.get(f"{self.base_url}/config")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "SMTP配置获取成功"
        # 验证密码被隐藏
        assert data["data"]["password"] == "***"
    
    @patch('server.database.smtp_collection.smtp_config_collection.get_config')
    def test_get_smtp_config_not_found(self, mock_get_config):
        """测试获取不存在的SMTP配置"""
        mock_get_config.return_value = asyncio.Future()
        mock_get_config.return_value.set_result(None)
        
        response = client.get(f"{self.base_url}/config")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["code"] == 404

class TestSMTPParameterAnalysis:
    """SMTP参数分析测试类"""
    
    def test_analyze_user_smtp_parameters(self):
        """分析用户提供的SMTP参数"""
        user_params = {
            "smtp_server": "smtp.163.com",
            "smtp_port": 465,
            "username": "杨鸿博",  # 问题：应该是邮箱地址
            "password": "FRYiZ4iP2Gp2Y8pZ",
            "use_tls": True,  # 问题：465端口应该用SSL
            "sender_name": "杨鸿博",
            "sender_email": "gmapop163@163.com"
        }
        
        issues = self._analyze_smtp_params(user_params)
        
        # 验证发现的问题
        assert len(issues) >= 2
        assert any("用户名" in issue for issue in issues)
        assert any("SSL" in issue or "TLS" in issue for issue in issues)
    
    def test_correct_smtp_parameters(self):
        """测试正确的SMTP参数"""
        correct_params = {
            "smtp_server": "smtp.163.com",
            "smtp_port": 465,
            "username": "gmapop163@163.com",  # 正确：使用邮箱地址
            "password": "ABCD1234EFGH5678",  # 正确：16位授权码格式
            "use_tls": False,  # 正确：465端口不使用TLS
            "use_ssl": True,   # 正确：465端口使用SSL
            "sender_name": "杨鸿博",
            "sender_email": "gmapop163@163.com"
        }
        
        issues = self._analyze_smtp_params(correct_params)
        
        # 正确的参数应该没有问题
        assert len(issues) == 0
    
    def _analyze_smtp_params(self, params):
        """分析SMTP参数并返回问题列表"""
        issues = []
        
        # 1. 检查用户名格式
        if "@" not in params.get("username", ""):
            issues.append("用户名应该使用完整的邮箱地址而不是姓名")
        
        # 2. 检查密码长度（163邮箱授权码通常是16位）
        password = params.get("password", "")
        if len(password) < 16:
            issues.append("163邮箱建议使用授权码，通常为16位字符")
        
        # 3. 检查端口和加密方式的匹配
        port = params.get("smtp_port")
        use_tls = params.get("use_tls")
        use_ssl = params.get("use_ssl")
        
        if port == 465 and use_tls:
            issues.append("465端口应该使用SSL连接，不应该启用TLS")
        
        if port == 465 and not use_ssl:
            issues.append("465端口应该启用SSL连接")
        
        if port == 587 and not use_tls:
            issues.append("587端口应该启用TLS连接")
        
        # 4. 检查邮箱域名匹配
        smtp_server = params.get("smtp_server", "")
        sender_email = params.get("sender_email", "")
        
        if "163.com" in smtp_server and "@163.com" not in sender_email:
            issues.append("SMTP服务器和发送邮箱的域名不匹配")
        
        return issues
    
    def test_generate_correct_curl_command(self):
        """生成正确的curl命令"""
        correct_curl = '''
curl -X 'POST' \\
  'http://127.0.0.1:8000/api/v1/smtp/test-connection' \\
  -H 'accept: application/json' \\
  -H 'Content-Type: application/json' \\
  -d '{
    "smtp_server": "smtp.163.com",
    "smtp_port": 465,
    "username": "gmapop163@163.com",
    "password": "your_16_digit_auth_code",
    "use_tls": false,
    "use_ssl": true,
    "sender_name": "杨鸿博",
    "sender_email": "gmapop163@163.com"
  }'
'''
        
        # 验证URL路径正确
        assert "/api/v1/smtp/test-connection" in correct_curl
        # 验证使用SSL而不是TLS
        assert '"use_ssl": true' in correct_curl
        assert '"use_tls": false' in correct_curl
        # 验证使用邮箱地址作为用户名
        assert '"username": "gmapop163@163.com"' in correct_curl

class TestEmailSending:
    """邮件发送测试类"""
    
    def setup_method(self):
        self.base_url = "/api/v1/smtp"
        self.sample_email = {
            "to_emails": ["recipient@example.com"],
            "subject": "测试邮件",
            "body": "这是一封测试邮件",
            "is_html": False
        }
    
    @patch('server.services.smtp_service.smtp_service.send_email')
    def test_send_email_success(self, mock_send_email):
        """测试成功发送邮件"""
        mock_send_email.return_value = asyncio.Future()
        mock_send_email.return_value.set_result({
            "success": True,
            "message": "邮件发送成功",
            "message_id": "<test@example.com>"
        })
        
        response = client.post(f"{self.base_url}/send", json=self.sample_email)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "邮件发送成功"
    
    @patch('server.services.smtp_service.smtp_service.send_email')
    def test_send_email_failure(self, mock_send_email):
        """测试邮件发送失败"""
        mock_send_email.return_value = asyncio.Future()
        mock_send_email.return_value.set_result({
            "success": False,
            "message": "邮件发送失败：SMTP服务器连接超时"
        })
        
        response = client.post(f"{self.base_url}/send", json=self.sample_email)
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data

if __name__ == "__main__":
    # 运行测试
    pytest.main(["-v", __file__])
    
    # 输出SMTP参数分析结果
    print("\n" + "="*50)
    print("SMTP参数问题分析")
    print("="*50)
    
    analyzer = TestSMTPParameterAnalysis()
    
    # 分析用户的原始参数
    user_params = {
        "smtp_server": "smtp.163.com",
        "smtp_port": 465,
        "username": "杨鸿博",
        "password": "FRYiZ4iP2Gp2Y8pZ",
        "use_tls": True,
        "sender_name": "杨鸿博",
        "sender_email": "gmapop163@163.com"
    }
    
    issues = analyzer._analyze_smtp_params(user_params)
    
    print("\n原始参数存在的问题:")
    for i, issue in enumerate(issues, 1):
        print(f"{i}. {issue}")
    
    print("\n修正后的正确curl命令:")
    print("curl -X 'POST' \\")
    print("  'http://127.0.0.1:8000/api/v1/smtp/test-connection' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "smtp_server": "smtp.163.com",')
    print('    "smtp_port": 465,')
    print('    "username": "gmapop163@163.com",')
    print('    "password": "your_16_digit_auth_code",')
    print('    "use_tls": false,')
    print('    "use_ssl": true,')
    print('    "sender_name": "杨鸿博",')
    print('    "sender_email": "gmapop163@163.com"')
    print("  }'")
    
    print("\n注意事项:")
    print("1. 163邮箱需要开启SMTP服务并获取授权码")
    print("2. 授权码不是登录密码，需要在邮箱设置中单独生成")
    print("3. 465端口使用SSL加密，不是TLS")
    print("4. 用户名必须是完整的邮箱地址")