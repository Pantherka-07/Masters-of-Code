from django.urls import path
from . import views
from .views import stats_view

urlpatterns = [
    path('', views.login_view, name='index'),
    path('logout/', views.logout_view, name='logout'),
    path('tasks/', views.tasks_view, name='tasks'),
    path('tasks/create/', views.task_create, name='task_create'),
    path('tasks/<int:pk>/update/', views.task_update, name='task_update'),
    path('tasks/<int:pk>/delete/', views.task_delete, name='task_delete'),
    path('tasks/<int:pk>/complete/', views.task_complete, name='task_complete'),
    path('tasks/<int:pk>/close/', views.task_close, name='task_close'),
    path('register/', views.register_view, name='register'),
    path('friends/', views.friends_list, name='friends'),
    path('friends/add/', views.add_friend, name='add_friend'),
    path('friends/remove/<int:user_id>/', views.remove_friend, name='remove_friend'),
    path('profile/', views.profile_view, name='profile'),
    path('stats/', stats_view, name='stats'),
    path('settings/', views.settings_view, name='settings'),
]
