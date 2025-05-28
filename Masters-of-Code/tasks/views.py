from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Task
from .forms import TaskForm
from django.contrib.auth.models import User
from django import forms
from django.db import models as dj_models
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.core.mail import send_mail
from django.db import models
from django.db.models import Count, Sum
import uuid

User = get_user_model()

def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('tasks')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, "tasks/index.html", {'no_sakura_bg': True})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def tasks_view(request):
    status = request.GET.get('status', 'active')
    tasks_qs = Task.objects.filter(user=request.user)
    if status == 'completed':
        tasks = tasks_qs.filter(is_completed=True, is_closed=False)
    elif status == 'closed':
        tasks = tasks_qs.filter(is_closed=True)
    else:  # active
        tasks = tasks_qs.filter(is_completed=False, is_closed=False)
    # Суммарная оценка за все завершённые задачи
    total_points = tasks_qs.filter(is_completed=True).aggregate(points_sum=models.Sum('points'))['points_sum'] or 0
    context = {'tasks': tasks, 'status': status, 'total_points': total_points}
    return render(request, "tasks/tasks.html", context)

@login_required
def task_create(request):
    if request.method == 'POST':
        form = TaskForm(request.POST, user=request.user)
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            form.save_m2m()
            if task.notification_method == 'email' and request.user.email:
                send_mail(
                    subject=f'Напоминание о задаче: {task.title}',
                    message=f'Вам назначена задача: {task.title}\n\nОписание: {task.description}\nВыполнить до: {task.due_date}',
                    from_email=None,
                    recipient_list=[request.user.email],
                    fail_silently=True,
                )
            return redirect('tasks')
    else:
        form = TaskForm(user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_update(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        form = TaskForm(request.POST, instance=task, user=request.user)
        if form.is_valid():
            form.save()
            return redirect('tasks')
    else:
        form = TaskForm(instance=task, user=request.user)
    return render(request, 'tasks/task_form.html', {'form': form})

@login_required
def task_delete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.delete()
        status = request.GET.get('status')
        if status:
            return redirect(f'/tasks/?status={status}')
        return redirect('tasks')
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def task_complete(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.is_completed = True
        task.save()
    return redirect(f'{request.META.get("HTTP_REFERER", "/tasks/")}')

@login_required
def task_close(request, pk):
    task = get_object_or_404(Task, pk=pk, user=request.user)
    if request.method == 'POST':
        task.is_closed = True
        task.save()
    return redirect(f'{request.META.get("HTTP_REFERER", "/tasks/")}')

class RegisterForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Пароль')
    password2 = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}), label='Повторите пароль')
    class Meta:
        model = User
        fields = ('username', 'email')
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password2')
        if password and password2 and password != password2:
            self.add_error('password2', 'Пароли не совпадают')
        return cleaned_data

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            if not user.invite_id:
                user.invite_id = uuid.uuid4().hex[:16]
            user.save()
            login(request, user)
            return redirect('tasks')
    else:
        form = RegisterForm()
    return render(request, 'tasks/register.html', {'form': form})

class FriendForm(forms.Form):
    username = forms.CharField(label='Имя пользователя', max_length=150, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))
    user_id = forms.IntegerField(label='ID пользователя', required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))

@login_required
def friends_list(request):
    friends = request.user.friends.all()
    form = FriendForm()
    return render(request, 'tasks/friends.html', {'friends': friends, 'form': form})

@login_required
def add_friend(request):
    if request.method == 'POST':
        form = FriendForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            user_id = form.cleaned_data.get('user_id')
            friend = None
            if user_id:
                try:
                    friend = User.objects.get(id=user_id)
                except User.DoesNotExist:
                    messages.error(request, f'Пользователь с ID {user_id} не найден.')
            elif username:
                try:
                    friend = User.objects.get(username=username)
                except User.DoesNotExist:
                    messages.error(request, f'Пользователь {username} не найден.')
            if friend:
                if friend != request.user:
                    request.user.friends.add(friend)
                    request.user.save()
                    messages.success(request, f'Пользователь {friend.username} (ID: {friend.id}) добавлен в друзья.')
                else:
                    messages.error(request, 'Нельзя добавить себя в друзья.')
        else:
            messages.error(request, 'Некорректный ввод.')
    return redirect('friends')

@login_required
def remove_friend(request, user_id):
    try:
        friend = User.objects.get(id=user_id)
        request.user.friends.remove(friend)
        request.user.save()
        messages.success(request, f'Пользователь {friend.username} удалён из друзей.')
    except User.DoesNotExist:
        messages.error(request, 'Пользователь не найден.')
    return redirect('friends')

class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'avatar', 'position']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'avatar': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'position': forms.TextInput(attrs={'class': 'form-control'}),
        }

@login_required
def profile_view(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Профиль обновлён!')
            return redirect('profile')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'tasks/profile.html', {'form': form, 'user_obj': request.user})

@login_required
def stats_view(request):
    tasks = Task.objects.filter(user=request.user)
    total_tasks = tasks.count()
    completed_tasks = tasks.filter(is_completed=True, is_closed=False).count()
    closed_tasks = tasks.filter(is_closed=True).count()
    active_tasks = tasks.filter(is_completed=False, is_closed=False).count()
    total_points = tasks.filter(is_completed=True).aggregate(points_sum=Sum('points'))['points_sum'] or 0
    # Для графика по датам завершения
    completed_by_date = (
        tasks.filter(is_completed=True)
        .values('due_date__date')
        .annotate(count=Count('id'))
        .order_by('due_date__date')
    )
    # Для графика по типу напоминания
    by_reminder = (
        tasks.values('reminder_type')
        .annotate(count=Count('id'))
        .order_by('reminder_type')
    )
    context = {
        'total_tasks': total_tasks,
        'completed_tasks': completed_tasks,
        'closed_tasks': closed_tasks,
        'active_tasks': active_tasks,
        'total_points': total_points,
        'completed_by_date': list(completed_by_date),
        'by_reminder': list(by_reminder),
    }
    return render(request, 'tasks/stats.html', context)

def settings_view(request):
    return render(request, 'tasks/settings.html')
