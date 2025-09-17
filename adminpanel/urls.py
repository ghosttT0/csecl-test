from django.urls import path
from . import views

urlpatterns = [
    # index
    path('', views.admin_index, name='admin_index'),

    # auth
    path('auth/login/', views.admin_login, name='admin_login'),
    path('auth/logout/', views.admin_logout, name='admin_logout'),

    # applications CRUD + extras
    path('applications/', views.application_list, name='admin_application_list'),
    path('applications/create/', views.application_create, name='admin_application_create'),
    path('applications/<int:app_id>/', views.application_detail, name='admin_application_detail'),
    path('applications/<int:app_id>/update/', views.application_update, name='admin_application_update'),
    path('applications/<int:app_id>/delete/', views.application_delete, name='admin_application_delete'),

    path('applications/<int:app_id>/score/', views.application_score, name='admin_application_score'),
    path('applications/<int:app_id>/remark/', views.application_remark, name='admin_application_remark'),

    # announcements (only if feature exists)
    path('announcements/', views.publish_announcement, name='admin_publish_announcement'),
]