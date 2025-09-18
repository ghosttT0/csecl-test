"""
URL configuration for CSECL project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.contrib import admin
from django.urls import path, include
from django.views.generic import RedirectView
from django.views.static import serve as static_serve
from django.conf import settings
from django.http import JsonResponse

def home_view(request):
    return JsonResponse({
        'message': 'CSECL 后端服务',
        'endpoints': {
            'admin': '/admin/',
            'interview': '/interview/',
            'django_admin': '/djadmin/'
        }
    })

urlpatterns = [
    # 将根路径与常用页面重定向到静态页面（由 WhiteNoise 在 /static/ 下提供）
    path("", RedirectView.as_view(url='/static/index.html', permanent=False), name='home'),
    path("index.html", RedirectView.as_view(url='/static/index.html', permanent=False)),
    path("apps.html", RedirectView.as_view(url='/static/apps.html', permanent=False)),
    path("announce.html", RedirectView.as_view(url='/static/announce.html', permanent=False)),
    path("forum.html", RedirectView.as_view(url='/static/forum.html', permanent=False)),
    path("detail.html", RedirectView.as_view(url='/static/detail.html', permanent=False)),
    # 兼容误访问 /admin/*.html，跳到静态页
    path("admin/index.html", RedirectView.as_view(url='/static/index.html', permanent=False)),
    path("admin/apps.html", RedirectView.as_view(url='/static/apps.html', permanent=False)),
    path("admin/announce.html", RedirectView.as_view(url='/static/announce.html', permanent=False)),
    path("admin/forum.html", RedirectView.as_view(url='/static/forum.html', permanent=False)),
    path("admin/detail.html", RedirectView.as_view(url='/static/detail.html', permanent=False)),
    path("djadmin/", admin.site.urls),

    # path('user/', include('user.urls')),
    path('interview/', include('interview.urls')),
    # path('class/', include('class.urls')),

    # mount custom admin API under /admin
    path('admin', RedirectView.as_view(url='/admin/', permanent=False)),
    path('admin/', include('adminpanel.urls')),

]
