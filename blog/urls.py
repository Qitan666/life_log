from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.post_list, name='post_list'),
    path('post/<int:pk>/', views.post_detail, name='post_detail'),
    path('post/create/', views.post_create, name='post_create'),
    path('post/<int:pk>/edit/', views.post_edit, name='post_edit'),
    path('post/<int:pk>/delete/', views.post_delete, name='post_delete'),

    path('post/<int:pk>/like/', views.toggle_like, name='toggle_like'),

    path('post/<int:pk>/comment/', views.comment_create, name='comment_create'),
    path('post/<int:pk>/comment/<int:comment_id>/edit/', views.comment_edit, name='comment_edit'),
    path('post/<int:pk>/comment/<int:comment_id>/delete/', views.comment_delete, name='comment_delete'),
]