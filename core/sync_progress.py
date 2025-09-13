"""
股票数据同步进度管理器
用于实时跟踪股票数据同步的进度
"""
import uuid
import threading
import time
from typing import Dict, Any, Optional
from datetime import datetime

class SyncProgressManager:
    """同步进度管理器"""
    
    def __init__(self):
        self.progress_data: Dict[str, Dict[str, Any]] = {}
        self.lock = threading.Lock()
    
    def create_session(self, sync_type: str, total_stocks: int) -> str:
        """创建新的同步会话"""
        session_id = str(uuid.uuid4())
        
        with self.lock:
            self.progress_data[session_id] = {
                'sync_type': sync_type,
                'total_stocks': total_stocks,
                'current_stock': 0,
                'current_symbol': '',
                'status': 'running',
                'message': '开始同步...',
                'start_time': datetime.now().isoformat(),
                'last_update': datetime.now().isoformat()
            }
        
        return session_id
    
    def update_progress(self, session_id: str, current_stock: int, current_symbol: str, message: str):
        """更新同步进度"""
        with self.lock:
            if session_id in self.progress_data:
                self.progress_data[session_id].update({
                    'current_stock': current_stock,
                    'current_symbol': current_symbol,
                    'message': message,
                    'last_update': datetime.now().isoformat(),
                    'percent': int((current_stock / self.progress_data[session_id]['total_stocks']) * 100)
                })
    
    def complete_sync(self, session_id: str, success_count: int, failed_count: int):
        """完成同步"""
        with self.lock:
            if session_id in self.progress_data:
                total = self.progress_data[session_id]['total_stocks']
                self.progress_data[session_id].update({
                    'status': 'completed',
                    'message': f'同步完成！成功: {success_count}, 失败: {failed_count}',
                    'last_update': datetime.now().isoformat(),
                    'percent': 100,
                    'total': total,
                    'success': success_count,
                    'failed': failed_count
                })
    
    def fail_sync(self, session_id: str, error_message: str):
        """同步失败"""
        with self.lock:
            if session_id in self.progress_data:
                self.progress_data[session_id].update({
                    'status': 'error',
                    'message': f'同步失败: {error_message}',
                    'last_update': datetime.now().isoformat()
                })
    
    def get_progress(self, session_id: str) -> Optional[Dict[str, Any]]:
        """获取同步进度"""
        with self.lock:
            return self.progress_data.get(session_id)
    
    def cleanup_old_sessions(self, max_age_hours: int = 24):
        """清理旧的会话"""
        with self.lock:
            current_time = datetime.now()
            to_remove = []
            
            for session_id, data in self.progress_data.items():
                start_time = datetime.fromisoformat(data['start_time'])
                if (current_time - start_time).total_seconds() > max_age_hours * 3600:
                    to_remove.append(session_id)
            
            for session_id in to_remove:
                del self.progress_data[session_id]

# 全局进度管理器实例
sync_progress_manager = SyncProgressManager()