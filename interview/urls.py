from django.urls import path
from . import views

urlpatterns = [
    # 帖子相关API
    path('posts/', views.post_list, name='post_list'),  # 帖子列表和创建
    path('posts/<int:pk>/', views.post_detail, name='post_detail'),  # 帖子详情

    # 评论相关API
    path('posts/<int:post_id>/comments/', views.comment_list, name='comment_list'),  # 评论列表和创建

    # 通知相关API
    path('notifications/', views.notification_list, name='notification_list'),  # 通知列表
    path('notifications/<int:pk>/read/', views.mark_notification_read, name='mark_notification_read'),  # 标记单条通知为已读
    path('notifications/read-all/', views.mark_all_notifications_read, name='mark_all_notifications_read'),  # 标记所有通知为已读
    path('notifications/unread-count/', views.notification_unread_count, name='notification_unread_count'),  # 未读计数

    # 点赞相关API
    path('posts/<int:post_id>/like/', views.post_like_toggle, name='post_like_toggle'),
    path('comments/<int:comment_id>/like/', views.comment_like_toggle, name='comment_like_toggle'),

    # 公告/系统通知
    path('announcements/', views.create_announcement, name='create_announcement'),
# 提交相关api
    path("apply/", views.application_form, name="apply"),  # 申请表单
    path("rate/", views.RateApplicationView.as_view(), name="rate"),  # 评分接口
    path("list/", views.application_list, name="list"),  # 申请列表
]