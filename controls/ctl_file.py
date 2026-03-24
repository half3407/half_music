import os

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from config import settings
from sqlalchemy.orm import Session
from deps.database import get_db
from deps.permissions import require_admin, require_authenticated
import uuid
import shutil
from pathlib import Path

from models.user import User

file_router = APIRouter(prefix="/files", tags=["文件管理"])

@file_router.post("/cover")
async def upload_cover(
    file: UploadFile = File(...),
    user = Depends(require_admin)  # 验证管理员身份
):
    # 验证文件类型（只允许图片）
    if file.content_type not in settings.allowed_image_types_list:
        raise HTTPException(400, detail=f"仅支持图片: {', '.join(settings.allowed_image_types_list)}")
    
    # 验证文件大小
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE:
        raise HTTPException(400, detail=f"文件超过 {settings.MAX_UPLOAD_SIZE // 1024 // 1024}MB 限制")
    
    # 生成安全文件名（避免中文/特殊字符问题）
    ext = Path(file.filename).suffix.lower()  # 获取扩展名（如.jpg）
    if ext not in [".jpg", ".jpeg", ".png", ".gif"]:
        raise HTTPException(400, detail="不支持的图片扩展名")
    
    safe_filename = f"{uuid.uuid4()}{ext}"
    save_path = settings.cover_dir / safe_filename
    
    # 保存文件
    try:
        with open(save_path, "wb") as f:
            f.write(content)
    except Exception as e:
        raise HTTPException(500, detail=f"保存失败: {str(e)}")
    
    # 生成可访问的URL
    file_url = f"{settings.STATIC_URL_PREFIX}/covers/{safe_filename}"
    
    return {
        "code": 200,
        "message": "封面上传成功",
        "data": {
            "file_url": file_url,
            "original_name": file.filename
        }
    }

@file_router.post("/song")
async def upload_song(
    file: UploadFile = File(...),
    _: dict = Depends(require_admin)
):
    # 验证音频类型
    if file.content_type not in settings.allowed_audio_types_list:
        raise HTTPException(400, detail=f"仅支持音频: {', '.join(settings.allowed_audio_types_list)}")
    
    content = await file.read()
    if len(content) > settings.MAX_UPLOAD_SIZE * 2:
        raise HTTPException(400, detail="音频文件超过大小限制")
    
    # 安全扩展名
    ext = Path(file.filename).suffix.lower()
    if ext not in [".mp3", ".wav", ".ogg", ".m4a"]:
        raise HTTPException(400, detail="不支持的音频格式")
    
    safe_filename = f"{uuid.uuid4()}{ext}"
    save_path = settings.song_dir / safe_filename
    
    with open(save_path, "wb") as f:
        f.write(content)
    
    file_url = f"{settings.STATIC_URL_PREFIX}/songs/{safe_filename}"
    return {
        "code": 200,
        "message": "歌曲上传成功",
        "data": {"file_url": file_url, "original_name": file.filename}
    }

