
from rest_framework import serializers
from .models import Post, Comment, Notification

class PostSerializer(serializers.ModelSerializer):
    """
    帖子序列化器
    - 用于序列化和反序列化帖子数据
    """
    class Meta:
        model = Post  # 关联的模型
        fields = '__all__'  # 包含所有字段
        read_only_fields = ('id', 'created_at', 'updated_at', 'comment_count')  # 只读字段

class CommentSerializer(serializers.ModelSerializer):
    """
    评论序列化器
    - 用于序列化和反序列化评论数据
    """
    class Meta:
        model = Comment  # 关联的模型
        fields = '__all__'  # 包含所有字段
        read_only_fields = ('id', 'created_at', 'updated_at')  # 只读字段

class NotificationSerializer(serializers.ModelSerializer):
    """
    通知序列化器
    - 用于序列化和反序列化通知数据
    """
    class Meta:
        model = Notification  # 关联的模型
        fields = '__all__'  # 包含所有字段
        read_only_fields = ('id', 'created_at')  # 只读字段