import os
import uuid
import aiofiles
from typing import Optional
from fastapi import UploadFile
from ..database.file_collection import file_collection_helper

class FileService:
    def __init__(self):
        # 设置文件上传目录
        self.upload_dir = "uploads"
        os.makedirs(self.upload_dir, exist_ok=True)
    
    async def upload_file(self, file: UploadFile) -> dict:
        """上传文件到服务器"""
        try:
            # 生成唯一文件名
            file_extension = os.path.splitext(file.filename)[1]
            unique_filename = f"{uuid.uuid4()}{file_extension}"
            file_path = os.path.join(self.upload_dir, unique_filename)
            
            # 保存文件到磁盘
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            # 保存文件信息到数据库
            file_data = {
                "filename": file.filename,
                "content_type": file.content_type,
                "size": len(content),
                "file_path": file_path
            }
            
            saved_file = await file_collection_helper.add_file(file_data)
            
            return {
                "success": True,
                "message": "文件上传成功",
                "data": saved_file
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"文件上传失败: {str(e)}"
            }
    
    async def get_file_info(self, file_id: str) -> Optional[dict]:
        """获取文件信息"""
        return await file_collection_helper.retrieve_file(file_id)
    
    async def get_files_list(self) -> list:
        """获取文件列表"""
        return await file_collection_helper.retrieve_files()
    
    async def delete_file(self, file_id: str) -> dict:
        """删除文件"""
        try:
            file_info = await file_collection_helper.retrieve_file(file_id)
            if not file_info:
                return {
                    "success": False,
                    "message": "文件不存在"
                }
            
            # 删除磁盘文件
            if os.path.exists(file_info["file_path"]):
                os.remove(file_info["file_path"])
            
            # 删除数据库记录
            await file_collection_helper.delete_file(file_id)
            
            return {
                "success": True,
                "message": "文件删除成功"
            }
            
        except Exception as e:
            return {
                "success": False,
                "message": f"文件删除失败: {str(e)}"
            }
    
    async def read_file_content(self, file_path: str) -> bytes:
        """读取文件内容"""
        async with aiofiles.open(file_path, 'rb') as f:
            return await f.read()

file_service = FileService()