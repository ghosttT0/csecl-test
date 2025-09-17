from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.utils import timezone
from django.db.models import Q
from ..models import Post, Comment, Notification, Like
from ..serializers import PostSerializer, CommentSerializer, NotificationSerializer
import uuid


class PostService:
    """帖子相关服务"""

    @staticmethod
    def get_posts(page=1, page_size=10):
        """
        获取帖子列表
        :param page: 页码
        :param page_size: 每页数量
        :return: 分页后的帖子数据
        """
        posts = Post.objects.all().order_by('-is_sticky', '-created_at')
        paginator = Paginator(posts, page_size)

        try:
            posts_page = paginator.page(page)
        except PageNotAnInteger:
            posts_page = paginator.page(1)
        except EmptyPage:
            posts_page = paginator.page(paginator.num_pages)

        serializer = PostSerializer(posts_page, many=True)
        return {
            'data': serializer.data,
            'pagination': {
                'current_page': posts_page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': int(page_size)
            }
        }

    @staticmethod
    def create_post(data, user_id):
        """
        创建新帖子
        :param data: 帖子数据
        :param user_id: 用户ID
        :return: 创建结果
        """
        post_data = data.copy()
        post_data['user_id'] = user_id

        serializer = PostSerializer(data=post_data)
        if serializer.is_valid():
            post = serializer.save()
            return {
                'success': True,
                'message': '帖子创建成功',
                'data': serializer.data
            }

        return {
            'success': False,
            'message': '数据验证失败',
            'errors': serializer.errors
        }

    @staticmethod
    def get_post_detail(post_id):
        """
        获取帖子详情
        :param post_id: 帖子ID
        :return: 帖子详情或错误信息
        """
        try:
            post = Post.objects.get(pk=post_id)
            serializer = PostSerializer(post)
            return {
                'success': True,
                'data': serializer.data
            }
        except Post.DoesNotExist:
            return {
                'success': False,
                'message': '帖子不存在'
            }


class CommentService:
    """评论相关服务"""

    @staticmethod
    def get_comments(post_id, page=1, page_size=20):
        """
        获取评论列表
        :param post_id: 帖子ID
        :param page: 页码
        :param page_size: 每页数量
        :return: 分页后的评论数据
        """
        comments = Comment.objects.filter(post_id=post_id).order_by('created_at')
        paginator = Paginator(comments, page_size)

        try:
            comments_page = paginator.page(page)
        except PageNotAnInteger:
            comments_page = paginator.page(1)
        except EmptyPage:
            comments_page = paginator.page(paginator.num_pages)

        serializer = CommentSerializer(comments_page, many=True)
        return {
            'data': serializer.data,
            'pagination': {
                'current_page': comments_page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': int(page_size)
            }
        }

    @staticmethod
    def create_comment(post_id, data, user_id):
        """
        创建新评论
        :param post_id: 帖子ID
        :param data: 评论数据
        :param user_id: 用户ID
        :return: 创建结果
        """
        from ..models import Post  # 避免循环导入

        comment_data = data.copy()
        comment_data['post_id'] = post_id
        comment_data['user_id'] = user_id

        serializer = CommentSerializer(data=comment_data)
        if serializer.is_valid():
            comment = serializer.save()

            # 更新帖子评论计数
            try:
                post = Post.objects.get(pk=post_id)
                post.comment_count = Comment.objects.filter(post_id=post_id).count()
                post.save()

                # 处理通知
                NotificationService.create_comment_notification(comment, post, user_id)

            except Post.DoesNotExist:
                # 帖子不存在，但仍保存评论（这种情况不应该发生）
                pass

            return {
                'success': True,
                'message': '评论发表成功',
                'data': serializer.data
            }

        return {
            'success': False,
            'message': '数据验证失败',
            'errors': serializer.errors
        }


class NotificationService:
    """通知相关服务"""

    @staticmethod
    def get_notifications(user_id, page=1, page_size=10, unread_only=False):
        """
        获取通知列表
        :param user_id: 用户ID
        :param page: 页码
        :param page_size: 每页数量
        :param unread_only: 是否只获取未读通知
        :return: 分页后的通知数据
        """
        # 合并定向通知与广播通知（recipient_user_id 为空代表广播）
        notifications = Notification.objects.filter(
            Q(recipient_user_id=user_id) | Q(recipient_user_id__isnull=True)
        )

        if unread_only:
            notifications = notifications.filter(is_read=False)

        notifications = notifications.order_by('-created_at')
        paginator = Paginator(notifications, page_size)

        try:
            notifications_page = paginator.page(page)
        except PageNotAnInteger:
            notifications_page = paginator.page(1)
        except EmptyPage:
            notifications_page = paginator.page(paginator.num_pages)

        serializer = NotificationSerializer(notifications_page, many=True)
        return {
            'data': serializer.data,
            'pagination': {
                'current_page': notifications_page.number,
                'total_pages': paginator.num_pages,
                'total_items': paginator.count,
                'page_size': int(page_size)
            }
        }

    @staticmethod
    def create_comment_notification(comment, post, commenter_id):
        """
        创建评论相关通知
        :param comment: 评论对象
        :param post: 帖子对象
        :param commenter_id: 评论者ID
        """
        # 通知帖子作者（如果不是自己评论自己的帖子）
        if post.user_id != commenter_id:
            notification = Notification(
                recipient_user_id=post.user_id,
                sender_user_id=commenter_id,
                notification_type='reply',
                message=f"用户{commenter_id}评论了您的帖子《{post.title}》",
                post_id=post.id,
                comment_id=comment.id
            )
            notification.save()

        # 通知被回复的用户（如果有父评论且不是回复自己）
        parent_comment_id = comment.parent_comment_id
        if parent_comment_id and parent_comment_id > 0:
            try:
                parent_comment = Comment.objects.get(pk=parent_comment_id)
                if (parent_comment.user_id != commenter_id and
                        parent_comment.user_id != post.user_id):  # 避免重复通知帖子作者
                    notification = Notification(
                        recipient_user_id=parent_comment.user_id,
                        sender_user_id=commenter_id,
                        notification_type='reply',
                        message=f"用户{commenter_id}回复了您的评论",
                        post_id=post.id,
                        comment_id=comment.id
                    )
                    notification.save()
            except Comment.DoesNotExist:
                # 父评论不存在，忽略
                pass

    @staticmethod
    def mark_notification_read(notification_id, user_id):
        """
        标记通知为已读
        :param notification_id: 通知ID
        :param user_id: 用户ID
        :return: 操作结果
        """
        try:
            notification = Notification.objects.get(pk=notification_id)

            # 检查用户是否有权限操作此通知
            if notification.recipient_user_id != user_id:
                return {
                    'success': False,
                    'message': '无权操作此通知'
                }

            # 标记通知为已读
            notification.is_read = True
            notification.save()

            return {
                'success': True,
                'message': '通知已标记为已读'
            }

        except Notification.DoesNotExist:
            return {
                'success': False,
                'message': '通知不存在'
            }

    @staticmethod
    def mark_all_notifications_read(user_id):
        """
        标记所有通知为已读
        :param user_id: 用户ID
        :return: 操作结果
        """
        # 获取用户的所有未读通知
        notifications = Notification.objects.filter(
            recipient_user_id=user_id,
            is_read=False
        )

        # 标记所有通知为已读
        updated_count = notifications.update(is_read=True)

        return {
            'success': True,
            'message': f'已标记{updated_count}条通知为已读'
        }

    @staticmethod
    def create_announcement(message, recipient_user_ids=None, sender_user_id=None):
        """
        创建公告/系统通知
        - recipient_user_ids=None 表示广播
        - 否则为定向通知
        """
        created = 0
        if not recipient_user_ids:
            notif = Notification(
                recipient_user_id=None,
                sender_user_id=sender_user_id,
                notification_type='announcement',
                message=message,
            )
            notif.save()
            created = 1
        else:
            for rid in recipient_user_ids:
                notif = Notification(
                    recipient_user_id=rid,
                    sender_user_id=sender_user_id,
                    notification_type='announcement',
                    message=message,
                )
                notif.save()
                created += 1
        return {
            'success': True,
            'message': f'创建公告成功，共创建{created}条',
            'created': created
        }

    @staticmethod
    def get_unread_count(user_id):
        """获取未读通知数量（仅统计定向给用户的通知，广播不计入未读）"""
        return Notification.objects.filter(
            Q(recipient_user_id=user_id) & Q(is_read=False)
        ).count()


class LikeService:
    """点赞相关服务"""

    @staticmethod
    def toggle_like_post(post_id, user_id):
        try:
            post = Post.objects.get(pk=post_id)
        except Post.DoesNotExist:
            return {'success': False, 'message': '帖子不存在'}

        like = Like.objects.filter(user_id=user_id, post_id=post_id).first()
        if like:
            like.delete()
            return {'success': True, 'liked': False, 'message': '已取消点赞'}
        else:
            Like.objects.create(user_id=user_id, post_id=post_id)
            # 不是自己给自己点赞时发送通知
            if post.user_id and post.user_id != user_id:
                Notification.objects.create(
                    recipient_user_id=post.user_id,
                    sender_user_id=user_id,
                    notification_type='like',
                    message=f"用户{user_id}赞了您的帖子《{post.title}》",
                    post_id=post.id,
                )
            return {'success': True, 'liked': True, 'message': '点赞成功'}

    @staticmethod
    def toggle_like_comment(comment_id, user_id):
        try:
            comment = Comment.objects.get(pk=comment_id)
        except Comment.DoesNotExist:
            return {'success': False, 'message': '评论不存在'}

        like = Like.objects.filter(user_id=user_id, comment_id=comment_id).first()
        if like:
            like.delete()
            return {'success': True, 'liked': False, 'message': '已取消点赞'}
        else:
            Like.objects.create(user_id=user_id, comment_id=comment_id)
            # 不是自己给自己点赞时发送通知
            if comment.user_id and comment.user_id != user_id:
                Notification.objects.create(
                    recipient_user_id=comment.user_id,
                    sender_user_id=user_id,
                    notification_type='like',
                    message=f"用户{user_id}赞了您的评论",
                    post_id=comment.post_id,
                    comment_id=comment.id,
                )
            return {'success': True, 'liked': True, 'message': '点赞成功'}

    @staticmethod
    def mark_notification_read(notification_id, user_id):
        """
        标记通知为已读
        :param notification_id: 通知ID
        :param user_id: 用户ID
        :return: 操作结果
        """
        try:
            notification = Notification.objects.get(pk=notification_id)

            # 检查用户是否有权限操作此通知
            if notification.recipient_user_id != user_id:
                return {
                    'success': False,
                    'message': '无权操作此通知'
                }

            # 标记通知为已读
            notification.is_read = True
            notification.save()

            return {
                'success': True,
                'message': '通知已标记为已读'
            }

        except Notification.DoesNotExist:
            return {
                'success': False,
                'message': '通知不存在'
            }

    @staticmethod
    def mark_all_notifications_read(user_id):
        """
        标记所有通知为已读
        :param user_id: 用户ID
        :return: 操作结果
        """
        # 获取用户的所有未读通知
        notifications = Notification.objects.filter(
            recipient_user_id=user_id,
            is_read=False
        )

        # 标记所有通知为已读
        updated_count = notifications.update(is_read=True)

        return {
            'success': True,
            'message': f'已标记{updated_count}条通知为已读'
        }