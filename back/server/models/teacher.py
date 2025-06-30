from typing import Optional

from pydantic import BaseModel, EmailStr, Field

class TeacherSchema(BaseModel):
    name: str = Field(..., description="教师姓名")
    title: str = Field(..., description="职称，如教授、副教授等")  # 修正：应该是str不是EmailStr
    url: str = Field(..., description="个人主页或简介链接")
    email: EmailStr = Field(..., description="邮箱地址")  # 修正拼写错误
    resh_dict: str = Field(..., description="研究方向")  # 修正：应该是str不是float
    school_college: str = Field(..., description="学院")
    school_level: Optional[str] = Field(None, description="学校层次")
    school: Optional[str] = Field(None, description="学校名称")

    class Config:
        schema_extra = {
            "example": {
                "name": "张教授",
                "title": "教授",
                "url": "https://example.com/profile",
                "email": "zhang@university.edu",
                "resh_dict": "机器学习,深度学习,计算机视觉",
                "school_college": "计算机科学与技术学院",
                "school_level": "985",
                "school": "清华大学"
            }
        }


class UpdateTeacherModel(BaseModel):
    name: Optional[str] = None
    title: Optional[str] = None
    url: Optional[str] = None
    email: Optional[EmailStr] = None
    resh_dict: Optional[str] = None
    school_college: Optional[str] = None
    school_level: Optional[str] = None
    school: Optional[str] = None

    class Config:
        schema_extra = {
            "example": {
                "name": "李教授",
                "title": "副教授",
                "url": "https://example.com/profile",
                "email": "li@university.edu",
                "resh_dict": "自然语言处理,知识图谱",
                "school_college": "信息与通信工程学院",
                "school_level": "211",
                "school": "北京邮电大学"
            }
        }


def ResponseModel(data, message):
    return {
        "data": [data],
        "code": 200,
        "message": message,
    }


def ErrorResponseModel(error, code, message):
    return {"error": error, "code": code, "message": message}
