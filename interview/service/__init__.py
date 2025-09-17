"""
服务层软件包
- 提供对各个服务模块的统一访问入口
"""
from .forum import PostService,CommentService,NotificationService

# 定义包的公开接口
__all__ = ['PostService', 'CommentService', 'NotificationService']