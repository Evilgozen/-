import motor.motor_asyncio
from bson.objectid import ObjectId
from datetime import datetime
from typing import Optional, List

from .connection import DatabaseManager

database_manager = DatabaseManager()
database = database_manager.database

file_collection = database.get_collection("files")

class FileCollection:
    @staticmethod
    async def add_file(file_data: dict) -> dict:
        """添加文件记录"""
        file_data["upload_time"] = datetime.now()
        file = await file_collection.insert_one(file_data)
        new_file = await file_collection.find_one({"_id": file.inserted_id})
        return FileCollection.file_helper(new_file)
    
    @staticmethod
    async def retrieve_file(id: str) -> dict:
        """根据ID获取文件信息"""
        file = await file_collection.find_one({"_id": ObjectId(id)})
        if file:
            return FileCollection.file_helper(file)
        return None
    
    @staticmethod
    async def retrieve_files() -> List[dict]:
        """获取所有文件列表"""
        files = []
        async for file in file_collection.find():
            files.append(FileCollection.file_helper(file))
        return files
    
    @staticmethod
    async def delete_file(id: str) -> bool:
        """删除文件记录"""
        file = await file_collection.find_one({"_id": ObjectId(id)})
        if file:
            await file_collection.delete_one({"_id": ObjectId(id)})
            return True
        return False
    
    @staticmethod
    def file_helper(file) -> dict:
        """文件数据格式化"""
        return {
            "id": str(file["_id"]),
            "filename": file["filename"],
            "content_type": file["content_type"],
            "size": file["size"],
            "upload_time": file["upload_time"],
            "file_path": file["file_path"]
        }

file_collection_helper = FileCollection()