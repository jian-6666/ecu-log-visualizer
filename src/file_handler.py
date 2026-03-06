"""
文件处理模块

该模块负责处理文件上传、验证、存储和管理。
"""

import uuid
from pathlib import Path
from typing import Optional
from fastapi import UploadFile


class FileHandler:
    """文件处理器类
    
    负责验证、保存、检索和删除上传的日志文件。
    """
    
    # 支持的文件格式
    ALLOWED_EXTENSIONS = {'.csv', '.json'}
    
    # 最大文件大小（50MB）
    MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB in bytes
    
    def __init__(self, storage_path: str = "uploads"):
        """初始化文件处理器
        
        Args:
            storage_path: 文件存储目录路径
        """
        self.storage_path = Path(storage_path)
        # 确保存储目录存在
        self.storage_path.mkdir(parents=True, exist_ok=True)
    
    def validate_file(self, file: UploadFile) -> bool:
        """验证文件格式和大小
        
        验证规则：
        - 文件格式必须是 .csv 或 .json
        - 文件大小不能超过 50MB
        
        Args:
            file: FastAPI UploadFile 对象
            
        Returns:
            bool: 验证通过返回 True，否则返回 False
            
        Validates: Requirements 1.2
        """
        # 验证文件名存在
        if not file.filename:
            return False
        
        # 验证文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        if file_ext not in self.ALLOWED_EXTENSIONS:
            return False
        
        # 验证文件大小
        # 注意：file.size 可能不总是可用，需要读取内容来检查
        if hasattr(file, 'size') and file.size is not None:
            if file.size > self.MAX_FILE_SIZE:
                return False
        
        return True
    
    def save_file(self, file: UploadFile) -> str:
        """保存文件并返回唯一文件 ID
        
        生成 UUID 作为文件 ID，保留原始文件扩展名。
        文件保存格式：{uuid}{original_extension}
        
        Args:
            file: FastAPI UploadFile 对象
            
        Returns:
            str: 生成的唯一文件 ID（UUID）
            
        Raises:
            ValueError: 如果文件验证失败
            IOError: 如果文件保存失败
            
        Validates: Requirements 1.3, 1.5
        """
        # 验证文件
        if not self.validate_file(file):
            raise ValueError("Invalid file format or size")
        
        # 生成唯一文件 ID
        file_id = str(uuid.uuid4())
        
        # 获取原始文件扩展名
        file_ext = Path(file.filename).suffix.lower()
        
        # 构建存储文件名
        stored_filename = f"{file_id}{file_ext}"
        file_path = self.storage_path / stored_filename
        
        # 保存文件
        try:
            # 读取文件内容
            content = file.file.read()
            
            # 再次验证文件大小（基于实际内容）
            if len(content) > self.MAX_FILE_SIZE:
                raise ValueError(f"File size exceeds maximum limit of {self.MAX_FILE_SIZE} bytes")
            
            # 写入文件
            with open(file_path, 'wb') as f:
                f.write(content)
            
            # 重置文件指针（以防后续需要再次读取）
            file.file.seek(0)
            
            return file_id
            
        except ValueError:
            # 重新抛出 ValueError（文件大小验证失败）
            raise
        except Exception as e:
            # 如果保存失败，清理可能创建的文件
            if file_path.exists():
                file_path.unlink()
            raise IOError(f"Failed to save file: {str(e)}")
    
    def get_file_path(self, file_id: str) -> Path:
        """根据文件 ID 获取文件路径
        
        Args:
            file_id: 文件的唯一标识符
            
        Returns:
            Path: 文件的完整路径
            
        Raises:
            FileNotFoundError: 如果文件不存在
            
        Validates: Requirements 1.3
        """
        # 尝试查找匹配的文件（可能是 .csv 或 .json）
        for ext in self.ALLOWED_EXTENSIONS:
            file_path = self.storage_path / f"{file_id}{ext}"
            if file_path.exists():
                return file_path
        
        # 如果没有找到文件，抛出异常
        raise FileNotFoundError(f"File with ID '{file_id}' not found")
    
    def delete_file(self, file_id: str) -> bool:
        """删除指定的文件
        
        Args:
            file_id: 文件的唯一标识符
            
        Returns:
            bool: 删除成功返回 True，文件不存在返回 False
            
        Validates: Requirements 1.4
        """
        try:
            file_path = self.get_file_path(file_id)
            file_path.unlink()
            return True
        except FileNotFoundError:
            return False
