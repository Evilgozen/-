from bson.objectid import ObjectId
from typing import List, Optional
from .connection import db_manager

class TeacherCollection:
    #简单的ORM，对于同一数据库的单例实现获得不同的表
    def __init__(self):
        self.collection = db_manager.database.get_collection("TeachesItem") #初始化中更改对应的表
    
    #将MongoDB的document格式转换为dict格式
    def teacher_helper(self, teacher) -> dict:
        """将MongoDB文档转换为字典格式"""
        return {
            "id": str(teacher["_id"]),
            "name": teacher["name"],
            "title": teacher["title"],  # 职称
            "url": teacher["url"],     # 个人主页或简介链接
            "email": teacher["email"], # 修正拼写错误
            "resh_dict": teacher["resh_dict"], # 研究方向字典
            "school_college":teacher["school_college"],
            "school_level": teacher.get("school_level"),  # 学校层次
            "school": teacher.get("school")  # 学校名称
        }
    
    #对于find实际上返回值为一个异步的游标对象，需要使用async来进行遍历
    async def retrieve_all(self) -> List[dict]:
        """获取所有教师"""
        teachers = []
        async for teacher in self.collection.find():
            teachers.append(self.teacher_helper(teacher))
        return teachers
    
    async def add_teacher(self, teacher_data: dict) -> dict:
        """添加新教师"""
        teacher = await self.collection.insert_one(teacher_data)
        new_teacher = await self.collection.find_one({"_id": teacher.inserted_id})
        return self.teacher_helper(new_teacher)
    
    async def retrieve_by_id(self, teacher_id: str) -> Optional[dict]:
        """根据ID获取教师"""
        teacher = await self.collection.find_one({"_id": ObjectId(teacher_id)})
        if teacher:
            return self.teacher_helper(teacher)
        return None
    
    async def update_teacher(self, teacher_id: str, data: dict) -> bool:
        """更新教师信息"""
        if len(data) < 1:
            return False
        
        teacher = await self.collection.find_one({"_id": ObjectId(teacher_id)})
        if teacher:
            # 移除空值字段
            update_data = {k: v for k, v in data.items() if v is not None}
            if update_data:
                result = await self.collection.update_one(
                    {"_id": ObjectId(teacher_id)}, 
                    {"$set": update_data}
                )
                return result.modified_count > 0
        return False
    
    async def delete_teacher(self, teacher_id: str) -> bool:
        """删除教师"""
        teacher = await self.collection.find_one({"_id": ObjectId(teacher_id)})
        if teacher:
            result = await self.collection.delete_one({"_id": ObjectId(teacher_id)})
            return result.deleted_count > 0
        return False
    
    async def find_by_email(self, email: str) -> Optional[dict]:
        """根据邮箱查找教师"""
        teacher = await self.collection.find_one({"email": email})
        if teacher:
            return self.teacher_helper(teacher)
        return None
    
    async def find_by_title(self, title: str) -> List[dict]:
        """根据职称查找教师"""
        teachers = []
        async for teacher in self.collection.find({"title": title}):
            teachers.append(self.teacher_helper(teacher))
        return teachers
    
    async def find_by_school_level(self, school_level: str) -> List[dict]:
        """根据学校层次查找教师"""
        teachers = []
        async for teacher in self.collection.find({"school_level": school_level}):
            teachers.append(self.teacher_helper(teacher))
        return teachers
    
    async def find_by_school(self, school: str) -> List[dict]:
        """根据学校名称查找教师"""
        teachers = []
        async for teacher in self.collection.find({"school": school}):
            teachers.append(self.teacher_helper(teacher))
        return teachers

# 全局教师collection实例
teacher_collection = TeacherCollection()