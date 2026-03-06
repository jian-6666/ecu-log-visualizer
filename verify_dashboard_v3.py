#!/usr/bin/env python3
"""
Dashboard V3 验证脚本
快速检查所有组件是否正常工作
"""

import sys
import os
from pathlib import Path

def check_file_exists(filepath, description):
    """检查文件是否存在"""
    if Path(filepath).exists():
        print(f"✅ {description}: {filepath}")
        return True
    else:
        print(f"❌ {description} 缺失: {filepath}")
        return False

def check_import(module_name, description):
    """检查模块是否可以导入"""
    try:
        __import__(module_name)
        print(f"✅ {description} 可以导入")
        return True
    except Exception as e:
        print(f"❌ {description} 导入失败: {e}")
        return False

def main():
    print("=" * 60)
    print("Dashboard V3 完整性验证")
    print("=" * 60)
    
    all_checks = []
    
    # 检查前端文件
    print("\n📁 检查前端文件...")
    all_checks.append(check_file_exists("frontend/engineering-dashboard-v3.html", "V3 HTML"))
    all_checks.append(check_file_exists("frontend/engineering-dashboard-v3.css", "V3 CSS"))
    all_checks.append(check_file_exists("frontend/engineering-dashboard-v3.js", "V3 JavaScript"))
    
    # 检查文档文件
    print("\n📄 检查文档文件...")
    all_checks.append(check_file_exists("DASHBOARD_V3_USAGE.md", "使用指南"))
    all_checks.append(check_file_exists("DASHBOARD_V3_DEMO_SCRIPT.md", "演示脚本"))
    
    # 检查 CI/CD 配置
    print("\n⚙️ 检查 CI/CD 配置...")
    all_checks.append(check_file_exists(".github/workflows/ci.yml", "GitHub Actions"))
    all_checks.append(check_file_exists("Dockerfile", "Dockerfile"))
    
    # 检查测试文件
    print("\n🧪 检查测试配置...")
    all_checks.append(check_file_exists("pytest.ini", "Pytest 配置"))
    all_checks.append(check_file_exists("tests/__init__.py", "Tests __init__"))
    all_checks.append(check_file_exists("tests/unit/__init__.py", "Unit tests __init__"))
    all_checks.append(check_file_exists("tests/integration/__init__.py", "Integration tests __init__"))
    all_checks.append(check_file_exists("tests/property/__init__.py", "Property tests __init__"))
    
    # 检查后端模块
    print("\n🐍 检查后端模块...")
    all_checks.append(check_import("src.main", "主应用"))
    all_checks.append(check_import("src.git_integration", "Git 集成"))
    all_checks.append(check_import("src.cicd_status", "CI/CD 状态"))
    all_checks.append(check_import("src.docker_status", "Docker 状态"))
    
    # 检查依赖
    print("\n📦 检查关键依赖...")
    all_checks.append(check_import("fastapi", "FastAPI"))
    all_checks.append(check_import("pandas", "Pandas"))
    all_checks.append(check_import("pytest", "Pytest"))
    
    # 总结
    print("\n" + "=" * 60)
    passed = sum(all_checks)
    total = len(all_checks)
    success_rate = (passed / total) * 100
    
    print(f"验证结果: {passed}/{total} 通过 ({success_rate:.1f}%)")
    
    if passed == total:
        print("🎉 所有检查通过！Dashboard V3 已准备就绪。")
        return 0
    else:
        print(f"⚠️ 有 {total - passed} 项检查失败，请修复后再试。")
        return 1

if __name__ == "__main__":
    sys.exit(main())
