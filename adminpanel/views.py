from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import login as dj_login, logout as dj_logout, authenticate
from django.core.paginator import Paginator
from interview.models import StudentApplication
from interview.service.forum import NotificationService
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
            'publish_announcement': '/admin/announcements/'
        }
    })


# --- Auth ---
@csrf_exempt
@require_http_methods(["POST"])
def admin_login(request):
    """Session login for admin users."""
    data = json.loads(request.body.decode('utf-8') or '{}')
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
            'phone_number': obj.phone_number,
            'gaokao_math': obj.gaokao_math,
            'gaokao_english': obj.gaokao_english,
            'follow_direction': obj.follow_direction,
            'good_at': obj.good_at,
            'reason': obj.reason,
            'future': obj.future,
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


# --- Applications: CRUD ---
@csrf_exempt
@require_http_methods(["POST"])
def application_create(request):
    """Create a new application (for admin data repair)."""
    not_logged = _require_login(request)
    if not_logged:
        return not_logged
    payload = json.loads(request.body.decode('utf-8') or '{}')
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
    payload = json.loads(request.body.decode('utf-8') or '{}')
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
        'phone_number': obj.phone_number,
        'gaokao_math': obj.gaokao_math,
        'gaokao_english': obj.gaokao_english,
        'follow_direction': obj.follow_direction,
        'good_at': obj.good_at,
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
    except Exception:
        payload = {}
    message = payload.get('message')
    recipient_user_ids = payload.get('recipient_user_ids')  # list[str] or None
    if not message:
        return JsonResponse({'success': False, 'message': 'message 不能为空'}, status=400)
    if recipient_user_ids and not isinstance(recipient_user_ids, list):
        return JsonResponse({'success': False, 'message': 'recipient_user_ids 必须为数组'}, status=400)

    result = NotificationService.create_announcement(message, recipient_user_ids, sender_user_id=str(request.user.id))
    return JsonResponse(result)