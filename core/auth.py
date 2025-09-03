"""
用户管理模块
提供用户认证和会话管理功能
"""
import sqlite3
import hashlib
import secrets
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from functools import wraps
from flask import session, request, redirect, url_for, jsonify

from utils.logger import logger
from core.storage import db_manager


class UserManager:
    """用户管理器"""
    
    def __init__(self):
        self.db_path = db_manager.db_path
        logger.info("用户管理器初始化完成")
    
    def _hash_password(self, password: str) -> str:
        """密码哈希"""
        salt = secrets.token_hex(16)
        pwd_hash = hashlib.sha256((password + salt).encode()).hexdigest()
        return f"{salt}:{pwd_hash}"
    
    def _verify_password(self, password: str, password_hash: str) -> bool:
        """验证密码"""
        try:
            salt, pwd_hash = password_hash.split(':')
            return hashlib.sha256((password + salt).encode()).hexdigest() == pwd_hash
        except ValueError:
            return False
    
    def create_user(self, username: str, password: str, email: str = None, 
                   real_name: str = None, role: str = 'user') -> bool:
        """创建用户"""
        try:
            password_hash = self._hash_password(password)
            
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO users (username, password_hash, email, real_name, role)
                    VALUES (?, ?, ?, ?, ?)
                ''', (username, password_hash, email, real_name, role))
                
            logger.info(f"用户创建成功: {username}")
            return True
            
        except sqlite3.IntegrityError as e:
            logger.error(f"用户创建失败，用户名或邮箱已存在: {e}")
            return False
        except Exception as e:
            logger.error(f"用户创建失败: {e}")
            return False
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """用户认证"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM users 
                    WHERE username = ? AND is_active = 1
                ''', (username,))
                
                user = cursor.fetchone()
                
                if user and self._verify_password(password, user['password_hash']):
                    # 更新最后登录时间
                    conn.execute('''
                        UPDATE users SET last_login = CURRENT_TIMESTAMP 
                        WHERE id = ?
                    ''', (user['id'],))
                    
                    # 返回用户信息（不包含密码哈希）
                    return {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'real_name': user['real_name'],
                        'role': user['role'],
                        'created_at': user['created_at'],
                        'last_login': user['last_login']
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"用户认证失败: {e}")
            return None
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict[str, Any]]:
        """根据ID获取用户信息"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute('''
                    SELECT * FROM users 
                    WHERE id = ? AND is_active = 1
                ''', (user_id,))
                
                user = cursor.fetchone()
                
                if user:
                    return {
                        'id': user['id'],
                        'username': user['username'],
                        'email': user['email'],
                        'real_name': user['real_name'],
                        'role': user['role'],
                        'created_at': user['created_at'],
                        'last_login': user['last_login']
                    }
                
                return None
                
        except Exception as e:
            logger.error(f"获取用户信息失败: {e}")
            return None
    
    def create_session(self, user_id: int) -> str:
        """创建用户会话"""
        try:
            session_token = str(uuid.uuid4())
            expires_at = datetime.now() + timedelta(days=7)  # 7天过期
            
            with sqlite3.connect(self.db_path) as conn:
                # 清理过期会话
                conn.execute('''
                    UPDATE user_sessions SET is_active = 0 
                    WHERE user_id = ? AND expires_at < CURRENT_TIMESTAMP
                ''', (user_id,))
                
                # 创建新会话
                conn.execute('''
                    INSERT INTO user_sessions (user_id, session_token, expires_at)
                    VALUES (?, ?, ?)
                ''', (user_id, session_token, expires_at))
                
            logger.info(f"用户会话创建成功: user_id={user_id}")
            return session_token
            
        except Exception as e:
            logger.error(f"创建用户会话失败: {e}")
            return None
    
    def validate_session(self, session_token: str) -> Optional[int]:
        """验证会话"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT user_id FROM user_sessions 
                    WHERE session_token = ? AND is_active = 1 
                    AND expires_at > CURRENT_TIMESTAMP
                ''', (session_token,))
                
                result = cursor.fetchone()
                return result[0] if result else None
                
        except Exception as e:
            logger.error(f"验证会话失败: {e}")
            return None
    
    def revoke_session(self, session_token: str):
        """撤销会话"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    UPDATE user_sessions SET is_active = 0 
                    WHERE session_token = ?
                ''', (session_token,))
                
            logger.info("用户会话已撤销")
            
        except Exception as e:
            logger.error(f"撤销会话失败: {e}")
    
    def init_default_user(self):
        """初始化默认用户"""
        try:
            # 检查是否已有管理员用户
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.execute('''
                    SELECT COUNT(*) FROM users WHERE role = 'admin'
                ''')
                
                admin_count = cursor.fetchone()[0]
                
                if admin_count == 0:
                    # 创建默认管理员用户
                    self.create_user(
                        username='admin',
                        password='admin123',
                        email='admin@finance.com',
                        real_name='系统管理员',
                        role='admin'
                    )
                    logger.info("默认管理员用户已创建: admin/admin123")
                
                # 创建默认普通用户（用于演示）
                cursor = conn.execute('''
                    SELECT COUNT(*) FROM users WHERE username = 'demo'
                ''')
                
                demo_count = cursor.fetchone()[0]
                
                if demo_count == 0:
                    self.create_user(
                        username='demo',
                        password='demo123',
                        email='demo@finance.com',
                        real_name='演示用户',
                        role='user'
                    )
                    logger.info("默认演示用户已创建: demo/demo123")
                    
        except Exception as e:
            logger.error(f"初始化默认用户失败: {e}")


def login_required(f):
    """登录验证装饰器"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        # 检查session中是否有用户ID
        if 'user_id' not in session:
            if request.is_json:
                return jsonify({'code': 401, 'message': '请先登录'}), 401
            return redirect(url_for('login'))
        
        # 验证session token
        user_manager = UserManager()
        session_token = session.get('session_token')
        
        if not session_token or not user_manager.validate_session(session_token):
            session.clear()
            if request.is_json:
                return jsonify({'code': 401, 'message': '登录已过期，请重新登录'}), 401
            return redirect(url_for('login'))
        
        return f(*args, **kwargs)
    
    return decorated_function


def admin_required(f):
    """管理员权限验证装饰器"""
    @wraps(f)
    @login_required
    def decorated_function(*args, **kwargs):
        user_manager = UserManager()
        user_id = session.get('user_id')
        user = user_manager.get_user_by_id(user_id)
        
        if not user or user['role'] != 'admin':
            if request.is_json:
                return jsonify({'code': 403, 'message': '需要管理员权限'}), 403
            return redirect(url_for('dashboard'))
        
        return f(*args, **kwargs)
    
    return decorated_function


# 全局实例
user_manager = UserManager()