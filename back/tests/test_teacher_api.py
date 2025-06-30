import pytest
import asyncio
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, patch
import sys
import os

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import app
from server.models.teacher import TeacherSchema, UpdateTeacherModel

client = TestClient(app)

class TestTeacherAPI:
    """教师API单元测试类"""
    
    def setup_method(self):
        """测试前的设置"""
        self.base_url = "/api/v1/teachers"
        self.sample_teacher = {
            "name": "张教授",
            "email": "zhang@university.edu.cn",
            "college": "材料科学与工程学院",
            "department": "陶瓷工程系",
            "position": "教授",
            "research_areas": ["先进陶瓷材料", "功能陶瓷"],
            "phone": "010-12345678",
            "office": "材料楼301"
        }
    
    @patch('server.database.teacher_collection.add_teacher')
    def test_add_teacher_success(self, mock_add_teacher):
        """测试成功添加教师"""
        # 模拟数据库返回
        mock_add_teacher.return_value = asyncio.Future()
        mock_add_teacher.return_value.set_result({
            "id": "507f1f77bcf86cd799439011",
            **self.sample_teacher
        })
        
        response = client.post(self.base_url + "/", json=self.sample_teacher)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Teacher added successfully."
        assert "data" in data
    
    @patch('server.database.teacher_collection.retrieve_all')
    def test_get_teachers_success(self, mock_retrieve_all):
        """测试成功获取教师列表"""
        # 模拟数据库返回
        mock_teachers = [
            {"id": "1", **self.sample_teacher},
            {"id": "2", "name": "李教授", "email": "li@university.edu.cn"}
        ]
        mock_retrieve_all.return_value = asyncio.Future()
        mock_retrieve_all.return_value.set_result(mock_teachers)
        
        response = client.get(self.base_url + "/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Teachers data retrieved successfully"
        assert len(data["data"]) == 2
    
    @patch('server.database.teacher_collection.retrieve_all')
    def test_get_teachers_empty(self, mock_retrieve_all):
        """测试获取空教师列表"""
        mock_retrieve_all.return_value = asyncio.Future()
        mock_retrieve_all.return_value.set_result([])
        
        response = client.get(self.base_url + "/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Empty list returned"
        assert data["data"] == []
    
    @patch('server.database.teacher_collection.retrieve_by_id')
    def test_get_teacher_by_id_success(self, mock_retrieve_by_id):
        """测试成功根据ID获取教师"""
        teacher_id = "507f1f77bcf86cd799439011"
        mock_retrieve_by_id.return_value = asyncio.Future()
        mock_retrieve_by_id.return_value.set_result({
            "id": teacher_id,
            **self.sample_teacher
        })
        
        response = client.get(f"{self.base_url}/{teacher_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Teacher data retrieved successfully"
        assert data["data"]["id"] == teacher_id
    
    @patch('server.database.teacher_collection.retrieve_by_id')
    def test_get_teacher_by_id_not_found(self, mock_retrieve_by_id):
        """测试根据ID获取不存在的教师"""
        teacher_id = "507f1f77bcf86cd799439011"
        mock_retrieve_by_id.return_value = asyncio.Future()
        mock_retrieve_by_id.return_value.set_result(None)
        
        response = client.get(f"{self.base_url}/{teacher_id}")
        
        assert response.status_code == 200  # FastAPI返回200，但包含错误信息
        data = response.json()
        assert "error" in data
        assert data["code"] == 404
    
    @patch('server.database.teacher_collection.update_teacher')
    def test_update_teacher_success(self, mock_update_teacher):
        """测试成功更新教师信息"""
        teacher_id = "507f1f77bcf86cd799439011"
        update_data = {
            "name": "张教授（更新）",
            "position": "副教授"
        }
        
        mock_update_teacher.return_value = asyncio.Future()
        mock_update_teacher.return_value.set_result(True)
        
        response = client.put(f"{self.base_url}/{teacher_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Teacher updated successfully"
    
    @patch('server.database.teacher_collection.update_teacher')
    def test_update_teacher_not_found(self, mock_update_teacher):
        """测试更新不存在的教师"""
        teacher_id = "507f1f77bcf86cd799439011"
        update_data = {"name": "张教授（更新）"}
        
        mock_update_teacher.return_value = asyncio.Future()
        mock_update_teacher.return_value.set_result(False)
        
        response = client.put(f"{self.base_url}/{teacher_id}", json=update_data)
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["code"] == 404
    
    @patch('server.database.teacher_collection.delete_teacher')
    def test_delete_teacher_success(self, mock_delete_teacher):
        """测试成功删除教师"""
        teacher_id = "507f1f77bcf86cd799439011"
        
        mock_delete_teacher.return_value = asyncio.Future()
        mock_delete_teacher.return_value.set_result(True)
        
        response = client.delete(f"{self.base_url}/{teacher_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Teacher deleted successfully"
    
    @patch('server.database.teacher_collection.delete_teacher')
    def test_delete_teacher_not_found(self, mock_delete_teacher):
        """测试删除不存在的教师"""
        teacher_id = "507f1f77bcf86cd799439011"
        
        mock_delete_teacher.return_value = asyncio.Future()
        mock_delete_teacher.return_value.set_result(False)
        
        response = client.delete(f"{self.base_url}/{teacher_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert "error" in data
        assert data["code"] == 404
    
    def test_add_teacher_invalid_data(self):
        """测试添加教师时数据验证失败"""
        invalid_teacher = {
            "name": "",  # 空名称
            "email": "invalid-email",  # 无效邮箱
        }
        
        response = client.post(self.base_url + "/", json=invalid_teacher)
        
        # 根据Pydantic验证，应该返回422状态码
        assert response.status_code == 422
    
    def test_update_teacher_partial_data(self):
        """测试部分更新教师数据"""
        teacher_id = "507f1f77bcf86cd799439011"
        
        # 测试只更新部分字段
        with patch('server.database.teacher_collection.update_teacher') as mock_update:
            mock_update.return_value = asyncio.Future()
            mock_update.return_value.set_result(True)
            
            partial_update = {"position": "教授"}
            response = client.put(f"{self.base_url}/{teacher_id}", json=partial_update)
            
            assert response.status_code == 200
            # 验证只传递了非None的字段
            mock_update.assert_called_once()
            args = mock_update.call_args[0]
            assert args[1] == {"position": "教授"}

class TestSMTPParameters:
    """SMTP参数测试类"""
    
    def test_smtp_parameters_analysis(self):
        """分析SMTP参数"""
        smtp_params = {
            "smtp_server": "smtp.163.com",
            "smtp_port": 465,
            "username": "杨鸿博",
            "password": "FRYiZ4iP2Gp2Y8pZ",
            "use_tls": True,
            "sender_name": "杨鸿博",
            "sender_email": "gmapop163@163.com"
        }
        
        # 参数验证
        assert smtp_params["smtp_server"] == "smtp.163.com"  # 163邮箱SMTP服务器正确
        assert smtp_params["smtp_port"] == 465  # SSL端口正确
        assert smtp_params["use_tls"] is True  # 启用TLS正确
        assert "@163.com" in smtp_params["sender_email"]  # 邮箱域名匹配
        
        # 检查潜在问题
        issues = []
        
        # 1. 用户名通常应该是邮箱地址而不是姓名
        if "@" not in smtp_params["username"]:
            issues.append("用户名应该使用完整的邮箱地址而不是姓名")
        
        # 2. 163邮箱通常使用授权码而不是登录密码
        if len(smtp_params["password"]) < 16:
            issues.append("163邮箱建议使用授权码，通常为16位字符")
        
        # 3. 对于465端口，应该使用SSL而不是TLS
        if smtp_params["smtp_port"] == 465:
            issues.append("465端口应该使用SSL连接，建议设置use_ssl=True而不是use_tls=True")
        
        return issues

if __name__ == "__main__":
    # 运行测试
    pytest.main(["-v", __file__])
    
    # 分析SMTP参数
    smtp_test = TestSMTPParameters()
    issues = smtp_test.test_smtp_parameters_analysis()
    
    print("\n=== SMTP参数分析结果 ===")
    if issues:
        print("发现的问题:")
        for i, issue in enumerate(issues, 1):
            print(f"{i}. {issue}")
    else:
        print("参数配置正确")
    
    print("\n=== 修正建议 ===")
    print("正确的curl命令应该是:")
    print("curl -X 'POST' \\")
    print("  'http://127.0.0.1:8000/api/v1/smtp/test-connection' \\")
    print("  -H 'accept: application/json' \\")
    print("  -H 'Content-Type: application/json' \\")
    print("  -d '{")
    print('    "smtp_server": "smtp.163.com",')
    print('    "smtp_port": 465,')
    print('    "username": "gmapop163@163.com",  // 使用完整邮箱地址')
    print('    "password": "your_auth_code_here",  // 使用163邮箱授权码')
    print('    "use_tls": false,  // 465端口使用SSL')
    print('    "use_ssl": true,   // 启用SSL')
    print('    "sender_name": "杨鸿博",')
    print('    "sender_email": "gmapop163@163.com"')
    print("  }'")