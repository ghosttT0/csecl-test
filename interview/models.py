from django.db import models
import uuid
from django.utils import timezone
# from zhl.python_xiazaibao.Lib.email.policy import default


class Post(models.Model):
    """
    帖子模型
    - 存储论坛中的所有帖子
    - 使用字符字段存储用户标识
    """
    # 帖子内容字段
    title = models.CharField(max_length=200, verbose_name="帖子标题")  # 帖子标题，最大长度200字符
    content = models.TextField(verbose_name="帖子内容")  # 帖子内容，文本类型

    # 用户标识字段
    user_id = models.CharField(max_length=36, verbose_name="用户标识",null=True,blank=True)  # 用户唯一标识，存储在客户端

    # 帖子状态字段
    is_sticky = models.BooleanField(default=False, verbose_name="是否置顶")  # 是否置顶，默认为False
    comment_count = models.IntegerField(default=0, verbose_name="评论次数")  # 评论次数，默认为0

    # 时间字段
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")  # 创建时间，默认为当前时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")  # 更新时间，自动更新

    class Meta:
        db_table = 'interview_post'  # 数据库表名
        ordering = ['-is_sticky', '-created_at']  # 默认排序：先按置顶倒序，再按创建时间倒序

    def __str__(self):
        return f"{self.title} (by {self.user_id})"  # 对象字符串表示


class Comment(models.Model):
    """
    评论模型
    - 存储帖子的所有评论
    - 支持评论的回复功能（通过parent_comment_id实现）
    """
    # 关联字段（不使用物理外键）
    post_id = models.IntegerField(verbose_name="所属帖子ID")  # 所属帖子的ID
    user_id = models.CharField(max_length=36, verbose_name="评论者标识",null=True,blank=True)  # 评论者唯一标识

    # 评论内容字段
    content = models.TextField(max_length=1000, verbose_name="评论内容")  # 评论内容，最大长度1000字符

    # 父评论字段（用于实现回复功能）
    parent_comment_id = models.IntegerField(default=0, verbose_name="父评论ID")  # 父评论ID，0表示无父评论

    # 时间字段
    created_at = models.DateTimeField(default=timezone.now, verbose_name="创建时间")  # 创建时间，默认为当前时间
    updated_at = models.DateTimeField(auto_now=True, verbose_name="更新时间")  # 更新时间，自动更新

    class Meta:
        db_table = 'interview_comment'  # 数据库表名
        ordering = ['created_at']  # 默认按创建时间正序排列

    def __str__(self):
        return f"评论ID#{self.id} - 帖子ID#{self.post_id}"  # 对象字符串表示


class Notification(models.Model):
    """
    通知模型
    - 存储用户的通知信息
    - 支持回复通知和系统通知两种类型
    """
    # 接收者和发送者字段（不使用物理外键）
    recipient_user_id = models.CharField(max_length=36, verbose_name="接收通知用户标识",null=True,blank=True)  # 接收通知用户标识
    sender_user_id = models.CharField(max_length=36, blank=True, null=True,
                                      verbose_name="发送通知用户标识")  # 发送通知用户标识，可为空

    # 通知类型和内容字段
    NOTIFICATION_TYPES = (
        ('reply', '回复'),  # 回复通知
        ('system', '系统通知'),  # 系统通知
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        verbose_name="通知类型"
    )  # 通知类型，从预定义选项中选择

    message = models.CharField(max_length=200, verbose_name="通知消息内容")  # 通知消息内容，最大长度200字符

    # 状态字段
    is_read = models.BooleanField(default=False, verbose_name="是否已读")  # 是否已读，默认为False

    # 关联字段（可选，用于跳转到相关内容）
    post_id = models.IntegerField(blank=True, null=True, verbose_name="关联帖子ID")  # 关联帖子ID，可为空
    comment_id = models.IntegerField(blank=True, null=True, verbose_name="关联评论ID")  # 关联评论ID，可为空

    # 时间字段
    created_at = models.DateTimeField(default=timezone.now, verbose_name="通知时间")  # 通知时间，默认为当前时间

    class Meta:
        db_table = 'interview_notification'  # 数据库表名
        ordering = ['-created_at']  # 默认按通知时间倒序排列

    def __str__(self):
        return f"{self.notification_type}通知 - 接收者ID#{self.recipient_user_id}"  # 对象字符串表示


class Like(models.Model):
    """
    点赞模型
    - 支持对帖子或评论点赞（二选一）
    - 仅存储用户ID和目标ID，避免硬外键
    """
    user_id = models.CharField(max_length=36, verbose_name="点赞用户标识", null=True, blank=True)
    post_id = models.IntegerField(verbose_name="被点赞帖子ID", null=True, blank=True)
    comment_id = models.IntegerField(verbose_name="被点赞评论ID", null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now, verbose_name="点赞时间")

    class Meta:
        db_table = 'interview_like'
        # 同一用户对同一目标只能有一条点赞记录
        constraints = [
            models.UniqueConstraint(fields=['user_id', 'post_id'], name='uniq_user_post_like'),
            models.UniqueConstraint(fields=['user_id', 'comment_id'], name='uniq_user_comment_like'),
        ]

    def __str__(self):
        target = f"post#{self.post_id}" if self.post_id else f"comment#{self.comment_id}"
        return f"Like by {self.user_id} on {target}"


class StudentApplication(models.Model):
    # 字段定义（与数据库表字段对应）
    id = models.BigAutoField(primary_key=True, verbose_name="主键ID")
    name = models.CharField(max_length=255, verbose_name="学生姓名")
    number = models.CharField(max_length=255, verbose_name="学生学号")
    good_at = models.TextField(blank=True, null=True, verbose_name="擅长领域")
    grade = models.CharField(max_length=255, verbose_name="年级")
    major=models.CharField(max_length=255,verbose_name="专业班级",default="null")
    experience=models.TextField(blank=True,null=True,verbose_name="项目经历")
    other_lab=models.CharField(max_length=255,verbose_name="其他实验室报名情况")
    email= models.EmailField( null=True, verbose_name="邮箱")
    reason = models.TextField(blank=True, null=True, verbose_name="申请理由")
    value = models.CharField(max_length=255, blank=True, null=True, verbose_name="管理员评分")
    admin_remark = models.TextField(blank=True, null=True, verbose_name="管理员备注")
    book_time = models.DateTimeField( verbose_name="申请时间",default="2025-09-16")
    phone_number = models.CharField(max_length=255,verbose_name="联系电话",default="null")
    gaokao_math = models.IntegerField(verbose_name="高考数学成绩",default="null")  # 修改为整数类型
    gaokao_english = models.IntegerField(verbose_name="高考英语成绩",default="null")  # 修改为整数类型
    follow_direction = models.CharField(max_length=255, verbose_name="发展方向",default="null")
    future = models.CharField(max_length=255, verbose_name="未来规划",default="null")
    # 添加创建时间字段，用于排序
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="创建时间")

    class Meta:
        db_table = "book_user"  # 数据库中的表名
        verbose_name = "学生申请表"
        verbose_name_plural = "学生申请表"

    def __str__(self):
        return f"{self.name}({self.number})"  # 便于在管理后台识别
