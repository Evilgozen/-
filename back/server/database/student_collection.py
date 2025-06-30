from bson.objectid import ObjectId
from typing import List, Optional
from .connection import db_manager

class StudentCollection:
    def __init__(self):
        self.collection = db_manager.database.get_collection("students_collection")
    
    def student_helper(self, student) -> dict:
        """将MongoDB文档转换为字典格式"""
        return {
            "id": str(student["_id"]),
            "fullname": student["fullname"],
            "email": student["email"],
            "course_of_study": student["course_of_study"],
            "year": student["year"],
            "gpa": student["gpa"],
        }
    
    async def retrieve_all(self) -> List[dict]:
        """获取所有学生"""
        students = []
        async for student in self.collection.find():
            students.append(self.student_helper(student))
        return students
    
    async def add_student(self, student_data: dict) -> dict:
        """添加新学生"""
        student = await self.collection.insert_one(student_data)
        new_student = await self.collection.find_one({"_id": student.inserted_id})
        return self.student_helper(new_student)
    
    async def retrieve_by_id(self, student_id: str) -> Optional[dict]:
        """根据ID获取学生"""
        student = await self.collection.find_one({"_id": ObjectId(student_id)})
        if student:
            return self.student_helper(student)
        return None
    
    async def update_student(self, student_id: str, data: dict) -> bool:
        """更新学生信息"""
        if len(data) < 1:
            return False
        
        student = await self.collection.find_one({"_id": ObjectId(student_id)})
        if student:
            update_data = {k: v for k, v in data.items() if v is not None}
            if update_data:
                result = await self.collection.update_one(
                    {"_id": ObjectId(student_id)}, 
                    {"$set": update_data}
                )
                return result.modified_count > 0
        return False
    
    async def delete_student(self, student_id: str) -> bool:
        """删除学生"""
        student = await self.collection.find_one({"_id": ObjectId(student_id)})
        if student:
            result = await self.collection.delete_one({"_id": ObjectId(student_id)})
            return result.deleted_count > 0
        return False

# 全局学生collection实例
student_collection = StudentCollection()