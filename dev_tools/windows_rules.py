#!/usr/bin/env python3
"""
Windows 系统专用规则和命令执行工具
"""

import subprocess
import sys
import os
import platform
from utils.logger import logger

class WindowsRules:
    """Windows系统规则类"""
    
    @staticmethod
    def is_windows():
        """检查当前系统是否为Windows"""
        return platform.system().lower() == 'windows'
    
    @staticmethod
    def run_powershell_command(command):
        """
        执行PowerShell命令
        
        Args:
            command (str): PowerShell命令
            
        Returns:
            dict: 执行结果
        """
        if not WindowsRules.is_windows():
            raise EnvironmentError("此功能仅支持Windows系统")
        
        try:
            result = subprocess.run(
                ["powershell", "-Command", command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': '命令执行超时',
                'returncode': -1,
                'success': False
            }
        except Exception as e:
            logger.error(f"执行PowerShell命令失败: {e}")
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'success': False
            }
    
    @staticmethod
    def run_cmd_command(command):
        """
        执行CMD命令
        
        Args:
            command (str): CMD命令
            
        Returns:
            dict: 执行结果
        """
        if not WindowsRules.is_windows():
            raise EnvironmentError("此功能仅支持Windows系统")
        
        try:
            result = subprocess.run(
                ["cmd", "/c", command],
                capture_output=True,
                text=True,
                encoding='utf-8',
                timeout=30
            )
            return {
                'stdout': result.stdout,
                'stderr': result.stderr,
                'returncode': result.returncode,
                'success': result.returncode == 0
            }
        except subprocess.TimeoutExpired:
            return {
                'stdout': '',
                'stderr': '命令执行超时',
                'returncode': -1,
                'success': False
            }
        except Exception as e:
            logger.error(f"执行CMD命令失败: {e}")
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'success': False
            }
    
    @staticmethod
    def get_system_info():
        """
        获取Windows系统信息
        
        Returns:
            dict: 系统信息
        """
        if not WindowsRules.is_windows():
            raise EnvironmentError("此功能仅支持Windows系统")
        
        info = {}
        
        # 获取Windows版本
        result = WindowsRules.run_cmd_command("ver")
        if result['success']:
            info['version'] = result['stdout'].strip()
        
        # 获取系统架构
        result = WindowsRules.run_cmd_command("wmic os get osarchitecture")
        if result['success']:
            lines = result['stdout'].strip().split('\n')
            if len(lines) > 1:
                info['architecture'] = lines[1].strip()
        
        return info
    
    @staticmethod
    def check_python_environment():
        """
        检查Python环境
        
        Returns:
            dict: Python环境信息
        """
        info = {}
        info['python_version'] = sys.version
        info['python_executable'] = sys.executable
        info['working_directory'] = os.getcwd()
        info['python_path'] = os.environ.get('PYTHONPATH', '未设置')
        return info
    
    @staticmethod
    def setup_project_directories():
        """
        设置项目目录结构
        
        Returns:
            dict: 执行结果
        """
        try:
            # 导入项目目录设置
            setup_script = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'setup_dirs.py')
            if os.path.exists(setup_script):
                result = subprocess.run([sys.executable, setup_script], capture_output=True, text=True)
                return {
                    'stdout': result.stdout,
                    'stderr': result.stderr,
                    'returncode': result.returncode,
                    'success': result.returncode == 0
                }
            else:
                return {
                    'stdout': '',
                    'stderr': 'setup_dirs.py 文件不存在',
                    'returncode': -1,
                    'success': False
                }
        except Exception as e:
            return {
                'stdout': '',
                'stderr': str(e),
                'returncode': -1,
                'success': False
            }

# 常用Windows命令规则
WINDOWS_COMMAND_RULES = {
    "check_system": {
        "description": "检查Windows系统信息",
        "command": "systeminfo",
        "type": "cmd"
    },
    "check_python": {
        "description": "检查Python环境",
        "command": "python --version",
        "type": "cmd"
    },
    "check_pip": {
        "description": "检查pip版本",
        "command": "pip --version",
        "type": "cmd"
    },
    "list_processes": {
        "description": "列出正在运行的进程",
        "command": "tasklist",
        "type": "cmd"
    },
    "check_disk": {
        "description": "检查磁盘空间",
        "command": "wmic logicaldisk get size,freespace,caption",
        "type": "cmd"
    },
    "check_memory": {
        "description": "检查内存使用情况",
        "command": "wmic OS get TotalVisibleMemorySize /value",
        "type": "cmd"
    },
    "check_network": {
        "description": "检查网络配置",
        "command": "ipconfig",
        "type": "cmd"
    },
    "check_services": {
        "description": "检查系统服务",
        "command": "sc query",
        "type": "cmd"
    }
}

def execute_windows_rule(rule_name):
    """
    执行预定义的Windows命令规则
    
    Args:
        rule_name (str): 规则名称
        
    Returns:
        dict: 执行结果
    """
    if not WindowsRules.is_windows():
        return {
            'stdout': '',
            'stderr': '此功能仅支持Windows系统',
            'returncode': -1,
            'success': False
        }
    
    if rule_name not in WINDOWS_COMMAND_RULES:
        return {
            'stdout': '',
            'stderr': f'未知的规则: {rule_name}',
            'returncode': -1,
            'success': False
        }
    
    rule = WINDOWS_COMMAND_RULES[rule_name]
    command = rule['command']
    
    if rule['type'] == 'powershell':
        return WindowsRules.run_powershell_command(command)
    else:
        return WindowsRules.run_cmd_command(command)

if __name__ == "__main__":
    # 测试Windows规则
    print("🔧 Windows 系统规则测试")
    
    # 检查系统信息
    print("\n1. 系统信息:")
    system_info = WindowsRules.get_system_info()
    for key, value in system_info.items():
        print(f"   {key}: {value}")
    
    # 检查Python环境
    print("\n2. Python环境:")
    python_info = WindowsRules.check_python_environment()
    for key, value in python_info.items():
        print(f"   {key}: {value}")
    
    # 执行预定义规则示例
    print("\n3. 执行预定义规则:")
    result = execute_windows_rule("check_python")
    if result['success']:
        print(f"   Python版本: {result['stdout'].strip()}")
    else:
        print(f"   执行失败: {result['stderr']}")