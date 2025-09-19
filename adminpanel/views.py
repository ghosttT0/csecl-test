from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as dj_login, logout as dj_logout, authenticate
from django.core.paginator import Paginator
from interview.models import StudentApplication
from interview.models import Post
from interview.service.forum import NotificationService
from interview.services import interview_services
from django.core.cache import cache
import json


@require_http_methods(["GET"])
def admin_index(request):
    return JsonResponse({
        'success': True,
        'message': 'Admin API index',
        'endpoints': {
            'login': '/admin/auth/login/',
            'logout': '/admin/auth/logout/',
            'applications_list': '/admin/applications/',
            'applications_create': '/admin/applications/create/',
            'application_detail': '/admin/applications/<id>/',
            'application_update': '/admin/applications/<id>/update/',
            'application_delete': '/admin/applications/<id>/delete/',
            'application_score': '/admin/applications/<id>/score/',
            'application_remark': '/admin/applications/<id>/remark/',
            'application_by_name': '/admin/applications/by-name/?name=张三',
            'application_result_by_number': '/admin/applications/result/?number=2025xxxxxx',
            'publish_announcement': '/admin/announcements/',
            'forum_posts': '/admin/forum/posts/',
            'forum_post_pin': '/admin/forum/posts/<id>/pin/',
            'forum_post_feature': '/admin/forum/posts/<id>/feature/',
            'forum_post_delete': '/admin/forum/posts/<id>/delete/'
        }
    })


# --- Auth ---
@csrf_exempt
@require_http_methods(["POST"])
def admin_login(request):
    """Session login for admin users."""
    try:
        data = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '请求数据格式错误，需要有效的 JSON'}, status=400)
    username = data.get('username')
    password = data.get('password')
    user = authenticate(request, username=username, password=password)
    if user is None:
        return JsonResponse({"success": False, "message": "用户名或密码错误"}, status=401)
    dj_login(request, user)
    return JsonResponse({"success": True, "message": "登录成功"})


@require_http_methods(["POST"])
def admin_logout(request):
    """Logout current admin session."""
    dj_logout(request)
    return JsonResponse({"success": True, "message": "已退出登录"})


def _require_login(request):
    if not getattr(request, 'user', None) or not request.user.is_authenticated:
        return JsonResponse({"success": False, "message": "未登录"}, status=401)
    return None
# --- Forum admin: list & actions ---
@require_http_methods(["GET"])
def forum_posts(request):
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    # 简单分页
    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    qs = Post.objects.all().order_by('-is_sticky', '-is_featured', '-created_at')
    from django.core.paginator import Paginator
    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)
    data = [{
        'id': p.id,
        'title': p.title,
        'user_id': p.user_id,
        'is_sticky': p.is_sticky,
        'is_featured': getattr(p, 'is_featured', False),
        'comment_count': p.comment_count,
        'created_at': p.created_at,
    } for p in page_obj.object_list]
    return JsonResponse({'success': True, 'data': data, 'pagination': {
        'current_page': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_items': paginator.count,
        'page_size': page_size,
    }})


@csrf_exempt
@require_http_methods(["POST"])
def forum_post_pin(request, post_id: int):
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        post = Post.objects.get(id=post_id)
        post.is_sticky = not post.is_sticky
        post.save()
        return JsonResponse({'success': True, 'is_sticky': post.is_sticky})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': '帖子不存在'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def forum_post_feature(request, post_id: int):
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        post = Post.objects.get(id=post_id)
        if hasattr(post, 'is_featured'):
            post.is_featured = not post.is_featured
            post.save()
            return JsonResponse({'success': True, 'is_featured': post.is_featured})
        return JsonResponse({'success': False, 'message': '未支持加精字段'}, status=400)
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': '帖子不存在'}, status=404)


@csrf_exempt
@require_http_methods(["POST"])
def forum_post_delete(request, post_id: int):
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        post = Post.objects.get(id=post_id)
        post.delete()
        return JsonResponse({'success': True})
    except Post.DoesNotExist:
        return JsonResponse({'success': False, 'message': '帖子不存在'}, status=404)


# --- Applications: Read list ---
@require_http_methods(["GET"])
def application_list(request):
    """List applications with simple filters and pagination."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged

    page = int(request.GET.get('page', 1))
    page_size = int(request.GET.get('page_size', 10))
    keyword = request.GET.get('keyword', '').strip()
    direction = request.GET.get('direction')
    grade = request.GET.get('grade')

    qs = StudentApplication.objects.all().order_by('-created_at')
    if keyword:
        qs = qs.filter(number__icontains=keyword)
    if direction:
        qs = qs.filter(follow_direction__icontains=direction)
    if grade:
        qs = qs.filter(grade=grade)

    paginator = Paginator(qs, page_size)
    page_obj = paginator.get_page(page)

    def to_dict(obj: StudentApplication):
        return {
            'id': obj.id,
            'name': obj.name,
            'number': obj.number,
            'grade': obj.grade,
            'major': obj.major,
            'phone_number': obj.phone_number,
            'email': getattr(obj, 'email', None),
            'gaokao_math': obj.gaokao_math,
            'gaokao_english': obj.gaokao_english,
            'follow_direction': obj.follow_direction,
            'good_at': obj.good_at,
            'reason': obj.reason,
            'future': obj.future,
            'experience': getattr(obj, 'experience', None),
            'other_lab': getattr(obj, 'other_lab', None),
            'value': obj.value,
            'admin_remark': getattr(obj, 'admin_remark', None),
            'book_time': obj.book_time,
            'created_at': obj.created_at,
        }

    data = [to_dict(x) for x in page_obj.object_list]
    return JsonResponse({
        'success': True,
        'data': data,
        'pagination': {
            'current_page': page_obj.number,
            'total_pages': paginator.num_pages,
            'total_items': paginator.count,
            'page_size': page_size
        }
    })


# --- Applications: Query by name ---
@require_http_methods(["GET"])
def application_by_name(request):
    """Query applications by exact or fuzzy student name."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged

    name = (request.GET.get('name') or '').strip()
    if not name:
        return JsonResponse({'success': False, 'message': 'name 不能为空'}, status=400)

    qs = StudentApplication.objects.filter(name__icontains=name).order_by('-created_at')

    def to_dict(obj: StudentApplication):
        return {
            'id': obj.id,
            'name': obj.name,
            'number': obj.number,
            'grade': obj.grade,
            'major': obj.major,
            'phone_number': obj.phone_number,
            'email': getattr(obj, 'email', None),
            'gaokao_math': obj.gaokao_math,
            'gaokao_english': obj.gaokao_english,
            'follow_direction': obj.follow_direction,
            'good_at': obj.good_at,
            'reason': obj.reason,
            'future': obj.future,
            'experience': getattr(obj, 'experience', None),
            'other_lab': getattr(obj, 'other_lab', None),
            'value': obj.value,
            'admin_remark': getattr(obj, 'admin_remark', None),
            'book_time': obj.book_time,
            'created_at': obj.created_at,
        }

    data = [to_dict(x) for x in qs]
    return JsonResponse({'success': True, 'data': data})


# --- Applications: Result by number (reuse interview_services) ---
@require_http_methods(["GET"])
def application_result_by_number(request):
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    number = (request.GET.get('number') or '').strip()
    if not number:
        return JsonResponse({'success': False, 'message': 'number 不能为空'}, status=400)
    ok, message = interview_services.get_applications(number)
    return JsonResponse({'success': bool(ok), 'message': message})


# --- Applications: CRUD ---
@csrf_exempt
@require_http_methods(["POST"])
def application_create(request):
    """Create a new application (for admin data repair)."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '请求数据格式错误，需要有效的 JSON'}, status=400)
    obj = StudentApplication.objects.create(
        name=payload.get('name') or '',
        number=payload.get('number') or '',
        grade=payload.get('grade') or '',
        phone_number=payload.get('phone_number') or '',
        gaokao_math=int(payload.get('gaokao_math') or 0),
        gaokao_english=int(payload.get('gaokao_english') or 0),
        follow_direction=payload.get('follow_direction') or '',
        good_at=payload.get('good_at') or '',
        reason=payload.get('reason') or '',
        future=payload.get('future') or '',
        value=str(payload.get('value') or ''),
        admin_remark=payload.get('admin_remark') or '',
    )
    return JsonResponse({'success': True, 'id': obj.id})


@csrf_exempt
@require_http_methods(["POST"])
def application_update(request, app_id: int):
    """Update fields of an application."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        obj = StudentApplication.objects.get(id=app_id)
    except StudentApplication.DoesNotExist:
        return JsonResponse({'success': False, 'message': '记录不存在'}, status=404)
    
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '请求数据格式错误，需要有效的 JSON'}, status=400)
    for field in ['name','number','grade','phone_number','follow_direction','good_at','reason','future','value','admin_remark']:
        if field in payload:
            setattr(obj, field, payload.get(field) or '')
    if 'gaokao_math' in payload:
        obj.gaokao_math = int(payload.get('gaokao_math') or 0)
    if 'gaokao_english' in payload:
        obj.gaokao_english = int(payload.get('gaokao_english') or 0)
    obj.save()
    return JsonResponse({'success': True})


@csrf_exempt
@require_http_methods(["POST"])
def application_delete(request, app_id: int):
    """Delete an application."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        StudentApplication.objects.get(id=app_id).delete()
        return JsonResponse({'success': True})
    except StudentApplication.DoesNotExist:
        return JsonResponse({'success': False, 'message': '记录不存在'}, status=404)


# --- Applications: Detail ---
@require_http_methods(["GET"])
def application_detail(request, app_id: int):
    """Get single application details."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        obj = StudentApplication.objects.get(id=app_id)
    except StudentApplication.DoesNotExist:
        return JsonResponse({'success': False, 'message': '记录不存在'}, status=404)

    return JsonResponse({'success': True, 'data': {
        'id': obj.id,
        'name': obj.name,
        'number': obj.number,
        'grade': obj.grade,
        'major': getattr(obj, 'major', None),
        'phone_number': obj.phone_number,
        'gaokao_math': obj.gaokao_math,
        'gaokao_english': obj.gaokao_english,
        'follow_direction': obj.follow_direction,
        'good_at': obj.good_at,
        'email': getattr(obj, 'email', None),
        'other_lab': getattr(obj, 'other_lab', None),
        'experience': getattr(obj, 'experience', None),
        'reason': obj.reason,
        'future': obj.future,
        'value': obj.value,
        'admin_remark': getattr(obj, 'admin_remark', None),
        'book_time': obj.book_time,
        'created_at': obj.created_at,
    }})


# --- Applications: Score & Remark ---
@csrf_exempt
@require_http_methods(["POST"])
def application_score(request, app_id: int):
    """Set score 1-100."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        obj = StudentApplication.objects.get(id=app_id)
    except StudentApplication.DoesNotExist:
        return JsonResponse({'success': False, 'message': '记录不存在'}, status=404)

    score = request.POST.get('score')
    if score is None and request.body:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
            score = payload.get('score')
        except Exception:
            score = None
    if not (str(score).isdigit() and 1 <= int(score) <= 100):
        return JsonResponse({'success': False, 'message': '评分必须是1-100的数字'}, status=400)
    obj.value = str(score)
    obj.save()
    return JsonResponse({'success': True, 'message': '评分成功'})


@csrf_exempt
@require_http_methods(["POST"])
def application_remark(request, app_id: int):
    """Update admin remark text."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        obj = StudentApplication.objects.get(id=app_id)
    except StudentApplication.DoesNotExist:
        return JsonResponse({'success': False, 'message': '记录不存在'}, status=404)

    remark = request.POST.get('remark')
    if remark is None and request.body:
        try:
            payload = json.loads(request.body.decode('utf-8') or '{}')
            remark = payload.get('remark')
        except Exception:
            remark = ''
    obj.admin_remark = remark or ''
    obj.save()
    return JsonResponse({'success': True, 'message': '备注已保存'})


# --- Announcements ---
@csrf_exempt
@require_http_methods(["POST"])
def publish_announcement(request):
    """Publish broadcast or targeted announcements via NotificationService."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    try:
        payload = json.loads(request.body.decode('utf-8') or '{}')
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': '请求数据格式错误，需要有效的 JSON'}, status=400)
    message = payload.get('message')
    recipient_user_ids = payload.get('recipient_user_ids')  # list[str] or None
    if not message:
        return JsonResponse({'success': False, 'message': 'message 不能为空'}, status=400)
    if recipient_user_ids and not isinstance(recipient_user_ids, list):
        return JsonResponse({'success': False, 'message': 'recipient_user_ids 必须为数组'}, status=400)

    result = NotificationService.create_announcement(message, recipient_user_ids, sender_user_id=str(request.user.id))
    return JsonResponse(result)


# --- Results release control ---
@csrf_exempt
@require_http_methods(["POST"])
def release_results(request):
    """Mark interview results as released so students can query."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    cache.set('interview_results_released', True, None)
    return JsonResponse({'success': True, 'message': '已发布面试结果'})


@csrf_exempt
@require_http_methods(["POST"])
def hide_results(request):
    """Hide interview results until admin releases them."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    cache.set('interview_results_released', False, None)
    return JsonResponse({'success': True, 'message': '已隐藏面试结果'})