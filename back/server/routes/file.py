from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from typing import List

from ..services.file_service import file_service
from ..models.file import FileResponseModel
from ..models.smtp import ResponseModel, ErrorResponseModel

router = APIRouter()

@router.post("/upload", response_description="文件上传成功")
async def upload_file(file: UploadFile = File(...)):
    """上传文件"""
    # 检查文件大小（限制10MB）
    if file.size and file.size > 10 * 1024 * 1024:
        return ErrorResponseModel(
            "文件过大", 400, "文件大小不能超过10MB"
        )
    
    result = await file_service.upload_file(file)
    
    if result["success"]:
        return ResponseModel(
            result["data"], result["message"]
        )
    else:
        return ErrorResponseModel(
            "上传失败", 500, result["message"]
        )

@router.get("/list", response_description="获取文件列表")
async def get_files_list():
    """获取已上传的文件列表"""
    try:
        files = await file_service.get_files_list()
        return ResponseModel(
            files, "获取文件列表成功"
        )
    except Exception as e:
        return ErrorResponseModel(
            "获取失败", 500, f"获取文件列表失败: {str(e)}"
        )

@router.get("/info/{file_id}", response_description="获取文件信息")
async def get_file_info(file_id: str):
    """获取文件信息"""
    try:
        file_info = await file_service.get_file_info(file_id)
        if file_info:
            return ResponseModel(
                file_info, "获取文件信息成功"
            )
        else:
            return ErrorResponseModel(
                "文件不存在", 404, "未找到指定文件"
            )
    except Exception as e:
        return ErrorResponseModel(
            "获取失败", 500, f"获取文件信息失败: {str(e)}"
        )

@router.delete("/delete/{file_id}", response_description="删除文件")
async def delete_file(file_id: str):
    """删除文件"""
    result = await file_service.delete_file(file_id)
    
    if result["success"]:
        return ResponseModel(
            None, result["message"]
        )
    else:
        return ErrorResponseModel(
            "删除失败", 500, result["message"]
        )

@router.get("/download/{file_id}", response_description="下载文件")
async def download_file(file_id: str):
    """下载文件"""
    try:
        file_info = await file_service.get_file_info(file_id)
        if not file_info:
            raise HTTPException(status_code=404, detail="文件不存在")
        
        return FileResponse(
            path=file_info["file_path"],
            filename=file_info["filename"],
            media_type=file_info["content_type"]
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"下载文件失败: {str(e)}")