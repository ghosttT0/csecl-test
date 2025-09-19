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

    # query by student name / number / result
    path('applications/by-name/', views.application_by_name, name='admin_application_by_name'),
    path('applications/result/', views.application_result_by_number, name='admin_application_result_by_number'),

    # announcements (only if feature exists)
    path('announcements/', views.publish_announcement, name='admin_publish_announcement'),
    # results release control
    path('results/release/', views.release_results, name='admin_results_release'),
    path('results/hide/', views.hide_results, name='admin_results_hide'),

    # forum admin
    path('forum/posts/', views.forum_posts, name='admin_forum_posts'),
    path('forum/posts/<int:post_id>/pin/', views.forum_post_pin, name='admin_forum_post_pin'),
    path('forum/posts/<int:post_id>/feature/', views.forum_post_feature, name='admin_forum_post_feature'),
    path('forum/posts/<int:post_id>/delete/', views.forum_post_delete, name='admin_forum_post_delete'),
]