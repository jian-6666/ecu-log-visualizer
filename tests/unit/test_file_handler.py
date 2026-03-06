"""
单元测试：FileHandler 文件处理模块

测试文件上传、验证、存储和管理功能。
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from io import BytesIO
from fastapi import UploadFile
from src.file_handler import FileHandler


@pytest.fixture
def temp_storage():
    """创建临时存储目录"""
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    # 清理临时目录
    shutil.rmtree(temp_dir)


@pytest.fixture
def file_handler(temp_storage):
    """创建 FileHandler 实例"""
    return FileHandler(storage_path=temp_storage)


def create_mock_upload_file(filename: str, content: bytes, content_type: str = "text/csv"):
    """创建模拟的 UploadFile 对象"""
    file_obj = BytesIO(content)
    return UploadFile(filename=filename, file=file_obj)


class TestFileValidation:
    """测试文件验证功能"""
    
    def test_validate_csv_file(self, file_handler):
        """测试验证有效的 CSV 文件"""
        file = create_mock_upload_file("test.csv", b"timestamp,sensor1\n2024-01-01,23.5")
        assert file_handler.validate_file(file) is True
    
    def test_validate_json_file(self, file_handler):
        """测试验证有效的 JSON 文件"""
        file = create_mock_upload_file("test.json", b'[{"timestamp": "2024-01-01"}]', "application/json")
        assert file_handler.validate_file(file) is True
    
    def test_validate_uppercase_extension(self, file_handler):
        """测试验证大写扩展名的文件"""
        file = create_mock_upload_file("test.CSV", b"data")
        assert file_handler.validate_file(file) is True
    
    def test_reject_invalid_extension(self, file_handler):
        """测试拒绝无效扩展名的文件"""
        file = create_mock_upload_file("test.txt", b"data", "text/plain")
        assert file_handler.validate_file(file) is False
    
    def test_reject_no_extension(self, file_handler):
        """测试拒绝没有扩展名的文件"""
        file = create_mock_upload_file("test", b"data")
        assert file_handler.validate_file(file) is False
    
    def test_reject_empty_filename(self, file_handler):
        """测试拒绝空文件名"""
        file = create_mock_upload_file("", b"data")
        assert file_handler.validate_file(file) is False
    
    def test_reject_oversized_file(self, file_handler):
        """测试拒绝超过大小限制的文件"""
        # 创建一个超过 50MB 的文件
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        file = create_mock_upload_file("large.csv", large_content)
        file.size = len(large_content)  # 设置 size 属性
        assert file_handler.validate_file(file) is False


class TestFileSaving:
    """测试文件保存功能"""
    
    def test_save_valid_csv_file(self, file_handler, temp_storage):
        """测试保存有效的 CSV 文件"""
        content = b"timestamp,sensor1\n2024-01-01,23.5"
        file = create_mock_upload_file("test.csv", content)
        
        file_id = file_handler.save_file(file)
        
        # 验证返回的是有效的 UUID
        assert file_id is not None
        assert len(file_id) == 36  # UUID 格式长度
        assert "-" in file_id
        
        # 验证文件已保存
        saved_path = Path(temp_storage) / f"{file_id}.csv"
        assert saved_path.exists()
        
        # 验证文件内容
        with open(saved_path, 'rb') as f:
            assert f.read() == content
    
    def test_save_valid_json_file(self, file_handler, temp_storage):
        """测试保存有效的 JSON 文件"""
        content = b'[{"timestamp": "2024-01-01", "sensor1": 23.5}]'
        file = create_mock_upload_file("test.json", content, "application/json")
        
        file_id = file_handler.save_file(file)
        
        # 验证文件已保存
        saved_path = Path(temp_storage) / f"{file_id}.json"
        assert saved_path.exists()
        
        # 验证文件内容
        with open(saved_path, 'rb') as f:
            assert f.read() == content
    
    def test_save_generates_unique_ids(self, file_handler):
        """测试每次保存生成唯一的文件 ID"""
        content = b"timestamp,sensor1\n2024-01-01,23.5"
        file1 = create_mock_upload_file("test.csv", content)
        file2 = create_mock_upload_file("test.csv", content)
        
        file_id1 = file_handler.save_file(file1)
        file_id2 = file_handler.save_file(file2)
        
        # 验证生成的 ID 不同
        assert file_id1 != file_id2
    
    def test_save_invalid_file_raises_error(self, file_handler):
        """测试保存无效文件时抛出异常"""
        file = create_mock_upload_file("test.txt", b"data", "text/plain")
        
        with pytest.raises(ValueError, match="Invalid file format or size"):
            file_handler.save_file(file)
    
    def test_save_oversized_file_raises_error(self, file_handler):
        """测试保存超大文件时抛出异常"""
        # 创建一个超过 50MB 的文件
        large_content = b"x" * (51 * 1024 * 1024)  # 51MB
        file = create_mock_upload_file("large.csv", large_content)
        
        with pytest.raises(ValueError, match="File size exceeds maximum limit"):
            file_handler.save_file(file)
    
    def test_save_preserves_file_extension(self, file_handler, temp_storage):
        """测试保存文件时保留原始扩展名"""
        csv_file = create_mock_upload_file("test.csv", b"data")
        json_file = create_mock_upload_file("test.json", b"data")
        
        csv_id = file_handler.save_file(csv_file)
        json_id = file_handler.save_file(json_file)
        
        # 验证扩展名被保留
        assert (Path(temp_storage) / f"{csv_id}.csv").exists()
        assert (Path(temp_storage) / f"{json_id}.json").exists()


class TestFileRetrieval:
    """测试文件检索功能"""
    
    def test_get_file_path_for_existing_file(self, file_handler):
        """测试获取已存在文件的路径"""
        content = b"timestamp,sensor1\n2024-01-01,23.5"
        file = create_mock_upload_file("test.csv", content)
        
        file_id = file_handler.save_file(file)
        file_path = file_handler.get_file_path(file_id)
        
        assert file_path.exists()
        assert file_path.name == f"{file_id}.csv"
    
    def test_get_file_path_for_json_file(self, file_handler):
        """测试获取 JSON 文件的路径"""
        content = b'[{"timestamp": "2024-01-01"}]'
        file = create_mock_upload_file("test.json", content, "application/json")
        
        file_id = file_handler.save_file(file)
        file_path = file_handler.get_file_path(file_id)
        
        assert file_path.exists()
        assert file_path.name == f"{file_id}.json"
    
    def test_get_file_path_for_nonexistent_file(self, file_handler):
        """测试获取不存在文件的路径时抛出异常"""
        with pytest.raises(FileNotFoundError, match="File with ID 'nonexistent-id' not found"):
            file_handler.get_file_path("nonexistent-id")


class TestFileDeletion:
    """测试文件删除功能"""
    
    def test_delete_existing_file(self, file_handler, temp_storage):
        """测试删除已存在的文件"""
        content = b"timestamp,sensor1\n2024-01-01,23.5"
        file = create_mock_upload_file("test.csv", content)
        
        file_id = file_handler.save_file(file)
        file_path = Path(temp_storage) / f"{file_id}.csv"
        
        # 验证文件存在
        assert file_path.exists()
        
        # 删除文件
        result = file_handler.delete_file(file_id)
        
        # 验证删除成功
        assert result is True
        assert not file_path.exists()
    
    def test_delete_nonexistent_file(self, file_handler):
        """测试删除不存在的文件返回 False"""
        result = file_handler.delete_file("nonexistent-id")
        assert result is False
    
    def test_delete_json_file(self, file_handler, temp_storage):
        """测试删除 JSON 文件"""
        content = b'[{"timestamp": "2024-01-01"}]'
        file = create_mock_upload_file("test.json", content, "application/json")
        
        file_id = file_handler.save_file(file)
        file_path = Path(temp_storage) / f"{file_id}.json"
        
        # 验证文件存在
        assert file_path.exists()
        
        # 删除文件
        result = file_handler.delete_file(file_id)
        
        # 验证删除成功
        assert result is True
        assert not file_path.exists()


class TestStorageDirectory:
    """测试存储目录管理"""
    
    def test_creates_storage_directory_if_not_exists(self):
        """测试如果存储目录不存在则自动创建"""
        temp_dir = tempfile.mkdtemp()
        storage_path = Path(temp_dir) / "new_uploads"
        
        try:
            # 验证目录不存在
            assert not storage_path.exists()
            
            # 创建 FileHandler
            handler = FileHandler(storage_path=str(storage_path))
            
            # 验证目录已创建
            assert storage_path.exists()
            assert storage_path.is_dir()
        finally:
            # 清理
            shutil.rmtree(temp_dir)
    
    def test_uses_existing_storage_directory(self, temp_storage):
        """测试使用已存在的存储目录"""
        # 在目录中创建一个文件
        test_file = Path(temp_storage) / "existing.txt"
        test_file.write_text("existing content")
        
        # 创建 FileHandler
        handler = FileHandler(storage_path=temp_storage)
        
        # 验证已存在的文件未被删除
        assert test_file.exists()
        assert test_file.read_text() == "existing content"
