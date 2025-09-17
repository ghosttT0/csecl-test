from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .service.forum import PostService, CommentService, NotificationService, LikeService
import uuid
from django.shortcuts import render
from .services import interview_services
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View  # 导入业务逻辑
from .models import StudentApplication


@api_view(['GET', 'POST'])
def post_list(request):
    """
    帖子列表API视图
    - GET: 获取帖子列表
    - POST: 创建新帖子
    """
    # 获取或创建用户标识
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        user_id = str(uuid.uuid4())

    if request.method == 'GET':
        # 获取查询参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 10)

        # 调用服务层获取帖子列表
        result = PostService.get_posts(page, page_size)

        # 返回响应
        return Response(result)

    elif request.method == 'POST':
        # 调用服务层创建帖子
        result = PostService.create_post(request.data, user_id)

        # 根据操作结果返回响应
        if result['success']:
            # 添加用户标识到响应中
            result['user_id'] = user_id
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def post_detail(request, pk):
    """
    帖子详情API视图
    - GET: 获取指定帖子的详细信息
    """
    # 调用服务层获取帖子详情
    result = PostService.get_post_detail(pk)

    # 根据操作结果返回响应
    if result['success']:
        return Response(result)
    else:
        return Response(result, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET', 'POST'])
def comment_list(request, post_id):
    """
    评论列表API视图
    - GET: 获取指定帖子的评论列表
    - POST: 为指定帖子创建新评论
    """
    # 获取或创建用户标识
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        user_id = str(uuid.uuid4())

    if request.method == 'GET':
        # 获取查询参数
        page = request.GET.get('page', 1)
        page_size = request.GET.get('page_size', 20)

        # 调用服务层获取评论列表
        result = CommentService.get_comments(post_id, page, page_size)

        # 返回响应
        return Response(result)

    elif request.method == 'POST':
        # 调用服务层创建评论
        result = CommentService.create_comment(post_id, request.data, user_id)

        # 根据操作结果返回响应
        if result['success']:
            # 添加用户标识到响应中
            result['user_id'] = user_id
            return Response(result, status=status.HTTP_201_CREATED)
        else:
            return Response(result, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def notification_list(request):
    """
    通知列表API视图
    - GET: 获取当前用户的通知列表
    """
    # 获取用户标识
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        # 如果没有用户标识，返回空列表
        return Response({
            'success': True,
            'data': [],
            'message': '未提供用户标识'
        })

    # 获取查询参数
    page = request.GET.get('page', 1)
    page_size = request.GET.get('page_size', 10)
    unread_only = request.GET.get('unread_only', 'false').lower() == 'true'

    # 调用服务层获取通知列表
    result = NotificationService.get_notifications(user_id, page, page_size, unread_only)

    # 返回响应
    return Response(result)


@api_view(['GET'])
def notification_unread_count(request):
    """
    未读通知计数API视图
    - GET: 返回当前用户的未读通知数量（包含广播）
    """
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return Response({'success': True, 'count': 0})
    count = NotificationService.get_unread_count(user_id)
    return Response({'success': True, 'count': count})


@api_view(['POST'])
def post_like_toggle(request, post_id):
    """帖子点赞/取消点赞"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return Response({'success': False, 'message': '未提供用户标识'}, status=status.HTTP_400_BAD_REQUEST)
    result = LikeService.toggle_like_post(post_id, user_id)
    status_code = status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND
    return Response(result, status=status_code)


@api_view(['POST'])
def comment_like_toggle(request, comment_id):
    """评论点赞/取消点赞"""
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return Response({'success': False, 'message': '未提供用户标识'}, status=status.HTTP_400_BAD_REQUEST)
    result = LikeService.toggle_like_comment(comment_id, user_id)
    status_code = status.HTTP_200_OK if result.get('success') else status.HTTP_404_NOT_FOUND
    return Response(result, status=status_code)


@api_view(['POST'])
def create_announcement(request):
    """创建公告（广播或定向）。简单版未接权限，后续可加。"""
    user_id = request.headers.get('X-User-ID')  # 作为 sender
    message = request.data.get('message')
    recipient_user_ids = request.data.get('recipient_user_ids')  # 可为 None 或 list[str]
    if not message:
        return Response({'success': False, 'message': 'message 不能为空'}, status=status.HTTP_400_BAD_REQUEST)
    if recipient_user_ids and not isinstance(recipient_user_ids, list):
        return Response({'success': False, 'message': 'recipient_user_ids 必须为数组'}, status=status.HTTP_400_BAD_REQUEST)
    result = NotificationService.create_announcement(message, recipient_user_ids, sender_user_id=user_id)
    return Response(result)


@api_view(['POST'])
def mark_notification_read(request, pk):
    """
    标记通知为已读API视图
    - POST: 将指定通知标记为已读
    """
    # 获取用户标识
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return Response({
            'success': False,
            'message': '未提供用户标识'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 调用服务层标记通知为已读
    result = NotificationService.mark_notification_read(pk, user_id)

    # 根据操作结果返回响应
    if result['success']:
        return Response(result)
    else:
        status_code = status.HTTP_404_NOT_FOUND if result['message'] == '通知不存在' else status.HTTP_403_FORBIDDEN
        return Response(result, status=status_code)


@api_view(['POST'])
def mark_all_notifications_read(request):
    """
    标记所有通知为已读API视图
    - POST: 将当前用户的所有通知标记为已读
    """
    # 获取用户标识
    user_id = request.headers.get('X-User-ID')
    if not user_id:
        return Response({
            'success': False,
            'message': '未提供用户标识'
        }, status=status.HTTP_400_BAD_REQUEST)

    # 调用服务层标记所有通知为已读
    result = NotificationService.mark_all_notifications_read(user_id)

    # 返回响应
    return Response(result)


# 学生提交申请的视图（页面 + 处理提交）
def application_form(request):
    # 处理POST请求（表单提交）
    if request.method == "POST":
        # 解析表单数据（适配Postman的form-data或x-www-form-urlencoded格式）
        data = {
            "name": request.POST.get("name"),
            "number": request.POST.get("number"),
            "grade": request.POST.get("grade"),
            "phone_number": request.POST.get("phone_number"),  # 前端参数为phone，映射到模型的phone_number
            "gaokao_math": request.POST.get("gaokao_math"),  # 前端参数为math，映射到模型的gaokao_math
            "gaokao_english": request.POST.get("gaokao_english"),  # 前端参数为english，映射到模型的gaokao_english
            "follow_direction": request.POST.get("follow_direction"),  # 前端参数为direction，映射到模型的follow_direction
            "good_at": request.POST.get("good_at"),
            "reason": request.POST.get("reason"),
            "book_time": request.POST.get("book_time"),
            "future":request.POST.get("future"),
            "email":request.POST.get("email"),
            "major":request.POST.get("major"),
            "other_lab":request.POST.get("other_lab"),
            "experience":request.POST.get("experience")

        }

        # 调用业务逻辑处理
        success, message = interview_services.submit_application(data)

        # 仅用于Postman测试：返回JSON响应,注意真正的在下面注释掉的
        return JsonResponse({
            "success": success,
            "message": message,
            "data": data  # 可选：返回提交的数据用于调试
        })

    # 处理GET请求（避免无返回值错误）
    return JsonResponse({
        "success": False,
        "message": "请使用POST方法提交申请",
        "method": request.method  # 显示当前请求方法，便于调试
    }, status=405)  # 405状态码表示方法不允许

        # 下面四行需与前端进行协商，故先注释
        # if success:
        #     return render(request, "success.html", {"message": message})
        # else:
        #     return render(request, "application_form.html", {"error": message})


# 管理员评分的 API 视图（JSON 接口）
class RateApplicationView(View):
    def post(self, request):
        app_id = request.POST.get("app_id")
        score = request.POST.get("score")

        success, message = interview_services.rate_application(app_id, score)
        return JsonResponse({"success": success, "message": message})


# 查询面试结果的视图
def application_list(request):
    student_number = request.POST.get("number")
    # if not student_number:
    #     return JsonResponse({
    #         "success": False,
    #         "message": "请提供正确的学号"
    #     })
    try:
        # 查看输入的学号是否正确
        StudentApplication.objects.get(number=student_number)
    except StudentApplication.DoesNotExist:
        return JsonResponse({
            "success": False,
            "message": "请输入正确的学号"
        })

    # 调用业务逻辑
    success, message = interview_services.get_applications(student_number)

    # 返回 JSON 响应
    return JsonResponse({
        "success": success,
        "message": message
    })